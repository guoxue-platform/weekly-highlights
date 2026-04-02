# 龙虾团队荣誉积分系统

> 版本：v1.0 | 日期：2026-04-02 | 负责人：DevAgent

## 概述

荣誉积分系统用于记录团队成员的正面贡献积分，按周统计、清零、归档，形成持续激励闭环。

### 核心规则

| 规则 | 说明 |
|------|------|
| 统计周期 | 每周一 00:00（UTC）至周日 23:59 |
| 清零时点 | 每周一 00:05（UTC），cron job 自动执行 |
| 录入权限 | dev（专属） |
| 清零权限 | main（专属） |
| 读取权限 | 全员可读 |

## 数据库

- **SQLite**：文件路径 `data/points.db`
- **三张表**：`records` / `weekly_current` / `weekly_history`

## 快速启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

API 文档：http://localhost:8000/docs

## 字段设计（fin 提供）

### records（原始记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增ID |
| proposer | TEXT | 提议人 |
| target | TEXT | 被记分人 |
| reason | TEXT | 事由 |
| delta | INTEGER | 分值（-5/-3/-1/1/3/5） |
| recorder | TEXT | 记录人 |
| week_num | TEXT | 周数（YYYY-Www） |
| created_at | DATETIME | 时间 |

### weekly_current（周看板表）

| 字段 | 类型 | 说明 |
|------|------|------|
| agent | TEXT | 人员 |
| week_num | TEXT | 周数 |
| total_points | INTEGER | 当周累计 |

### weekly_history（历史归档表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增ID |
| agent | TEXT | 人员 |
| week_num | TEXT | 周数 |
| total_points | INTEGER | 清零前累计 |
| archived_at | DATETIME | 归档时间 |

## API 接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/v1/points/record | 录入积分记录 | dev |
| GET | /api/v1/points/weekly | 当周看板 | 全员 |
| GET | /api/v1/points/records | 原始记录查询 | 全员 |
| GET | /api/v1/points/history | 历史归档 | 全员 |
| POST | /api/v1/points/reset | 清零归档 | main |

## 部署

- **Backend**：Railway / 本地
- **数据库**：SQLite 文件（Git 版本化）
- **CI/CD**：GitHub Actions
