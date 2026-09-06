import streamlit as st
from utils.ui import style,selected_data
from services.handoff_service import generate_handoff
style(); p,e,a=selected_data(); st.title("CheckOUT handoff")
if not e or not a: st.info("Run a CheckIN first to generate a handoff."); st.stop()
h=generate_handoff(p,type("Event",(),e)(),type("Intel",(),a)())
st.markdown(h.markdown)
st.download_button("Download CheckOUT Markdown",h.markdown,file_name=f"checkout-{p.project_name.lower().replace(' ','-')}.md",mime="text/markdown")
