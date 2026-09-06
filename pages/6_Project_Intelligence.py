import streamlit as st
from utils.ui import style,selected_data,metric
style(); _,_,a=selected_data(); st.title("Project intelligence")
if not a: st.info("Run a CheckIN to generate intelligence."); st.stop()
for col,(l,v,c) in zip(st.columns(4),[("Completion",f"{a['completion_score']}%","evidence-based estimate"),("Risk",a['risk_level'],f"{a['risk_score']}/100"),("Context debt",a['context_debt_level'],f"{a['context_debt_score']}/100"),("Blast radius",a['blast_radius'],"estimated impact")]):
    with col: metric(l,v,c)
st.markdown("### Intent vs implementation")
st.write(f"**{a['intent_drift_status']}** — {a['intent_drift_reason']}")
st.markdown("### Evidence and next action")
st.write("**Handoff readiness:**",a["handoff_readiness"],"—",a["handoff_readiness_reason"])
st.write("**Recommended next step:**",a["recommended_next_step"])
if a["smart_checkpoint_gaps"]: st.warning("\n".join(a["smart_checkpoint_gaps"]))
with st.expander("Evidence used"): st.json(a["evidence"])
