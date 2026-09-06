import streamlit as st
import pandas as pd
from utils.ui import style,selected_data
from services import databricks_service
style(); p,e,_=selected_data(); st.title("Code changes")
if not e: st.info("No Git evidence has been collected yet."); st.stop()
g=e["git_evidence"]; c1,c2,c3=st.columns(3); c1.metric("Branch",g.get("branch","—")); c2.metric("Latest commit",g.get("latest_commit","—")); c3.metric("Files",len(g.get("changed_files",[])))
for warning in g.get("warnings",[]): st.warning(warning)
changes=databricks_service.project_rows("code_changes",p.project_id)
if changes: st.dataframe(pd.DataFrame(changes)[["file_path","change_type","insertions","deletions","diff_summary","timestamp"]],use_container_width=True,hide_index=True)
else: st.caption("No working-tree file changes were captured. Recent commits are listed below.")
if g.get("commits"): st.dataframe(pd.DataFrame(g["commits"]),use_container_width=True,hide_index=True)
