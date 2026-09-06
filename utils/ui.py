import streamlit as st
from services import project_service,databricks_service

def style():
    st.set_page_config(page_title="CheckIN",page_icon="◈",layout="wide")
    st.markdown("""<style>.stApp{background:#07111f;color:#eaf2ff}.block-container{padding-top:2rem}.metric-card{background:#0d1d31;border:1px solid #1b3855;border-radius:14px;padding:14px 18px;margin-bottom:10px}.eyebrow{color:#55d6ff;text-transform:uppercase;letter-spacing:.12em;font-size:.78rem}.status{color:#9db3c8}.stButton>button{border-radius:9px;border:0;background:#16a9d5;color:#00111b;font-weight:700}.stButton>button:hover{background:#5edbff}</style>""",unsafe_allow_html=True)

def seed_demo():
    if project_service.list_projects(): return
    samples=[("Atlas API","Near-release authentication platform","Implement JWT authentication and audit logging",[],[],["Run final security test"],85,18,24,"Ready"),("Beacon Console","Operations dashboard undergoing a broad UI refactor","Refine incident-management workflows",["Assume new API contracts are stable"],["Tried component migration"],["Resolve failed alert filters","Document API changes"],61,56,71,"Needs context"),("Legacy Bridge","Stale integration service with incomplete migration context","Migrate payment adapter",[],["Initial adapter migration failed"],["Reconcile webhook payload behavior"],43,78,82,"Needs resolution")]
    from utils.helpers import now_iso,new_id
    for name,desc,intent,ass,fail,unresolved,completion,risk,debt,ready in samples:
        p=project_service.create_project(name,desc)
        event={"event_id":new_id("evt"),"project_id":p.project_id,"checkpoint_id":new_id("cp"),"timestamp":now_iso(),"git_evidence":{"available":True,"branch":"main","latest_commit":"Demo checkpoint","commits":[],"warnings":[],"changed_files":[{"file_path":"src/auth/service.py"},{"file_path":"src/ui/console.py"}]},"intent":intent,"assumptions":ass,"actions_attempted":["Reviewed current implementation"],"failures":fail,"unresolved_work":unresolved,"impacted_components":["src/auth/service.py","src/ui/console.py"],"dependencies":["src/config.py"],"metadata":{"context_source":"demo/mock","impact_confidence":"estimated"}}
        analysis={"analysis_id":new_id("analysis"),"project_id":p.project_id,"checkpoint_id":event["checkpoint_id"],"timestamp":now_iso(),"completion_score":completion,"risk_score":risk,"risk_level":"High" if risk>65 else "Medium" if risk>35 else "Low","unfinished_requirements":unresolved,"unresolved_risks":fail+unresolved,"release_readiness":"Ready" if completion>80 and risk<30 else "Not ready","recommended_next_step":"Resolve the highest-priority unresolved item and document the outcome.","intent_drift_status":"Minor Drift" if risk>40 else "Aligned","intent_drift_reason":"Demo evidence compares intended scope with changed components.","context_debt_score":debt,"context_debt_level":"High" if debt>65 else "Medium" if debt>35 else "Low","context_debt_reason":"Based on completeness of context and unresolved work.","blast_radius":"Medium","blast_radius_reason":"Estimated from changed components and dependency evidence.","smart_checkpoint_gaps":["Add verification evidence before next handoff."] if risk>40 else [],"handoff_readiness":ready,"handoff_readiness_reason":"Based on risk, context debt, and unresolved work.","evidence":{"changed_files":["src/auth/service.py","src/ui/console.py"],"failures":fail,"unresolved_work":unresolved,"dependencies":["src/config.py"]}}
        databricks_service.store_event(event,{"checkpoint_id":event["checkpoint_id"],"project_id":p.project_id,"timestamp":event["timestamp"],"intent":intent,"assumptions":ass,"actions_attempted":["Reviewed current implementation"],"failures":fail,"unresolved_work":unresolved,"verification_status":"estimated","source":"demo/mock"},[],[]); databricks_service.store_analysis(analysis)

def sidebar():
    seed_demo(); projects=project_service.list_projects()
    with st.sidebar:
        st.markdown("## ◈ CheckIN\n<span class='status'>Know where your code is, and why it’s there.</span>",unsafe_allow_html=True)
        labels={p.project_id:p.project_name for p in projects}; current=st.session_state.get("selected_project_id")
        index=list(labels).index(current) if current in labels else 0
        selected=st.selectbox("Active project",options=list(labels),index=index,format_func=lambda x:labels[x]) if labels else None
        if selected: st.session_state["selected_project_id"]=selected
        with st.expander("Register project"):
            name=st.text_input("Project name"); desc=st.text_area("Description"); path=st.text_input("Local repository path"); url=st.text_input("Repository URL")
            if st.button("Register",use_container_width=True) and name:
                p=project_service.create_project(name,desc,path,url); st.session_state["selected_project_id"]=p.project_id; st.rerun()
        if selected and st.button("CHECK IN PROJECT",use_container_width=True):
            try:
                from services.sync_service import check_in_project
                check_in_project(selected); st.success("CheckIN recorded."); st.rerun()
            except Exception as exc: st.error(str(exc))
        st.caption("● Local JSON store active · Entire and Databricks optional")
    return project_service.get_project(st.session_state.get("selected_project_id")) if st.session_state.get("selected_project_id") else None

def selected_data():
    p=sidebar()
    if not p: st.info("Register or select a project to begin."); st.stop()
    return p,databricks_service.latest_event(p.project_id),databricks_service.latest_analysis(p.project_id)

def metric(label,value,caption=""):
    st.markdown(f"<div class='metric-card'><div class='eyebrow'>{label}</div><h2 style='margin:.25rem 0'>{value}</h2><div class='status'>{caption}</div></div>",unsafe_allow_html=True)
