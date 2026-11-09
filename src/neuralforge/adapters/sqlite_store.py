"""SQLite persistence adapter for local projects, datasets and run records."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from threading import RLock
from neuralforge.domain.projects import Project
from neuralforge.domain.datasets import DatasetProfile


class SQLiteStore:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.database_path, timeout=15)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self):
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL COLLATE NOCASE,
                    task_type TEXT NOT NULL, description TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS datasets (
                    id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    filename TEXT NOT NULL, stored_name TEXT NOT NULL, profile_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_datasets_project ON datasets(project_id);
                CREATE TABLE IF NOT EXISTS dataset_targets (
                    dataset_id TEXT PRIMARY KEY REFERENCES datasets(id) ON DELETE CASCADE,
                    target_column TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    dataset_id TEXT NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
                    target_column TEXT NOT NULL, task_type TEXT NOT NULL, status TEXT NOT NULL,
                    config_json TEXT NOT NULL, result_json TEXT, error TEXT,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_runs_project ON runs(project_id, created_at DESC);
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY, username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    password_hash TEXT NOT NULL, role TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    expires_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS project_shares (
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    role TEXT NOT NULL CHECK(role IN ('viewer','editor')),
                    PRIMARY KEY(project_id,user_id)
                );
                CREATE TABLE IF NOT EXISTS global_config (
                    key TEXT PRIMARY KEY, value_json TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS auth_failures (
                    subject_hash TEXT NOT NULL, source_hash TEXT NOT NULL,
                    failure_count INTEGER NOT NULL, window_started REAL NOT NULL, locked_until REAL NOT NULL,
                    PRIMARY KEY(subject_hash,source_hash)
                );
            """)
            columns = [row[1] for row in db.execute("PRAGMA table_info(projects)").fetchall()]
            if "owner_id" not in columns:
                db.execute("ALTER TABLE projects ADD COLUMN owner_id TEXT REFERENCES users(id)")

    def register_user(self, username: str, password_hash: str):
        from uuid import uuid4
        from datetime import datetime, timezone
        with self._connect() as db:
            count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            user_id, role = str(uuid4()), "admin" if count == 0 else "user"
            db.execute("INSERT INTO users VALUES(?,?,?,?,?)", (user_id, username, password_hash, role, datetime.now(timezone.utc).isoformat()))
            if count == 0:
                db.execute("UPDATE projects SET owner_id=? WHERE owner_id IS NULL", (user_id,))
        return self.get_user(user_id)

    def get_user(self, user_id: str):
        with self._connect() as db: row = db.execute("SELECT id,username,role,created_at FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None

    def user_by_name(self, username: str):
        with self._connect() as db: row = db.execute("SELECT * FROM users WHERE username=? COLLATE NOCASE", (username,)).fetchone()
        return dict(row) if row else None

    def create_session(self, token_hash: str, user_id: str, expires_at: float):
        with self._connect() as db: db.execute("INSERT INTO sessions VALUES(?,?,?)", (token_hash,user_id,expires_at))

    def session_user(self, token_hash: str, now: float):
        with self._connect() as db:
            row=db.execute("SELECT users.id,users.username,users.role,users.created_at FROM sessions JOIN users ON users.id=sessions.user_id WHERE token_hash=? AND expires_at>?", (token_hash,now)).fetchone()
            db.execute("DELETE FROM sessions WHERE expires_at<=?", (now,))
        return dict(row) if row else None

    def delete_session(self, token_hash: str):
        with self._connect() as db: db.execute("DELETE FROM sessions WHERE token_hash=?", (token_hash,))

    def login_lock_state(self, subject_hash: str, source_hash: str, now: float):
        with self._connect() as db:
            row=db.execute("SELECT failure_count,window_started,locked_until FROM auth_failures WHERE subject_hash=? AND source_hash=?",(subject_hash,source_hash)).fetchone()
            if not row: return 0,0.0,0.0
            return tuple(row)

    def record_login_failure(self, subject_hash: str, source_hash: str, now: float, window_seconds: int, threshold: int, lock_seconds: int):
        with self._connect() as db:
            row=db.execute("SELECT failure_count,window_started,locked_until FROM auth_failures WHERE subject_hash=? AND source_hash=?",(subject_hash,source_hash)).fetchone()
            if not row or now-row[1]>window_seconds:
                count,started=1,now
            else: count,started=row[0]+1,row[1]
            locked=now+lock_seconds if count>=threshold else 0.0
            db.execute("INSERT INTO auth_failures VALUES(?,?,?,?,?) ON CONFLICT(subject_hash,source_hash) DO UPDATE SET failure_count=excluded.failure_count,window_started=excluded.window_started,locked_until=excluded.locked_until",(subject_hash,source_hash,count,started,locked))
            return locked

    def clear_login_failures(self, subject_hash: str, source_hash: str):
        with self._connect() as db: db.execute("DELETE FROM auth_failures WHERE subject_hash=? AND source_hash=?",(subject_hash,source_hash))

    def update_password_hash(self, user_id: str, password_hash: str):
        with self._connect() as db:
            db.execute("UPDATE users SET password_hash=? WHERE id=?",(password_hash,user_id))
            db.execute("DELETE FROM sessions WHERE user_id=?",(user_id,))

    def is_owner(self, project_id: str, user_id: str) -> bool:
        with self._connect() as db:
            row=db.execute("SELECT 1 FROM projects WHERE id=? AND owner_id=?", (project_id,user_id)).fetchone()
        return bool(row)

    def can_access(self, project_id: str, user_id: str, write: bool = False) -> bool:
        with self._connect() as db:
            row=db.execute("SELECT owner_id FROM projects WHERE id=?", (project_id,)).fetchone()
            if not row: return False
            if row[0] == user_id: return True
            share=db.execute("SELECT role FROM project_shares WHERE project_id=? AND user_id=?", (project_id,user_id)).fetchone()
            return bool(share and (not write or share[0]=="editor"))

    def list_for_user(self, user_id: str):
        with self._connect() as db:
            rows=db.execute("SELECT DISTINCT p.* FROM projects p LEFT JOIN project_shares s ON s.project_id=p.id WHERE p.owner_id=? OR s.user_id=? ORDER BY p.updated_at DESC", (user_id,user_id)).fetchall()
        return [Project.from_dict(dict(row)) for row in rows]

    def share_project(self, project_id: str, username: str, role: str):
        if role not in ("viewer","editor"): raise ValueError("Role must be viewer or editor.")
        user=self.user_by_name(username)
        if not user: raise KeyError(username)
        with self._connect() as db: db.execute("INSERT INTO project_shares VALUES(?,?,?) ON CONFLICT(project_id,user_id) DO UPDATE SET role=excluded.role",(project_id,user["id"],role))

    def get_global_config(self):
        with self._connect() as db: rows=db.execute("SELECT key,value_json FROM global_config").fetchall()
        return {row[0]:json.loads(row[1]) for row in rows}

    def set_global_config(self, key: str, value):
        from datetime import datetime, timezone
        allowed={"application_name","allow_registration","max_upload_bytes","default_task"}
        if key not in allowed: raise ValueError("This global setting is not configurable.")
        if key == "application_name" and (not isinstance(value,str) or not 1<=len(value)<=80): raise ValueError("Application name must be 1 to 80 characters.")
        if key == "allow_registration" and not isinstance(value,bool): raise ValueError("allow_registration must be boolean.")
        if key == "max_upload_bytes" and (not isinstance(value,int) or not 1_000_000<=value<=100*1024*1024): raise ValueError("max_upload_bytes must be from 1 MB to 100 MiB in this local server build.")
        if key == "default_task" and value not in ("tabular_classification","tabular_regression","text_classification"): raise ValueError("Unsupported default task.")
        with self._connect() as db: db.execute("INSERT INTO global_config VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at",(key,json.dumps(value),datetime.now(timezone.utc).isoformat()))

    def add(self, project: Project, owner_id: str | None = None) -> None:
        with self._lock, self._connect() as db:
            db.execute("INSERT INTO projects(id,name,task_type,description,created_at,updated_at,owner_id) VALUES(?,?,?,?,?,?,?)", (project.id.value, project.name,
                project.task_type, project.description, project.created_at, project.updated_at, owner_id))

    def get(self, project_id: str) -> Project | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
        return Project.from_dict(dict(row)) if row else None

    def list(self) -> list[Project]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
        return [Project.from_dict(dict(row)) for row in rows]

    def update(self, project: Project) -> None:
        with self._lock, self._connect() as db:
            result = db.execute("UPDATE projects SET name=?,task_type=?,description=?,updated_at=? WHERE id=?",
                (project.name, project.task_type, project.description, project.updated_at, project.id.value))
            if result.rowcount == 0: raise KeyError(project.id.value)

    def delete(self, project_id: str) -> bool:
        with self._lock, self._connect() as db:
            cursor = db.execute("DELETE FROM projects WHERE id=?", (project_id,))
            return cursor.rowcount > 0

    def dataset_source(self, dataset_id: str):
        with self._connect() as db:
            row = db.execute("SELECT project_id,stored_name,profile_json FROM datasets WHERE id=?", (dataset_id,)).fetchone()
        return dict(row) if row else None

    def set_target(self, dataset_id: str, target_column: str) -> None:
        with self._connect() as db:
            row = db.execute("SELECT profile_json FROM datasets WHERE id=?", (dataset_id,)).fetchone()
            if not row: raise KeyError(dataset_id)
            profile = json.loads(row[0])
            if target_column not in [column["name"] for column in profile["columns"]]:
                raise ValueError("Target column is not present in this dataset.")
            db.execute("INSERT INTO dataset_targets(dataset_id,target_column) VALUES(?,?) ON CONFLICT(dataset_id) DO UPDATE SET target_column=excluded.target_column", (dataset_id,target_column))

    def get_target(self, dataset_id: str):
        with self._connect() as db:
            row = db.execute("SELECT target_column FROM dataset_targets WHERE dataset_id=?", (dataset_id,)).fetchone()
        return row[0] if row else None

    def add_run(self, run: dict) -> None:
        with self._connect() as db:
            db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?)", (run["id"],run["project_id"],run["dataset_id"],run["target_column"],run["task_type"],run["status"],json.dumps(run["config"]),None,None,run["created_at"],run["updated_at"]))

    def update_run(self, run_id: str, status: str, result=None, error=None) -> None:
        from datetime import datetime, timezone
        with self._connect() as db:
            db.execute("UPDATE runs SET status=?,result_json=?,error=?,updated_at=? WHERE id=?", (status,json.dumps(result) if result is not None else None,error,datetime.now(timezone.utc).isoformat(),run_id))

    def get_run(self, run_id: str):
        with self._connect() as db: row = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        return _run_dict(row) if row else None

    def list_runs(self, project_id: str):
        with self._connect() as db: rows = db.execute("SELECT * FROM runs WHERE project_id=? ORDER BY created_at DESC", (project_id,)).fetchall()
        return [_run_dict(row) for row in rows]

    def add_profile(self, profile: DatasetProfile, stored_name: str) -> None:
        from datetime import datetime, timezone
        with self._lock, self._connect() as db:
            db.execute("INSERT INTO datasets VALUES(?,?,?,?,?,?)", (profile.dataset_id, profile.project_id,
                profile.filename, stored_name, json.dumps(profile.to_dict()), datetime.now(timezone.utc).isoformat()))

    def get_profile(self, dataset_id: str) -> DatasetProfile | None:
        with self._connect() as db: row = db.execute("SELECT profile_json FROM datasets WHERE id=?", (dataset_id,)).fetchone()
        return _profile(json.loads(row[0])) if row else None

    def list_profiles(self, project_id: str) -> list[DatasetProfile]:
        with self._connect() as db: rows = db.execute("SELECT profile_json FROM datasets WHERE project_id=? ORDER BY created_at DESC", (project_id,)).fetchall()
        return [_profile(json.loads(row[0])) for row in rows]


def _profile(data: dict) -> DatasetProfile:
    from neuralforge.domain.datasets import ColumnProfile
    columns = tuple(ColumnProfile(c["name"], c["inferred_type"], c["missing"], c["unique"],
        tuple(c["sample_values"]), c.get("numeric"), tuple((x["value"], x["count"]) for x in c.get("top_values", [])))
        for c in data["columns"])
    return DatasetProfile(data["dataset_id"], data["project_id"], data["filename"],
        data["row_count"], data["column_count"], data["duplicate_rows"], columns, data.get("target_column"))


def _run_dict(row):
    value = dict(row)
    value["config"] = json.loads(value.pop("config_json"))
    value["result"] = json.loads(value.pop("result_json")) if value.get("result_json") else None
    value.pop("result_json", None)
    return value
