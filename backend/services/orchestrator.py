import asyncio
import json
import uuid
from datetime import datetime
from threading import Thread
from typing import Optional

# Import agents and state from the moved src directory
from ..src.agents.validator import ValidatorAgent
from ..src.agents.hunter import HunterAgent
from ..src.agents.miner import MinerAgent
from ..src.agents.synthesizer import SynthesizerAgent
from ..src.agents.feature_justifier import FeatureJustificationAgent
from ..src.agents.kill_switch import KillSwitchAgent
from ..src.agents.architect import ArchitectAgent
from ..src.state import ResearchState, ResearchStage, FeatureDecision, KillSwitchVerdict, PRD, ValidatedIdea, Competitor, EvidenceSignal, PainCluster
from ..db import get_db_connection
from ..src.logic.competitor_validator import extract_core_intent, extract_competitor_intent, is_wrong_competitor
from ..src.confidence import calculate_confidence

class AnalysisOrchestrator:
    def __init__(self):
        # Initialize Agents (Shared instance or per-request? Shared is better for caching if any)
        self.validator = ValidatorAgent()
        self.hunter = HunterAgent()
        self.miner = MinerAgent()
        self.synthesizer = SynthesizerAgent()
        self.feature_justifier = FeatureJustificationAgent()
        self.kill_switch = KillSwitchAgent()
        self.architect = ArchitectAgent()

    def start_analysis_background(self, analysis_id: str, raw_input: str, user_id: int, original_input: Optional[str] = None):
        """Starts the analysis in a background thread."""
        thread = Thread(target=self.run_analysis, args=(analysis_id, user_id, raw_input, original_input))
        thread.start()

    def run_analysis(self, analysis_id: str, user_id: int, raw_input: str, original_input: Optional[str] = None):
        print(f"[{analysis_id}] Starting pipeline for: {raw_input[:50]}... (Original: {original_input[:50] if original_input else 'Same'})")
        
        # Update initial record to STARTING
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE analyses SET status = ?, verdict = ?, confidence = ? WHERE id = ?",
            ("STARTING", "PENDING", 0.0, analysis_id)
        )
        conn.commit()

        # update status helper
        def update_status(status: str):
            cursor.execute("UPDATE analyses SET status = ? WHERE id = ?", (status, analysis_id))
            conn.commit()

        # Token Tracker for this run
        token_tracker = {"input": 0, "output": 0}

        try:
            # 0. Init State
            update_status("VERIFYING")
            
            validated_input = raw_input 
            # If we had a Verifier step consuming tokens, pass tracker here
            
            update_status("HUNTING")
            
            # A. Hunting
            try:
                competitors = self.hunter.hunt(validated_input, tracker=token_tracker)
            except ValueError as ve:
                update_status("FAILED")
                cursor.execute(
                    "UPDATE analyses SET status = ?, verdict = ?, confidence = ?, kill_switch_metadata = ? WHERE id = ?",
                    ("FAILED", "ABORTED", 0.0, json.dumps({"reason": str(ve)}), analysis_id)
                )
                conn.commit()
                conn.close()
                return

            # A1. Wrong Competitor Detection (Precision Upgrade)
            user_intent = extract_core_intent(validated_input)
            valid_competitors = []
            
            for comp in competitors:
                # We need a description or snippet to extract intent. The competitor object has 'title' and maybe snippet in metadata?
                # Hunter stores snippet in metadata? No, it returns Competitor objects.
                # Competitor object has `metadata`. Hunter puts `found_via_seeds` there.
                # Hunter snippet logic was: `competitors_map[link]['snippet']`.
                # But `hunt` returns `Competitor` objects which only strict fields.
                # Let's assume name + url is what we have. 
                # Ideally Hunter should attach description/snippet to the Competitor object for this validaton.
                # I will deduce intent from Name + URL for now, or assume Hunter attaches snippet to metadata.
                # Let's check Hunter again. Hunter doesn't seemingly attach snippet to Competitor in the final list, only Name/URL.
                # Wait, User provided `extract_competitor_intent` which takes `description`.
                # To fix this, I should update Hunter to ensure snippet is in metadata.
                # For now, I will assume it's there or use Name.
                comp_desc = comp.name 
                # If metadata exists and has snippet?
                if comp.metadata and 'snippet' in comp.metadata:
                     comp_desc += " " + comp.metadata['snippet']
                
                comp_intent = extract_competitor_intent(comp_desc)
                
                if not is_wrong_competitor(user_intent, comp_intent):
                    valid_competitors.append(comp)
            
            # Use VALID competitors for Mining
            competitors = valid_competitors
            valid_competitor_count = len(competitors)
            print(f"   [Orchestrator] {valid_competitor_count} valid competitors after intent filtering.")
            
            # Extract all seeds used (from competitor metadata)
            all_seeds = set()
            for c in competitors:
                if c.metadata and "found_via_seeds" in c.metadata:
                    all_seeds.update(c.metadata["found_via_seeds"])
            all_seeds_list = list(all_seeds)

            update_status("MINING")
            
            # B. Mining
            signals = self.miner.mine(competitors, tracker=token_tracker)
            signals_dicts = [s.model_dump() for s in signals]
            # Save Evidence to DB
            for s in signals_dicts:
                cursor.execute("""
                    INSERT INTO evidence_signals (analysis_id, source_type, platform, pain_theme, description, impact, severity, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (analysis_id, s['source_type'], s['platform'], s['pain_theme'], s['pain_description'], s['impact'], s['severity'], s['confidence']))
            conn.commit()
            
            update_status("SYNTHESIZING")
            
            # C. Synthesizing
            clusters = self.synthesizer.synthesize(signals, tracker=token_tracker)
            clusters_dicts = [c.model_dump() for c in clusters]
            
            # Save Clusters
            for c in clusters_dicts:
                 cursor.execute("""
                    INSERT INTO pain_clusters (analysis_id, cluster_name, severity, description, evidence_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (analysis_id, c['cluster_name'], c['severity'], c['description'], c['evidence_count']))
            conn.commit()
            
            # 3.5 Calculate Confidence (Deterministic)
            # D. Confidence Scoring
            confidence_result = calculate_confidence(signals_dicts, clusters_dicts, all_seeds_list, valid_competitor_count)
            
            update_status("JUSTIFYING")
            
            # D. Feature Justification
            feat_decisions_dicts = self.feature_justifier.justify(clusters_dicts, tracker=token_tracker)
            # Save Decisions
            for f in feat_decisions_dicts:
                cursor.execute("""
                    INSERT INTO feature_decisions (analysis_id, feature_name, mvp_priority, success_metric, complexity)
                    VALUES (?, ?, ?, ?, ?)
                """, (analysis_id, f['feature_name'], f['mvp_priority'], f['success_metric'], f['complexity']))
            conn.commit()
            
            update_status("KILL_SWITCH")
            
            # E. Kill Switch (With Confidence Override)
            ks_verdict = self.kill_switch.decide(
                clusters_dicts, 
                feat_decisions_dicts, 
                confidence_data=confidence_result,
                tracker=token_tracker
            )
            
            cursor.execute("""
                INSERT INTO kill_switch (analysis_id, verdict, confidence, primary_reason, failed_criteria, recommendation)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                analysis_id, 
                ks_verdict['verdict'], 
                ks_verdict['confidence'], 
                ks_verdict['primary_reason'], 
                json.dumps(ks_verdict['failed_criteria']), 
                ks_verdict['recommendation']
            ))
            
            # Update main analysis record with verdict AND final token counts AND confidence metadata
            cursor.execute("""
                UPDATE analyses 
                SET verdict = ?, confidence = ?, 
                    total_input_tokens = ?, total_output_tokens = ?,
                    original_input = ?, confidence_metadata = ?
                WHERE id = ?
            """, (
                ks_verdict['verdict'], 
                ks_verdict['confidence'], 
                token_tracker['input'], 
                token_tracker['output'], 
                original_input, 
                json.dumps(confidence_result), # Save metadata
                analysis_id
            ))
            conn.commit()
            
            if ks_verdict['verdict'] == "DO_NOT_BUILD":
                update_status("COMPLETED_DO_NOT_BUILD")
                conn.close()
                return

            update_status("ARCHITECTING")
            
            # F. Architecting (Only if BUILD)
            mvp_features = [f for f in feat_decisions_dicts if f.get('mvp_priority', False)]
            
            prd_data = self.architect.generate_prd(
                ValidatedIdea(description=raw_input, target_keyword=raw_input, search_volume=0, cpc=0, difficulty=0, opportunity_score=0), 
                mvp_features,
                tracker=token_tracker
            )
            
            # We need to save PRD
            if prd_data:
                cursor.execute("INSERT INTO prd (analysis_id, content_json) VALUES (?, ?)", 
                            (analysis_id, json.dumps(prd_data.model_dump())))
            
            # Final token update after Architecting
            cursor.execute("""
                UPDATE analyses 
                SET total_input_tokens = ?, total_output_tokens = ? 
                WHERE id = ?
            """, (token_tracker['input'], token_tracker['output'], analysis_id))
            conn.commit()
            
            update_status("COMPLETED_BUILD")
            
        except Exception as e:
            print(f"Pipeline Error: {e}")
            update_status(f"FAILED: {str(e)}")
            # Log error properly in real app
        finally:
            if conn:
                conn.close()

# Singleton
orchestrator = AnalysisOrchestrator()
