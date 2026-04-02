-- 荣誉积分系统数据库 Schema
-- SQLite

-- 原始记录表
CREATE TABLE IF NOT EXISTS records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    proposer    TEXT    NOT NULL,
    target      TEXT    NOT NULL,
    reason      TEXT    NOT NULL,
    delta       INTEGER NOT NULL CHECK (delta IN (-5, -3, -1, 1, 3, 5)),
    recorder    TEXT    NOT NULL,
    week_num    TEXT    NOT NULL,
    created_at  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_records_week_num   ON records(week_num);
CREATE INDEX IF NOT EXISTS idx_records_target     ON records(target);
CREATE INDEX IF NOT EXISTS idx_records_proposer   ON records(proposer);

-- 周看板表（当周实时累计）
CREATE TABLE IF NOT EXISTS weekly_current (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    target       TEXT    NOT NULL UNIQUE,
    total_points INTEGER NOT NULL DEFAULT 0,
    week_num     TEXT    NOT NULL,
    updated_at   TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_weekly_current_target ON weekly_current(target);

-- 周统计历史表（清零前归档）
CREATE TABLE IF NOT EXISTS weekly_history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    target        TEXT    NOT NULL,
    total_points  INTEGER NOT NULL,
    week_num      TEXT    NOT NULL,
    archived_at   TEXT    NOT NULL,
    archived_by   TEXT    NOT NULL DEFAULT 'main',
    UNIQUE(target, week_num)
);

CREATE INDEX IF NOT EXISTS idx_weekly_history_week    ON weekly_history(week_num);
CREATE INDEX IF NOT EXISTS idx_weekly_history_target  ON weekly_history(target);
