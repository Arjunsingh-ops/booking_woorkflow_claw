import streamlit as st
from agents.ai_booking_agent import ai_booking_agent

st.title("Booking Workflow Claw (AI)")

user_request = st.text_area(
    "Describe your booking request (e.g., 'Book Station A at 09:00 for Arjun').",
    height=120,
)

auto_rebook = st.checkbox("Auto-rebook at another station if preferred station is full", value=True)

if st.button("Run AI Booking"):
    if not user_request.strip():
        st.warning("Please enter a request.")
    else:
        result = ai_booking_agent(user_request, auto_rebook=auto_rebook)

        status = result.get("status", "")

        if status in ("BOOKED", "CONFIRMED_ALTERNATIVE"):
            st.success(f"✅ {status}")
        elif status == "AUTO_REBOOKED":
            st.info(f"🔄 **Auto-Rebooked at another station!** Requested {result.get('requested_station')} at `{result.get('requested_slot')}` was full → booked **{result.get('station')}** at **{result.get('slot')}** instead.")
        elif status == "ESCALATED":
            station_name = result.get('station', 'the requested station')
            st.error(f"🚨 **No slots available at {station_name}.**")
            suggestions = result.get("suggestions", [])
            if suggestions:
                st.warning("📍 **Available slots at other stations:**")
                grouped = {}
                for s in suggestions:
                    grouped.setdefault(s["station"], []).append(s["slot"])
                for stn, slots in grouped.items():
                    st.markdown(f"**{stn}** — " + " · ".join(f"`{sl}`" for sl in slots))
            else:
                st.warning("No slots available at any station right now.")
        elif status == "FAILED":
            st.warning(f"⚠️ {status} — {result.get('reason', '')}")
        else:
            st.info(f"ℹ️ {status}")

        st.json(result)
