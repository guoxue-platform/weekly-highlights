"""
Weekly Highlights FastAPI Backend
"""
import sqlite3
import uuid
from datetime import date, datetime
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse

# Database path
DB_PATH = "/home/node/.openclaw/workspace-main/本周高光/data/本周高光.db"

app = FastAPI(title="Weekly Highlights API", version="1.0.0")

# ─── Helpers ─────────────────────────────────────────────────────────────────

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)

def current_week() -> str:
    today = date.today()
    y, w = today.isocalendar()[:2]
    return f"{y}-W{w:02d}"

def get_dashboard_stats(week: str) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT total_score, record_count, top_agent FROM dashboard WHERE week = ?",
            (week,)
        )
        row = cursor.fetchone()
        if not row:
            return {"total_score": 0, "record_count": 0, "top_agent": None}
        return row_to_dict(row)

def rebuild_dashboard(week: str):
    """Recalculate dashboard totals from records."""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT agent, SUM(score) as total FROM records WHERE week = ? GROUP BY agent ORDER BY total DESC",
            (week,)
        )
        rows = cursor.fetchall()
        total_score = sum(r["total"] for r in rows)
        record_count = conn.execute(
            "SELECT COUNT(*) FROM records WHERE week = ?", (week,)
        ).fetchone()[0]
        top_agent = rows[0]["agent"] if rows else None
        now = datetime.utcnow().isoformat()
        conn.execute(
            """INSERT INTO dashboard (week, total_score, record_count, top_agent, last_updated)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(week) DO UPDATE SET
               total_score=excluded.total_score,
               record_count=excluded.record_count,
               top_agent=excluded.top_agent,
               last_updated=excluded.last_updated""",
            (week, total_score, record_count, top_agent, now)
        )
        conn.commit()

# ─── Permission ────────────────────────────────────────────────────────────────

def require_role(required: set):
    def inner(role: Optional[str] = Header(None)):
        if role not in required:
            raise HTTPException(403, "Forbidden")
        return role
    return inner

can_write = require_role({"fin", "main"})
is_main   = require_role({"main"})

# ─── GET /api/records ─────────────────────────────────────────────────────────

@app.get("/api/records")
def get_records(
    agent: Optional[str] = Query(None),
    week:  Optional[str] = Query(None),
    from_: Optional[str]  = Query(None, alias="from"),
    to:    Optional[str]  = Query(None),
):
    conditions = []
    params = []

    if agent:
        conditions.append("agent = ?")
        params.append(agent)
    if week:
        conditions.append("week = ?")
        params.append(week)
    if from_:
        conditions.append("date >= ?")
        params.append(from_)
    if to:
        conditions.append("date <= ?")
        params.append(to)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_db() as conn:
        cursor = conn.execute(f"SELECT * FROM records {where} ORDER BY created_at DESC", params)
        rows = [row_to_dict(r) for r in cursor.fetchall()]

    return JSONResponse({"data": rows, "total": len(rows)})

# ─── GET /api/dashboard ───────────────────────────────────────────────────────

@app.get("/api/dashboard")
def get_current_dashboard():
    week = current_week()
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM dashboard WHERE week = ?", (week,))
        row = cursor.fetchone()
        if not row:
            row = {"week": week, "total_score": 0, "record_count": 0, "top_agent": None, "last_updated": None}
        else:
            row = row_to_dict(row)
    return JSONResponse({"data": row, "total": 1})

@app.get("/api/dashboard/{week}")
def get_dashboard_by_week(week: str):
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM dashboard WHERE week = ?", (week,))
        row = cursor.fetchone()
        if not row:
            row = {"week": week, "total_score": 0, "record_count": 0, "top_agent": None, "last_updated": None}
        else:
            row = row_to_dict(row)
    return JSONResponse({"data": row, "total": 1})

# ─── GET /api/history ──────────────────────────────────────────────────────────

@app.get("/api/history")
def get_history(
    from_: Optional[str] = Query(None, alias="from"),
    to:    Optional[str] = Query(None),
):
    conditions = []
    params = []
    if from_:
        conditions.append("week >= ?")
        params.append(from_)
    if to:
        conditions.append("week <= ?")
        params.append(to)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_db() as conn:
        cursor = conn.execute(f"SELECT * FROM history {where} ORDER BY week DESC", params)
        rows = [row_to_dict(r) for r in cursor.fetchall()]

    return JSONResponse({"data": rows, "total": len(rows)})

