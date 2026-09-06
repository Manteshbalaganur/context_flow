import streamlit as st
from utils.ui import style,selected_data,metric
style(); p,e,a=selected_data()
st.title(p.project_name); st.caption(p.description or "No project description")
if not a: st.info("No CheckIN yet. Use the sidebar button to create the first project memory snapshot."); st.stop()
for col,(l,v,c) in zip(st.columns(4),[("Completion",f"{a['completion_score']}%","current estimate"),("Risk",a['risk_level'],f"score {a['risk_score']}"),("Context debt",a['context_debt_level'],f"score {a['context_debt_score']}"),("Handoff",a['handoff_readiness'],a['release_readiness'])]):
    with col: metric(l,v,c)
st.markdown("### What changed and why")
st.write(e.get("intent") or "No intent recorded.")
c1,c2=st.columns(2)
with c1: st.markdown("**Unresolved work**"); st.write(a["unfinished_requirements"] or "None recorded")
with c2: st.markdown("**Recommended next step**"); st.write(a["recommended_next_step"])
st.caption(f"Project ID: {p.project_id} · Repository: {p.repository_path or p.repository_url or 'Not mapped'} · Last CheckIN: {p.last_checkin_at or '—'}")
