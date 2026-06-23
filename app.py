import streamlit as st
from agents.booking_agent import booking_agent

st.set_page_config(page_title="EV Booking Workflow", page_icon="⚡")
st.title("⚡ EV Charging Booking Workflow")

user = st.text_input("Your Name")

station = st.selectbox(
    "Station",
    ["Station A", "Station B", "Station C"]
)

slot = st.selectbox(
    "Preferred Slot",
    ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
)

auto_rebook = st.checkbox("Auto-rebook at another station if preferred station is full", value=True)

if st.button("Book Slot", type="primary"):
    if not user.strip():
        st.warning("Please enter your name.")
    else:
        result = booking_agent(user, station, slot, auto_rebook=auto_rebook)
        status = result.get("status", "")

        if status == "CONFIRMED":
            st.success(f"✅ **Booked!** {station} at {result['slot']}")
        elif status == "CONFIRMED_ALTERNATIVE":
            st.info(f"🔄 **Alternative booked!** Requested `{result['requested_slot']}` was taken → booked `{result['slot']}` instead.")
        elif status == "AUTO_REBOOKED":
            st.info(f"🔄 **Auto-Rebooked at another station!** {station} at `{result['requested_slot']}` was full → booked **{result['station']}** at **{result['slot']}** instead.")
        elif status == "ESCALATED":
            st.error(f"🚨 **No slots available at {station}.**")
            suggestions = result.get("suggestions", [])
            if suggestions:
                st.warning("📍 **Available slots at other stations:**")
                grouped = {}
                for s in suggestions:
                    grouped.setdefault(s["station"], []).append(s["slot"])
                for stn, slots in grouped.items():
                    st.markdown(f"**{stn}** — " + " · ".join(f"`{sl}`" for sl in slots))
            else:
                st.warning("No slots available at any station.")
        else:
            st.warning(f"⚠️ **{status}**")

        st.json(result)