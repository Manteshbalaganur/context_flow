import streamlit as st
from utils.ui import style,selected_data
from services.sync_service import check_in_project
from services.entire_service import get_status, list_native_checkpoints
style(); p,e,_=selected_data(); st.title("Entire context")
status=get_status(p.repository_path)
if status["available"]:
    st.success("Entire CLI connected. Native checkpoints shown below are real Entire records.")
    checkpoints,error=list_native_checkpoints(p.repository_path)
    if error: st.warning(error)
    elif checkpoints: st.dataframe(checkpoints,use_container_width=True,hide_index=True)
    else: st.info("Entire is enabled, but this repository has no checkpoints yet.")
else:
    st.warning(status["message"])
    st.caption("CheckIN can still store manual project context locally. It is not an Entire checkpoint.")
    st.code("entire enable --agent codex\n# work with your agent, then stage and commit the change",language="bash")
st.caption("Entire creates a native checkpoint only when enabled agent-session context is linked to a Git commit; saving this form creates a CheckIN event, not a fabricated Entire checkpoint.")
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
