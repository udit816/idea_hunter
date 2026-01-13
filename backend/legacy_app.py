import streamlit as st
import time
import os
from dotenv import load_dotenv

# Load logic
from src.state import ResearchState, ResearchStage
from src.agents.verifier import VerifierAgent
from src.agents.hunter import HunterAgent
from src.agents.miner import MinerAgent
from src.agents.validator import ValidatorAgent
from src.report_generator import ReportGenerator
from src.agents.architect import ArchitectAgent
from src.agents.discovery import DiscoveryAgent
from src.agents.synthesizer import SynthesizerAgent
from src.agents.feature_justifier import FeatureJustificationAgent
from src.agents.kill_switch import KillSwitchAgent
from src.state import ResearchState, ResearchStage, FeatureDecision, KillSwitchVerdict

# Page Config
st.set_page_config(page_title="MicroSaaS Validator", page_icon="🕵️", layout="wide")

# --- CUSTOM CSS (Optional) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; }
    .success-box { padding: 10px; background-color: #d4edda; color: #155724; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
if "state" not in st.session_state:
    st.session_state.state = None # To store ResearchState
if "verifier" not in st.session_state:
    load_dotenv()
    st.session_state.verifier = VerifierAgent()
    st.session_state.hunter = None
    st.session_state.miner = None
    st.session_state.validator = None
    st.session_state.architect = ArchitectAgent()
    st.session_state.discovery = DiscoveryAgent()
    st.session_state.reporter = ReportGenerator()

# --- SIDEBAR (Configuration) ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = os.getenv("SERPAPI_KEY")
    status = "✅ Connected" if api_key else "❌ Missing Key"
    st.info(f"SerpApi Status: {status}")
    
    country_code = st.selectbox("Target Market", ["in", "us", "uk", "ca"], index=0, format_func=lambda x: x.upper())
    
    if st.button("Reset / New Search"):
        st.session_state.state = None
        st.rerun()

# --- MAIN UI ---
st.title("🕵️ MicroSaaS Validator Engine")
st.markdown("##### *Turn Vague Ideas into Validated Gold*")

# PHASE 1: DISCOVERY & DEFINITION
if st.session_state.state is None:
    st.info("💡 **Tip:** Enter a URL, a competitor name, or just a vague problem statement.")
    raw_niche = st.text_input("What are you exploring?", placeholder="e.g. 'linear.app' or 'project management for remote teams'")
    
    if st.button("🚀 Discover Problems"):
        if not raw_niche:
            st.warning("Please enter something to analyze.")
        else:
            with st.spinner("🕵️ Analyzing Context & Extracting Problems..."):
                discovery_data = st.session_state.discovery.discover(raw_niche)
                
            st.success(f"**Interpreted Domain:** {discovery_data.interpreted_domain}")
            
            st.subheader("⚠️ Identified Problem Statements")
            
            selected_problem = None
            for idx, p in enumerate(discovery_data.problem_statements):
                with st.container():
                    st.markdown(f"**{idx+1}. {p.problem}**")
                    st.caption(f"**Who:** {p.who} | **Why Now:** {p.why_now}")
                    if st.button(f"✅ Solve This Problem", key=f"prob_{idx}"):
                        selected_problem = p
            
            if selected_problem:
                # Initialize State with the Selected Problem Context
                st.session_state.state = ResearchState(
                    project_id=f"proj_{int(time.time())}",
                    niche=f"{discovery_data.interpreted_domain} - {selected_problem.problem}",
                    country_code=country_code,
                    current_stage=ResearchStage.HUNTING,
                    discovery_data=discovery_data
                )
                # Initialize Agents
                st.session_state.hunter = HunterAgent(country_code=country_code)
                st.session_state.miner = MinerAgent(country_code=country_code)
                st.session_state.validator = ValidatorAgent(country_code=country_code)
                st.rerun()

# PHASE 2: HUNTING (The Search)
elif st.session_state.state.current_stage == ResearchStage.HUNTING:
    st.header(f"🔍 Phase 1: Market Scan ({st.session_state.state.niche})")
    
    with st.spinner("🦅 Hunter Agent is scouring the web..."):
        competitors = st.session_state.hunter.hunt(st.session_state.state.niche)
        st.session_state.state.competitors = competitors
        st.session_state.state.current_stage = ResearchStage.HUNTING_REVIEW
        st.rerun()

# PHASE 3: HUMAN CHECKPOINT
elif st.session_state.state.current_stage == ResearchStage.HUNTING_REVIEW:
    st.header("📋 Phase 2: Competitor Review")
    st.write("The Hunter found these existing solutions. Uncheck any irrelevant ones.")
    
    # Render Checkboxes
    comps = st.session_state.state.competitors
    if not comps:
        st.warning("No competitors found. Attempting to proceed might fail.")
    
    selected_indices = []
    for i, comp in enumerate(comps):
        is_checked = st.checkbox(f"{comp.name}", value=True, key=f"comp_{i}")
        if is_checked:
            selected_indices.append(i)
            
    st.write(f"**{len(selected_indices)}** competitors selected for Deep Dive.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve & Start Mining"):
            # Filter the list based on selection
            final_list = [comps[i] for i in selected_indices]
            st.session_state.state.competitors = final_list
            st.session_state.state.current_stage = ResearchStage.MINING
            st.rerun()
    with col2:
        if st.button("🛑 Stop Research"):
            st.session_state.state = None
            st.rerun()

# PHASE 4: MINING, VALIDATING & ARCHITECTING
elif st.session_state.state.current_stage == ResearchStage.MINING:
    st.header("⛏️ Phase 3: Deep Research & Architecture")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 1. MINER
    status_text.text("Miner Agent is extracting evidence signals...")
    signals = st.session_state.miner.mine(st.session_state.state.competitors)
    st.session_state.state.evidence_signals = signals
    progress_bar.progress(33)
    from src.agents.feature_justifier import FeatureJustificationAgent

# ... (inside init)
    if "feature_justifier" not in st.session_state:
        st.session_state.feature_justifier = FeatureJustificationAgent()
    if "kill_switch" not in st.session_state:
        st.session_state.kill_switch = KillSwitchAgent()
# ...

    # 2. SYNTHESIZER
    if signals:
        status_text.text("Synthesizer Agent is grouping clusters...")
        st.session_state.state.current_stage = ResearchStage.SYNTHESIZING
        clusters = st.session_state.synthesizer.synthesize(signals)
        st.session_state.state.pain_clusters = clusters
        
        status_text.text("Synthesizer Agent is deriving product intent...")
        intent = st.session_state.synthesizer.derive_intent(clusters)
        st.session_state.state.product_intent = intent
        
    # 3. FEATURE JUSTIFIER (New Step)
    if st.session_state.state.pain_clusters:
        status_text.text("Feature Justifier is deciding scope...")
        st.session_state.state.current_stage = ResearchStage.JUSTIFYING
        
        # Convert Pydantic models to dicts for the agent
        cluster_dicts = [c.model_dump() for c in st.session_state.state.pain_clusters]
        decisions = st.session_state.feature_justifier.justify(cluster_dicts)
        
        # Convert back to Pydantic models
        st.session_state.state.feature_decisions = [
            FeatureDecision(**d) for d in decisions
        ]

    progress_bar.progress(66)
    
    # ... (Feature Justifier Block above) ...
        # Convert back to Pydantic models
        st.session_state.state.feature_decisions = [
            FeatureDecision(**d) for d in decisions
        ]
        
    # 4. KILL SWITCH (New Gatekeeper)
    if st.session_state.state.feature_decisions:
        status_text.text("Kill-Switch Agent is evaluating viability...")
        st.session_state.state.current_stage = ResearchStage.KILL_SWITCH
        
        verdict_data = st.session_state.kill_switch.decide(
            pain_clusters=[c.model_dump() for c in st.session_state.state.pain_clusters],
            feature_decisions=[f.model_dump() for f in st.session_state.state.feature_decisions]
        )
        verdict = KillSwitchVerdict(**verdict_data)
        st.session_state.state.kill_switch = verdict
        
        if verdict.verdict == "DO_NOT_BUILD":
            status_text.text("❌ Verdict: DO NOT BUILD. Stopping pipeline.")
            st.session_state.state.current_stage = ResearchStage.COMPLETED
            st.rerun()
            
    # 5. ARCHITECT (Only if verdict is BUILD)
    can_build = st.session_state.state.kill_switch and st.session_state.state.kill_switch.verdict == "BUILD"
    
    if can_build and st.session_state.state.feature_decisions:
        status_text.text("Architect Agent is drafting the PM-Grade PRD...")
# ...
        st.session_state.state.current_stage = ResearchStage.ARCHITECTING
        
        prd = st.session_state.architect.generate_prd(
            feature_decisions=[f.model_dump() for f in st.session_state.state.feature_decisions],
            pain_clusters=[c.model_dump() for c in st.session_state.state.pain_clusters]
        )
        st.session_state.state.prd = prd
    
    progress_bar.progress(100)
    
    # Save Report
    report_path = st.session_state.reporter.save_report(st.session_state.state)
    st.session_state.report_path = report_path
    
    st.session_state.state.current_stage = ResearchStage.COMPLETED
    st.rerun()

# PHASE 5: FINAL REPORT
elif st.session_state.state.current_stage == ResearchStage.COMPLETED:
    st.balloons()
    st.header("🏆 Analysis Complete!")
    
    # Top Section: The Winning Idea or Verdict
    
    # KILL SWITCH BANNER
    if st.session_state.state.kill_switch:
        ks = st.session_state.state.kill_switch
        if ks.verdict == "DO_NOT_BUILD":
            st.error(f"⛔ **KILL SWITCH TRIGGERED: {ks.verdict}**")
            st.markdown(f"**Primary Reason:** {ks.primary_reason}")
            st.write(f"**Recommendation:** {ks.recommendation}")
            with st.expander("Why did this fail?"):
                for r in ks.supporting_reasons:
                    st.write(f"- {r}")
                st.write("**Failed Criteria:**")
                for c in ks.failed_criteria:
                    st.code(c)
            st.stop() # Stop rendering the rest
            
        else:
            st.success(f"✅ **PASSED FEASIBILITY CHECK** (Confidence: {ks.confidence})")

    if st.session_state.state.product_intent:
        intent = st.session_state.state.product_intent
        st.info(f"**Strategic Opportunity:** {intent.opportunity_statement}")
    
    # Tabs for Details
    tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Blueprint", "💡 Opportunities", "🩸 Pain Points", "🏢 Competitors"])
    
    with tab1: # New Tab
        if st.session_state.state.prd:
            prd = st.session_state.state.prd
            overview = prd.get("product_overview", {})
            st.subheader(f"{overview.get('name', 'MVP')}")
            st.caption(overview.get("one_liner", ""))
            st.markdown(f"**Problem Statement:** *{overview.get('problem_statement', '')}*")
            
            # --- PRD SECTION ---
            st.divider()
            st.subheader("📜 Product Requirements Document (PRD)")
            
            p_tabs = st.tabs(["Goals & Scope", "User Flow", "Risks", "MVP Features"])
            
            with p_tabs[0]:
                c1, c2 = st.columns(2)
                with c1:
                    st.write("#### 🎯 Goals")
                    for g in prd.get("goals", []):
                        st.write(f"- {g}")
                with c2:
                    st.write("#### ⛔ Non-Goals")
                    for ng in prd.get("non_goals", []):
                        st.write(f"- {ng}")

            with p_tabs[1]:
                st.write("#### 🛤️ Core User Flow")
                for idx, step in enumerate(prd.get("user_flow", [])):
                    st.info(f"**Step {idx+1}:** {step}")

            with p_tabs[2]:
                st.write("#### 🚩 Risks & Unknowns")
                for r in prd.get("risks_and_unknowns", []):
                    st.warning(f"- **{r.get('risk', 'Risk')}**: {r.get('mitigation', '')}")

            with p_tabs[3]:
                st.write("#### ✨ MVP Feature Specification")
                for mvp_feat in prd.get("mvp_features", []):
                    with st.expander(f"{mvp_feat.get('name', 'Feature')}"):
                        st.write(f"**Description:** {mvp_feat.get('description', '')}")
                        st.write(f"**Solves:** {mvp_feat.get('user_pain_addressed', '')}")
                        st.write(f"**Success Metric:** `{mvp_feat.get('success_metric', '')}`")
                        st.write(f"**Complexity:** {mvp_feat.get('complexity', '')}")

            # --- LAUNCH SCOPE & SUCCESS ---
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                 st.write("#### 🏗️ Launch Scope")
                 st.write("**Included:**")
                 for i in prd.get("launch_scope", {}).get("included", []):
                     st.write(f"- {i}")
                 st.write("**Excluded:**")
                 for e in prd.get("launch_scope", {}).get("excluded", []):
                     st.write(f"- {e}")
            with c2:
                 st.write("#### 📈 Success Success Definition")
                 st.write("**Leading Indicators:**")
                 for l in prd.get("success_definition", {}).get("leading_indicators", []):
                     st.write(f"- {l}")
                 
    with tab2:
        for idea in st.session_state.state.final_ideas:
            with st.expander(f"Target: {idea.target_keyword} (Score: {idea.opportunity_score})"):
                st.write(f"**Concept:** {idea.description}")
                st.write(f"**Search Vol:** {idea.search_volume}")

    with tab3:
        st.subheader("🔥 Synthesized Pain Clusters")
        
        if st.session_state.state.product_intent:
            intent = st.session_state.state.product_intent
            st.info(f"**Strategic Opportunity:** {intent.opportunity_statement}")
            st.caption(f"**Market Failure:** {intent.current_market_failure}")
        
        if st.session_state.state.pain_clusters:
            for cluster in st.session_state.state.pain_clusters:
                with st.expander(f"{cluster.cluster_name} ({cluster.severity.upper()})"):
                    st.write(f"**Real Problem:** {cluster.description}")
                    st.write(f"**Why Users Angry:** {cluster.why_users_get_angry}")
                    st.write(f"**Impact:** Trial Blocker: {cluster.impact_summary.trial_blocker} | Trust Collapse: {cluster.impact_summary.trust_collapse}")
                    st.write(f"**Affected:** {', '.join(cluster.affected_personas)}")
                    st.caption("Quotes:")
                    for q in cluster.representative_quotes:
                        st.text(f"\"{q}\"")
        else:
            st.write("No clusters found.")
            
        st.divider()
        st.write("### All Evidence Signals")
        for sig in st.session_state.state.evidence_signals:
            st.write(f"- **{sig.pain_theme}:** \"{sig.pain_description}\"")
            st.caption(f"Impact: {sig.impact} | Severity: {sig.severity} | Src: {sig.source_type}")

    with tab4:
        for comp in st.session_state.state.competitors:
            st.write(f"- [{comp.name}]({comp.url})")

    # Download Button
    with open(st.session_state.report_path, "rb") as file:
        st.download_button(
            label="📄 Download Full Report (Markdown)",
            data=file,
            file_name=os.path.basename(st.session_state.report_path),
            mime="text/markdown"
        )