import streamlit as st
from utils.ui import style,selected_data
from services.sync_service import check_in_project
style(); p,e,_=selected_data(); st.title("Development context")
st.caption("Context is stored with the next CheckIN. Manual context is used when Entire is unavailable.")
with st.form("context"):
    intent=st.text_area("Intent",value=e.get("intent","") if e else "")
    assumptions=st.text_area("Assumptions (one per line)",value="\n".join(e.get("assumptions",[])) if e else "")
    actions=st.text_area("Actions attempted (one per line)",value="\n".join(e.get("actions_attempted",[])) if e else "")
    failures=st.text_area("Failures (one per line)",value="\n".join(e.get("failures",[])) if e else "")
    unresolved=st.text_area("Unresolved work (one per line)",value="\n".join(e.get("unresolved_work",[])) if e else "")
    verification=st.selectbox("Verification",["not verified","partially verified","verified"])
    if st.form_submit_button("Save context and CheckIN"):
        split=lambda x:[v.strip() for v in x.splitlines() if v.strip()]
        check_in_project(p.project_id,{"intent":intent,"assumptions":split(assumptions),"actions_attempted":split(actions),"failures":split(failures),"unresolved_work":split(unresolved),"verification_status":verification}); st.success("Context captured."); st.rerun()
