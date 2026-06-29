import subprocess
import json
import streamlit as st
from agents.booking_agent import BookingAgent
from openclaw_client import run_openclaw

# Set page configuration with premium styling elements
st.set_page_config(
    page_title="Autonomous EV Booking AGENT",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design System CSS
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main-header {
        font-family: 'Outfit', 'Inter', sans-serif;
        color: #00e5ff;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #8a99ad;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .state-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
        background-color: #1e293b;
        color: #38bdf8;
        border: 1px solid #38bdf8;
        margin-right: 0.5rem;
    }
    .metric-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar configurations
with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/lightning-bolt.png", width=70)

    st.markdown("## 🤖 Autonomous Agent")

    st.success("Mission: Manage EV charging bookings autonomously.")

    st.markdown("### Agent Capabilities")

    st.markdown("""
- 🧠 Intent Understanding
- 📍 Station Validation
- ⚡ Slot Availability Check
- 🔍 Duplicate Booking Detection
- 🔄 Alternative Slot Search
- ✅ Booking Creation
- 💾 Workflow Memory
- 📋 Audit Logging
- 🚨 Escalation Handling
""")

    st.markdown("---")

    auto_rebook = st.checkbox(
        "Enable Auto-Rebooking",
        value=True,
        help="Automatically book the nearest available slot when the requested slot is unavailable."
    )

    st.markdown("---")

    st.markdown("### Runtime Status")

    st.metric("Workflow", "EV Booking")
    st.metric("Reasoning", "Enabled")
    st.metric("Memory", "Persistent")
    st.metric("Audit", "Enabled")
# Main Title
st.markdown("<div class='main-header'>⚡ Autonomous EV Booking Agent</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>AI-Powered EV Charging Workflow with OpenClaw Plugin Integration</div>", unsafe_allow_html=True)
# User NL Request Input
user_request = st.text_area(
    "Booking Command Input",
    placeholder="Describe your booking request in natural language (e.g., 'Book a slot at Station A at 09:00 for Arjun')",
    height=100,
    help="Type in natural language. The agent will autonomously extract entities, validate, check slot, handle duplicates, book, or escalate."
)

if st.button("Initialize Autonomous Agent", type="primary"):
    if not user_request.strip():
        st.warning("Please input a natural language request command to proceed.")
    else:
        with st.spinner("Agent initializing state machine and memory manager..."):
            try:
                # Call OpenClaw runtime tool directly (minimal integration layer).
                # This avoids direct Groq prompting in Streamlit and forces immediate tool use.
                openclaw_request = {
                    "tool": "book_ev_slot",
                    "parameters": {
                        "request": user_request
                    }
                }

                ow = run_openclaw(
                    json.dumps(openclaw_request, ensure_ascii=False)
                )

                if ow.get("returncode") != 0:
                    raise RuntimeError(
                        f"OpenClaw tool invocation failed: rc={ow.get('returncode')} stderr={ow.get('stderr')}"
                    )

                # Expect plugin to return JSON on stdout.
                # If OpenClaw wraps output, try to locate the last JSON object.
                stdout = (ow.get("stdout") or "").strip()
                try:
                    plugin_result = json.loads(stdout)
                except Exception:
                    # Fallback: attempt to parse the last JSON block
                    start = stdout.rfind("{")
                    plugin_result = json.loads(stdout[start:])

                # Preserve existing Streamlit expectations: `record` dict with `final_outcome`.
                record = plugin_result if isinstance(plugin_result, dict) else {"final_outcome": plugin_result}
                
                
                # Display Results
                outcome = record.get("final_outcome", {})
                status = outcome.get("status")
                

                st.markdown("### Execution Outcome")
                # ----------------------------
                # Agent Reasoning
                # ----------------------------

                st.markdown("### 🧠 Agent Reasoning")

                for i, decision in enumerate(record.get("decisions", []), start=1):
                    with st.container():
                        st.success(f"Step {i}: {decision['decision']}")

                        if decision.get("context"):
                            st.caption(f"Reason: {decision['context']}")

                # ----------------------------
                # Current Agent State
                # ----------------------------

                states = record.get("state_transitions", [])

                if states:
                    st.info(f"📍 Current Agent State: **{states[-1]['to_state']}**")



                # Display outcome card
                if status == "CONFIRMED":
                    st.success(f"🎉 **Booking Confirmed!** Slot `{outcome.get('slot')}` has been secured at **{outcome.get('station')}** for **{outcome.get('user')}**.")
                elif status == "CONFIRMED_ALTERNATIVE":
                    st.info(f"🔄 **Alternative Slot Booked!** Requested slot `{outcome.get('requested_slot')}` was unavailable. Slot `{outcome.get('slot')}` has been booked at **{outcome.get('station')}** instead.")
                elif status == "AUTO_REBOOKED":
                    st.info(f"🔄 **Auto-Rebooked Across Stations!** **{outcome.get('requested_station')}** was fully booked at `{outcome.get('requested_slot')}`. Slot `{outcome.get('slot')}` was secured at **{outcome.get('station')}** instead.")
                elif status == "ESCALATED":
                    st.error(f"🚨 **Workflow Escalated!** {outcome.get('escalation', {}).get('reason')}")
                    
                    # Suggestions display
                    suggestions = outcome.get("suggestions", [])
                    if suggestions:
                        st.markdown("**Alternative suggestions available at other stations:**")
                        for sug in suggestions:
                            st.markdown(f"- **{sug['station']}** at `{sug['slot']}`")
                    else:
                        st.markdown("_No alternative slots are currently available across any operating stations._")
                    
                    st.warning(f"💡 **Recommended Action**: {outcome.get('escalation', {}).get('recommended_action')}")
                elif status == "FAILED":
                    st.warning(f"⚠️ **Validation Failed:** {outcome.get('reason')}")
                else:
                    st.error(f"❌ **Error:** {outcome.get('error', {}).get('message', 'Unexpected error occurred during booking.')}")

                # Tabs for Audit Log, Transition Log, and Technical State details
                tab1, tab2, tab3 = st.tabs(["📋 Execution Log & Audit", "🔗 State Transitions Graph", "🛠 Raw JSON Payload"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Extracted Entity Intent")
                        st.json(record.get("extracted_intent", {}))
                        
                        st.markdown("#### Autonomous Decisions")
                        for dec in record.get("decisions", []):
                            st.markdown(f"**[{dec['state']}]** {dec['decision']}")
                            if dec.get("context"):
                                st.caption(f"Context: {dec['context']}")
                                
                    with col2:
                        st.markdown("#### Tool Invocations")
                        for i, tool in enumerate(record.get("tool_invocations", [])):
                            with st.expander(f"{i+1}. Tool: {tool['tool']} ({tool['status']})"):
                                st.markdown(f"**Time**: {tool['timestamp']}")
                                st.markdown("**Inputs**:")
                                st.json(tool["input"])
                                st.markdown("**Outputs**:")
                                st.json(tool["output"])

                with tab2:
                    st.markdown("#### Workflow Execution Steps")
                    for trans in record.get("state_transitions", []):
                        from_s = trans['from_state'] or "START_TRIGGER"
                        to_s = trans['to_state']
                        st.markdown(f"🔄 **{from_s}** ──► **{to_s}**  *({trans['reason']})*")
                        
                with tab3:
                    st.markdown("#### Complete Audit File Record")
                    st.json(record)

            except Exception as e:
                st.exception(e)
