"""Application services for project and CSV dataset workflows."""
import csv
import math
import statistics
from collections import Counter
from pathlib import Path
from uuid import uuid4
from neuralforge.domain.projects import Project, ProjectId
from neuralforge.domain.datasets import DatasetProfile, ColumnProfile


class ProjectService:
    def __init__(self, repository): self.repository = repository

    def create(self, name: str, task_type: str, description: str = "", owner_id: str | None = None) -> Project:
        project = Project(ProjectId.new(), name, task_type, description)
        self.repository.add(project, owner_id)
        return project

    def list(self): return self.repository.list()

    def rename(self, project_id: str, name: str) -> Project:
        project = self.repository.get(project_id)
        if project is None: raise KeyError(project_id)
        project.rename(name)
        self.repository.update(project)
        return project

    def delete(self, project_id: str) -> bool: return self.repository.delete(project_id)


class CsvDatasetService:
    MAX_BYTES = 100 * 1024 * 1024
    MAX_COLUMNS = 500
    SAMPLE_LIMIT = 5

    def __init__(self, repository, storage_root: Path):
        self.repository, self.storage_root = repository, Path(storage_root)

    def ingest(self, project_id: str, filename: str, content: bytes) -> DatasetProfile:
        max_bytes=self.repository.get_global_config().get("max_upload_bytes",self.MAX_BYTES)
        if len(content) > max_bytes: raise ValueError(f"CSV exceeds the configured {max_bytes // (1024*1024)} MiB upload limit.")
        if not content: raise ValueError("The uploaded file is empty.")
        project = self.repository.get(project_id)
        if project is None: raise KeyError(project_id)
        try:
            text = content.decode("utf-8-sig")
            rows = list(csv.reader(text.splitlines()))
        except (UnicodeDecodeError, csv.Error) as exc:
            raise ValueError("Could not parse CSV. Upload a valid UTF-8 CSV file.") from exc
        if not rows or not rows[0] or len(rows[0]) > self.MAX_COLUMNS:
            raise ValueError(f"CSV must contain 1 to {self.MAX_COLUMNS} columns.")
        headers = [h.strip() for h in rows[0]]
        if any(not h for h in headers) or len(set(headers)) != len(headers):
            raise ValueError("CSV headers must be non-empty and unique.")
        if len(rows) < 2: raise ValueError("CSV must contain a header and at least one data row.")
        data = []
        for line_no, row in enumerate(rows[1:], start=2):
            if not row or (len(row) == 1 and not row[0]): continue
            if len(row) != len(headers):
                raise ValueError(f"Row {line_no} has {len(row)} fields; expected {len(headers)}.")
            data.append([v.strip() for v in row])
        if not data: raise ValueError("CSV contains no data rows.")
        profiles = []
        for index, name in enumerate(headers):
            values = [r[index] for r in data]
            present = [v for v in values if v != ""]
            numeric = _numeric_values(present)
            kind = "numeric" if present and numeric is not None else "categorical"
            numeric_summary = None
            if numeric is not None and numeric:
                numeric_summary = {"min": min(numeric), "max": max(numeric), "mean": statistics.fmean(numeric),
                    "std": statistics.pstdev(numeric), "median": statistics.median(numeric)}
            counts = Counter(present)
            profiles.append(ColumnProfile(name, kind, len(values)-len(present), len(counts),
                tuple(list(dict.fromkeys(present))[:self.SAMPLE_LIMIT]), numeric_summary,
                tuple(counts.most_common(10)) if kind != "numeric" else ()))
        duplicates = len(data) - len({tuple(row) for row in data})
        dataset_id = str(uuid4())
        safe_name = Path(filename.replace('\\', '/')).name[:180] or "dataset.csv"
        stored = f"{dataset_id}.csv"
        directory = self.storage_root / "datasets" / project_id
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / stored
        temp = directory / f".{stored}.tmp"
        temp.write_bytes(content)
        temp.replace(destination)
        profile = DatasetProfile(dataset_id, project_id, safe_name, len(data), len(headers), duplicates, tuple(profiles))
        try:
            self.repository.add_profile(profile, stored)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return profile


def _numeric_values(values):
    try:
        result = [float(v) for v in values]
        if not all(math.isfinite(v) for v in result): return None
        return result
    except (ValueError, TypeError):
        return None