# ─── POST /api/records ────────────────────────────────────────────────────────

@app.post("/api/records")
def create_record(
    body: dict,
    role: str = Header(..., alias="X-User-Role"),
):
    if role not in {"fin", "main"}:
        raise HTTPException(403, "Forbidden")

    required = ["agent", "score", "reason", "category", "recorder", "date"]
    for field in required:
        if field not in body:
            raise HTTPException(422, f"Missing field: {field}")

    week = body.get("week") or current_week()
    now = datetime.utcnow().isoformat()
    record_id = str(uuid.uuid4())

    with get_db() as conn:
        conn.execute(
            """INSERT INTO records (id, agent, score, reason, category, recorder, date, summary, remark, week, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (record_id, body["agent"], body["score"], body["reason"], body["category"],
             body["recorder"], body["date"], body.get("summary"), body.get("remark"),
             week, now)
        )
        conn.commit()

    rebuild_dashboard(week)

    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM records WHERE id = ?", (record_id,))
        row = row_to_dict(cursor.fetchone())

    return JSONResponse({"data": row, "total": 1}, status_code=201)

# ─── DELETE /api/records/{id} ────────────────────────────────────────────────

@app.delete("/api/records/{record_id}")
def delete_record(record_id: str, role: str = Header(..., alias="X-User-Role")):
    if role != "main":
        raise HTTPException(403, "Forbidden")

    with get_db() as conn:
        cursor = conn.execute("SELECT week FROM records WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(404, "Record not found")
        week = row["week"]
        conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
        conn.commit()

    rebuild_dashboard(week)
    return JSONResponse({"data": None, "total": 0})

# ─── POST /api/dashboard/archive ──────────────────────────────────────────────

@app.post("/api/dashboard/archive")
def archive_week(role: str = Header(..., alias="X-User-Role")):
    if role != "main":
        raise HTTPException(403, "Forbidden")

    week = current_week()

    with get_db() as conn:
        # Get dashboard data
        cursor = conn.execute("SELECT * FROM dashboard WHERE week = ?", (week,))
        dash = cursor.fetchone()
        if not dash:
            raise HTTPException(400, "No dashboard data to archive")

        dash = row_to_dict(dash)
        # Build summary from records
        rec_cursor = conn.execute(
            "SELECT agent, score, reason FROM records WHERE week = ?", (week,)
        )
        records = rec_cursor.fetchall()
        summary_parts = [f"{r['agent']}: {r['reason']} (+{r['score']})" for r in records]
        summary = "; ".join(summary_parts)

        now = datetime.utcnow().isoformat()

        # Insert into history
        conn.execute(
            """INSERT INTO history (week, total_score, record_count, top_agent, summary, archived_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(week) DO UPDATE SET
               total_score=excluded.total_score, record_count=excluded.record_count,
               top_agent=excluded.top_agent, summary=excluded.summary, archived_at=excluded.archived_at""",
            (week, dash["total_score"], dash["record_count"], dash["top_agent"], summary, now)
        )

        # Clear records and dashboard
        conn.execute("DELETE FROM records WHERE week = ?", (week,))
        conn.execute("DELETE FROM dashboard WHERE week = ?", (week,))
        conn.commit()

    return JSONResponse({"data": {"week": week, "archived": True}, "total": 1})

# ─── PUT /api/dashboard/reset ────────────────────────────────────────────────

@app.put("/api/dashboard/reset")
def reset_dashboard(role: str = Header(..., alias="X-User-Role")):
    if role != "main":
        raise HTTPException(403, "Forbidden")

    week = current_week()
    now = datetime.utcnow().isoformat()

    with get_db() as conn:
        conn.execute(
            """INSERT INTO dashboard (week, total_score, record_count, top_agent, last_updated)
               VALUES (?, 0, 0, NULL, ?)
               ON CONFLICT(week) DO UPDATE SET
               total_score=0, record_count=0, top_agent=NULL, last_updated=excluded.last_updated""",
            (week, now)
        )
        conn.execute("DELETE FROM records WHERE week = ?", (week,))
        conn.commit()

    return JSONResponse({"data": {"week": week, "reset": True}, "total": 1})

# ─── Health check ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}
