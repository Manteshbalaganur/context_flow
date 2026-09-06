import streamlit as st
from utils.ui import style,selected_data
from services import databricks_service
style(); p,_,_=selected_data(); st.title("Development timeline")
rows=sorted(databricks_service.project_rows("events",p.project_id),key=lambda x:x["timestamp"],reverse=True)
for event in rows:
    with st.expander(f"{event['timestamp'][:19]} · {event.get('intent','Checkpoint')}",expanded=False):
        st.write("**Intent:**",event.get("intent") or "Not recorded")
        st.write("**Actions:**",", ".join(event.get("actions_attempted",[])) or "None")
        st.write("**Failures:**",", ".join(event.get("failures",[])) or "None")
        st.write("**Unresolved:**",", ".join(event.get("unresolved_work",[])) or "None")
        st.json(event.get("git_evidence",{}))
