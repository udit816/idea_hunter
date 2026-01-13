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

# PHASE 1: INPUT & VERIFICATION
if st.session_state.state is None:
    st.info("💡 **Tip:** Use the formula '[Specific Process] software for [Specific Industry]'")
    raw_niche = st.text_input("Enter your Niche Idea:", placeholder="e.g. HACCP compliance software for commercial kitchens")
    
    if st.button("🚀 Analyze Potential"):
        if not raw_niche:
            st.warning("Please enter a niche.")
        else:
            with st.spinner("🤖 Verifying Intent..."):
                feedback = st.session_state.verifier.verify_niche(raw_niche)
                
            if feedback['status'] == 'valid':
                st.success("✅ Prompt Verified! Starting Research...")
                # Initialize State
                st.session_state.state = ResearchState(
                    project_id=f"proj_{int(time.time())}",
                    niche=raw_niche,
                    country_code=country_code,
                    current_stage=ResearchStage.HUNTING
                )
                # Initialize Agents with correct Country
                st.session_state.hunter = HunterAgent(country_code=country_code)
                st.session_state.miner = MinerAgent(country_code=country_code)
                st.session_state.validator = ValidatorAgent(country_code=country_code)
                st.rerun()
                
            else:
                st.error(f"⚠️ Too Vague: {feedback['critique']}")
                st.write("**Try these AI Suggestions:**")
                for s in feedback['suggestions']:
                    st.code(s)

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
    status_text.text("Miner Agent is extracting pains...")
    pains = st.session_state.miner.mine(st.session_state.state.competitors)
    st.session_state.state.pain_points = pains
    progress_bar.progress(33)
    
    # 2. VALIDATOR
    status_text.text("Validator Agent is scoring demand...")
    ideas = st.session_state.validator.validate(pains)
    st.session_state.state.final_ideas = ideas
    progress_bar.progress(66)
    
    # 3. ARCHITECT (New Step)
    if ideas:
        status_text.text("Architect Agent is drafting the Blueprint...")
        # We pick the top idea to architect
        winning_idea = ideas[0]
        spec = st.session_state.architect.create_spec(winning_idea, pains)
        st.session_state.state.product_spec = spec
    
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
    
    # Top Section: The Winning Idea
    if st.session_state.state.final_ideas:
        winner = st.session_state.state.final_ideas[0]
        st.success(f"**Top Opportunity:** {winner.description}")
        st.metric(label="Opportunity Score", value=f"{winner.opportunity_score}/10", delta="High Demand")
    
    # Tabs for Details
    tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Blueprint", "💡 Opportunities", "🩸 Pain Points", "🏢 Competitors"])
    
    with tab1: # New Tab
        if st.session_state.state.product_spec:
            spec = st.session_state.state.product_spec
            st.subheader(f"{spec.mvp_name}")
            st.caption(spec.tagline)
            st.info(f"**Hero Copy:** {spec.marketing_hook}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Core Features:**")
                for f in spec.core_features:
                    st.checkbox(f, value=True, key=f)
            with col2:
                st.write("**Tech Stack:**")
                st.code("\n".join(spec.tech_stack_recommendation), language="bash")
                
    with tab2:
        for idea in st.session_state.state.final_ideas:
            with st.expander(f"Target: {idea.target_keyword} (Score: {idea.opportunity_score})"):
                st.write(f"**Concept:** {idea.description}")
                st.write(f"**Search Vol:** {idea.search_volume}")

    with tab3:
        for pain in st.session_state.state.pain_points:
            st.write(f"- **{pain.pain_category}:** \"{pain.quote}\" (Freq: {pain.frequency})")

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