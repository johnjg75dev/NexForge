"""Dataset/profile domain value objects."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnProfile:
    name: str
    inferred_type: str
    missing: int
    unique: int
    sample_values: tuple[str, ...]
    numeric: dict | None = None
    top_values: tuple[tuple[str, int], ...] = ()

    def to_dict(self) -> dict:
        return {"name": self.name, "inferred_type": self.inferred_type,
                "missing": self.missing, "unique": self.unique,
                "sample_values": list(self.sample_values), "numeric": self.numeric,
                "top_values": [{"value": v, "count": n} for v, n in self.top_values]}


@dataclass(frozen=True)
class DatasetProfile:
    dataset_id: str
    project_id: str
    filename: str
    row_count: int
    column_count: int
    duplicate_rows: int
    columns: tuple[ColumnProfile, ...]
    target_column: str | None = None

    def to_dict(self) -> dict:
        return {"dataset_id": self.dataset_id, "project_id": self.project_id,
                "filename": self.filename, "row_count": self.row_count,
                "column_count": self.column_count, "duplicate_rows": self.duplicate_rows,
                "target_column": self.target_column,
                "columns": [c.to_dict() for c in self.columns]}
