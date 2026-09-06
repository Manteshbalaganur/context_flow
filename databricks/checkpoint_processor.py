# Databricks notebook source
# COMMAND ----------
# CheckIN / hackathon-data-pipeline / checkpoint_processor
#
# The producer that calls this notebook must send real Entire records with the
# active CheckIN project_id. Never overwrite another project's rows.

import json
from datetime import datetime
from pyspark.sql import Row
from pyspark.sql import functions as F

spark.sql("CREATE DATABASE IF NOT EXISTS checkin_db")
spark.sql("CREATE DATABASE IF NOT EXISTS processed_db")

spark.sql("""
CREATE TABLE IF NOT EXISTS checkin_db.raw_checkpoints (
    project_id STRING, checkpoint_id STRING, timestamp STRING, agent STRING,
    message STRING, files_changed STRING, raw_context STRING, branch STRING,
    ingestion_time TIMESTAMP
) USING DELTA
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS processed_db.llm_insights (
    project_id STRING, checkpoint_id STRING, timestamp STRING, agent STRING,
    intent STRING, status STRING, summary STRING, risk_level STRING,
    completion_score INT, recommendations STRING, unresolved_issues STRING,
    files_changed STRING, processing_time TIMESTAMP
) USING DELTA
""")

# COMMAND ----------
# Option A (recommended): pass a JSON array through a job parameter named
# `checkpoints_json`. Each item requires project_id, checkpoint_id, timestamp,
# agent, message, files_changed, raw_context, and branch.
# Option B: replace this sample with a source that runs `entire checkpoint list
# --json` in your ingestion environment and posts those real records.

try:
    checkpoints_json = dbutils.widgets.get("checkpoints_json")
except Exception:
    checkpoints_json = ""

sample_checkpoints = [
    {"project_id": "REPLACE_WITH_CHECKIN_PROJECT_ID", "checkpoint_id": "cp_demo_001",
     "timestamp": "2026-09-06T10:30:00", "agent": "codex",
     "message": "Initial CheckIn setup with Streamlit dashboard",
     "files_changed": "app.py, README.md, requirements.txt",
     "raw_context": "Set up CheckIn project with Streamlit", "branch": "checkin"}
]
records = json.loads(checkpoints_json) if checkpoints_json.strip() else sample_checkpoints
raw_df = spark.createDataFrame(records).withColumn("ingestion_time", F.current_timestamp())

# Idempotent raw upsert: same project/checkpoint can be rerun safely.
raw_df.createOrReplaceTempView("incoming_raw_checkpoints")
spark.sql("""
MERGE INTO checkin_db.raw_checkpoints target
USING incoming_raw_checkpoints source
ON target.project_id = source.project_id AND target.checkpoint_id = source.checkpoint_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")

# COMMAND ----------
def fallback_analysis(record):
    message = record["message"] or "Code change in progress"
    has_todo = "todo" in message.lower() or "unfinished" in message.lower()
    return {
        "intent": message[:180],
        "status": "In Progress" if has_todo else "Complete",
        "summary": message[:250],
        "risk_level": "Medium" if has_todo else "Low",
        "completion_score": 70 if has_todo else 90,
        "recommendations": "Review changed files and run verification.",
        "unresolved_issues": "Check open TODOs." if has_todo else "None recorded",
    }

# For hackathon reliability this notebook retains deterministic fallback analysis.
# Replace fallback_analysis with an approved AI-function or model-serving call in
# your Databricks workspace when that endpoint is enabled.
processed = []
for record in raw_df.collect():
    item = record.asDict()
    insight = fallback_analysis(item)
    processed.append({
        "project_id": item["project_id"], "checkpoint_id": item["checkpoint_id"],
        "timestamp": item["timestamp"], "agent": item["agent"],
        "intent": insight["intent"], "status": insight["status"],
        "summary": insight["summary"], "risk_level": insight["risk_level"],
        "completion_score": int(insight["completion_score"]),
        "recommendations": insight["recommendations"],
        "unresolved_issues": insight["unresolved_issues"],
        "files_changed": item["files_changed"], "processing_time": datetime.utcnow(),
    })

processed_df = spark.createDataFrame(processed)
processed_df.createOrReplaceTempView("incoming_llm_insights")
spark.sql("""
MERGE INTO processed_db.llm_insights target
USING incoming_llm_insights source
ON target.project_id = source.project_id AND target.checkpoint_id = source.checkpoint_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")

display(processed_df.select("project_id", "checkpoint_id", "intent", "status", "risk_level", "completion_score"))
