import time
import os
from .state import ResearchState, ResearchStage, Competitor
from .agents.hunter import HunterAgent
from .agents.miner import MinerAgent
from .agents.validator import ValidatorAgent
from .report_generator import ReportGenerator
from dotenv import load_dotenv

load_dotenv()

class SupervisorAgent:
    def __init__(self, niche: str, country_code: str = "in"):
        # Initialize the State
        self.state = ResearchState(
            project_id=f"proj_{int(time.time())}",
            niche=niche,
            country_code=country_code
        )
        
        # Initialize Hunter with your Key
        # Ensure you have your key here or in environment variables
        api_key = os.getenv("SERPAPI_KEY")
        self.hunter = HunterAgent(api_key=api_key, country_code=country_code)
        self.miner = MinerAgent(country_code=country_code)
        self.validator = ValidatorAgent(country_code=country_code)
        self.reporter = ReportGenerator()
        
        print(f"--- Supervisor Initialized for Niche: {niche} in ({country_code.upper()}) ---")

    def run(self):
        """The Main Event Loop"""
        while self.state.current_stage != ResearchStage.COMPLETED:
            
            # 1. INIT -> HUNTING
            if self.state.current_stage == ResearchStage.INIT:
                self.state.add_log("Starting Research. Transitioning to HUNTING.")
                self.state.current_stage = ResearchStage.HUNTING
            
            # 2. HUNTING (The Real Call)
            elif self.state.current_stage == ResearchStage.HUNTING:
                print(">> Supervisor: Dispatching Hunter Agent...")
                
                try:
                    # Call the real Hunter Agent
                    results = self.hunter.hunt(self.state.niche)
                    self.state.competitors = results
                    self.state.add_log(f"Hunter found {len(results)} competitors.")
                except Exception as e:
                    print(f"Error during Hunting: {e}")
                    # If hunting fails, we can't proceed. You might want to handle this differently.
                    return self.state

                self.state.current_stage = ResearchStage.HUNTING_REVIEW

            # 3. CHECKPOINT (Stop for Human)
            elif self.state.current_stage == ResearchStage.HUNTING_REVIEW:
                print("\n[!] CHECKPOINT REACHED: Review Competitors")
                self._print_competitors()
                # Break the loop to return control to the main interface (main.py)
                return self.state 

            # 4. MINING (Call Agent B)
            elif self.state.current_stage == ResearchStage.MINING:
                print(">> Supervisor: Competitors approved. Calling 'The Miner'...")
                
                try:
                    # Pass the APPROVED competitors to the miner
                    pains = self.miner.mine(self.state.competitors)
                    self.state.pain_points = pains
                    self.state.add_log(f"Miner found {len(pains)} pain points.")
                    
                    # Print results for you to see
                    print(f"\n--- [MINING COMPLETE] Found {len(pains)} signals ---")
                    for p in pains[:3]: # Show top 3
                        print(f"   * {p.pain_category}: \"{p.quote}\"")
                        
                except Exception as e:
                    print(f"Error during Mining: {e}")
                self.state.current_stage = ResearchStage.VALIDATING

            # 5. VALIDATING (Call Agent C)
            elif self.state.current_stage == ResearchStage.VALIDATING:
                print(">> Supervisor: Pains found. Calling 'The Validator'...")
                
                try:
                    ideas = self.validator.validate(self.state.pain_points)
                    self.state.final_ideas = ideas
                    
                    # --- NEW: GENERATE REPORT ---
                    print("\n>> Supervisor: Generating Final Report...")
                    filepath = self.reporter.save_report(self.state)
                    print(f"✅ REPORT SAVED: {filepath}")
                    # ----------------------------
                        
                except Exception as e:
                    print(f"Error during Validation/Reporting: {e}")

                self.state.current_stage = ResearchStage.COMPLETED
                
        print("--- Workflow Completed ---")
        return self.state

    def _print_competitors(self):
        print(f"found {len(self.state.competitors)} competitors:")
        for i, comp in enumerate(self.state.competitors):
            print(f"  {i+1}. {comp.name} ({comp.url})")
        print("\nType 'ok' to proceed or 'reject [number]' (logic to be added) to filter.")