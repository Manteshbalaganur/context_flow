import streamlit as st
from utils.ui import style,selected_data
from services import databricks_service
style(); p,_,_=selected_data(); st.title("Project memory")
events=sorted(databricks_service.project_rows("events",p.project_id),key=lambda x:x["timestamp"],reverse=True)
query=st.text_input("Search development memory")
for event in events:
    blob=str(event).lower()
    if query.lower() and query.lower() not in blob: continue
    st.markdown(f"### {event['timestamp'][:19]} · {event.get('intent','Untitled checkpoint')}")
    st.write("Changed:",", ".join(x.get("file_path","") for x in event.get("git_evidence",{}).get("changed_files",[])) or "No files captured")
    st.write("Unresolved:",", ".join(event.get("unresolved_work",[])) or "None")
