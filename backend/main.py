"""
龙虾团队荣誉积分系统 - FastAPI Backend
版本：v1.0 | 日期：2026-04-02
"""

import os
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ============ 配置 ============
DATABASE_PATH = os.getenv("DATABASE_PATH", "/home/node/.openclaw/workspace-dev/projects/weekly-highlights/data/points.db")
ALLOWED_RECORDERS = {"dev"}  # 录入权限
ALLOWED_RESETTERS = {"main"}  # 清零权限

# ============ 数据库工具 ============
def get_db():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库（创建表）"""
    schema_path = Path(__file__).parent / "schema.sql"
    conn = get_db()
    try:
        with open(schema_path) as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()

# ============ Pydantic 模型 ============
class RecordCreate(BaseModel):
    proposer: str
    target: str
    reason: str
    delta: int = Field(..., ge=-5, le=5)
    recorder: str

class RecordResponse(BaseModel):
    id: int
    proposer: str
    target: str
    reason: str
    delta: int
    recorder: str
    week_num: str
    created_at: str

class WeeklyCurrent(BaseModel):
    agent: str
    week_num: str
    total_points: int

class WeeklyHistory(BaseModel):
    id: int
    agent: str
    week_num: str
    total_points: int
    archived_at: str
    archived_by: str

# ============ 工具函数 ============
def get_week_num(dt: datetime = None) -> str:
    """获取 ISO 周标识（YYYY-Www）"""
    if dt is None:
        dt = datetime.utcnow()
    week = dt.isocalendar()
    return f"{week[0]}-W{week[1]:02d}"

def sync_weekly_current(target: str, week_num: str, conn: sqlite3.Connection):
    """同步周看板：根据 records 计算当周累计并更新 weekly_current"""
    cursor = conn.execute(
        "SELECT COALESCE(SUM(delta), 0) FROM records WHERE target = ? AND week_num = ?",
        (target, week_num)
    )
    total = cursor.fetchone()[0]
    now = datetime.utcnow().isoformat()
    conn.execute("""
        INSERT INTO weekly_current (target, total_points, week_num, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(target) DO UPDATE SET
            total_points = excluded.total_points,
            week_num = excluded.week_num,
            updated_at = excluded.updated_at
    """, (target, total, week_num, now))
    conn.commit()

# ============ FastAPI 应用 ============
app = FastAPI(
    title="龙虾团队荣誉积分系统",
    version="1.0.0",
    description="按周统计、清零、归档的团队积分管理系统"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

# ============ API 路由 ============

@app.post("/api/v1/points/record", response_model=RecordResponse)
def create_record(record: RecordCreate):
    """录入积分记录（dev 专属）"""
    if record.recorder not in ALLOWED_RECORDERS:
        raise HTTPException(status_code=403, detail="无录入权限")

    week_num = get_week_num()
    created_at = datetime.utcnow().isoformat()

    conn = get_db()
    try:
        cursor = conn.execute("""
            INSERT INTO records (proposer, target, reason, delta, recorder, week_num, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (record.proposer, record.target, record.reason, record.delta, record.recorder, week_num, created_at))
        record_id = cursor.lastrowid
        conn.commit()

        # 同步周看板
        sync_weekly_current(record.target, week_num, conn)

        return RecordResponse(
            id=record_id,
            proposer=record.proposer,
            target=record.target,
            reason=record.reason,
            delta=record.delta,
            recorder=record.recorder,
            week_num=week_num,
            created_at=created_at
        )
    finally:
        conn.close()

@app.get("/api/v1/points/weekly", response_model=list[WeeklyCurrent])
def get_weekly_current(week_num: Optional[str] = Query(None)):
    """获取当周看板（全员可读）"""
    if week_num is None:
        week_num = get_week_num()

    conn = get_db()
    try:
        cursor = conn.execute(
            "SELECT target as agent, week_num, total_points FROM weekly_current WHERE week_num = ?",
            (week_num,)
        )
        rows = cursor.fetchall()
        return [WeeklyCurrent(agent=r["agent"], week_num=r["week_num"], total_points=r["total_points"]) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/points/records", response_model=list[RecordResponse])
def get_records(
    target: Optional[str] = Query(None),
    week_num: Optional[str] = Query(None),
    limit: int = Query(100, le=500)
):
    """查询原始记录（全员可读）"""
    conn = get_db()
    try:
        query = "SELECT * FROM records WHERE 1=1"
        params = []
        if target:
            query += " AND target = ?"
            params.append(target)
        if week_num:
            query += " AND week_num = ?"
            params.append(week_num)
        query += f" ORDER BY created_at DESC LIMIT {limit}"

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return [RecordResponse(**dict(r)) for r in rows]
    finally:
        conn.close()

@app.get("/api/v1/points/history", response_model=list[WeeklyHistory])
def get_history(
    agent: Optional[str] = Query(None),
    week_num: Optional[str] = Query(None)
):
    """查询历史归档（全员可读）"""
    conn = get_db()
    try:
        query = "SELECT id, target as agent, week_num, total_points, archived_at, archived_by FROM weekly_history WHERE 1=1"
        params = []
        if agent:
            query += " AND target = ?"
            params.append(agent)
        if week_num:
            query += " AND week_num = ?"
            params.append(week_num)
        query += " ORDER BY week_num DESC, target"

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return [WeeklyHistory(**dict(r)) for r in rows]
    finally:
        conn.close()

@app.post("/api/v1/points/reset")
def reset_weekly(
    resetter: str = Query(..., description="执行清零的操作者"),
    target: Optional[str] = Query(None, description="指定成员，为空则清零所有")
):
    """清零当周看板，归档到历史表（main 专属）"""
    if resetter not in ALLOWED_RESETTERS:
        raise HTTPException(status_code=403, detail="无清零权限")

    week_num = get_week_num()
    archived_at = datetime.utcnow().isoformat()

    conn = get_db()
    try:
        # 归档
        if target:
            cursor = conn.execute(
                "SELECT target, total_points, week_num FROM weekly_current WHERE target = ?",
                (target,)
            )
        else:
            cursor = conn.execute("SELECT target, total_points, week_num FROM weekly_current")

        rows = cursor.fetchall()
        for r in rows:
            conn.execute("""
                INSERT OR IGNORE INTO weekly_history (target, total_points, week_num, archived_at, archived_by)
                VALUES (?, ?, ?, ?, ?)
            """, (r["target"], r["total_points"], r["week_num"], archived_at, resetter))

        # 清空当周看板
        if target:
            conn.execute("DELETE FROM weekly_current WHERE target = ?", (target,))
        else:
            conn.execute("DELETE FROM weekly_current")

        conn.commit()
        return {"status": "ok", "archived": len(rows), "week_num": week_num, "reset_by": resetter}
    finally:
        conn.close()

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# ============ 启动 ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
