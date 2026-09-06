from datetime import datetime, timezone
from uuid import uuid4
def now_iso(): return datetime.now(timezone.utc).isoformat()
def new_id(prefix): return f"{prefix}_{uuid4().hex[:12]}"
def compact(items): return [item for item in (items or []) if item]
