import streamlit as st
from utils.ui import style, sidebar, metric
from services import project_service, databricks_service

style(); selected=sidebar(); projects=project_service.list_projects()
st.markdown("# Portfolio health\n<span class='status'>Persistent development intelligence across every registered project.</span>",unsafe_allow_html=True)
rows=[]
for p in projects:
    a=databricks_service.latest_analysis(p.project_id) or {}
    rows.append((p,a))
healthy=sum(1 for _,a in rows if a.get("risk_level")=="Low")
attention=sum(1 for _,a in rows if a.get("risk_level") in ("Medium","High"))
high_debt=sum(1 for _,a in rows if a.get("context_debt_level")=="High")
release=sum(1 for _,a in rows if a.get("release_readiness")=="Ready")
cols=st.columns(4)
for col,(label,value,caption) in zip(cols,[("Projects",len(projects),"registered"),("Healthy",healthy,"low risk"),("Attention",attention,"risk detected"),("Release-ready",release,"ready now")]):
    with col: metric(label,value,caption)
st.markdown("### Projects")
for p,a in rows:
    with st.container(border=True):
        left,right=st.columns([4,1])
        with left:
            st.subheader(p.project_name); st.caption(p.description or "No description")
            st.write(f"Progress **{a.get('completion_score','—')}%** · Risk **{a.get('risk_level','Unknown')}** · Context debt **{a.get('context_debt_score','—')}** · Handoff **{a.get('handoff_readiness','Unknown')}**")
            st.caption(f"Last CheckIN: {p.last_checkin_at or 'Not yet checked in'}")
        with right:
            if st.button("Open",key=p.project_id): st.session_state["selected_project_id"]=p.project_id; st.switch_page("pages/1_Project_Overview.py")
