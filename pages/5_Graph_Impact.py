import streamlit as st
import pandas as pd
from utils.ui import style,selected_data
from services import databricks_service
style(); p,_,a=selected_data(); st.title("Graph impact")
rows=databricks_service.project_rows("graph_impact",p.project_id)
st.info("Impact is estimated from changed files and discovered imports unless verified evidence is supplied.")
if rows: st.dataframe(pd.DataFrame(rows)[["changed_component","dependencies","impacted_modules","verification_status"]],use_container_width=True,hide_index=True)
else: st.write("No file-level dependency evidence captured yet.")
if a: st.metric("Blast radius",a["blast_radius"],a["blast_radius_reason"])
