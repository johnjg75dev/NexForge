"""Project domain objects. These classes contain invariants, not persistence or HTTP code."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


class DomainError(ValueError):
    """A user-correctable domain invariant violation."""


@dataclass(frozen=True)
class ProjectId:
    value: str

    @classmethod
    def new(cls) -> "ProjectId":
        return cls(str(uuid4()))


@dataclass
class Project:
    id: ProjectId
    name: str
    task_type: str
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    SUPPORTED_TASKS = frozenset({"tabular_classification", "tabular_regression", "text_classification"})

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.description = self.description.strip()
        if not 1 <= len(self.name) <= 80:
            raise DomainError("Project name must contain 1 to 80 characters.")
        if self.task_type not in self.SUPPORTED_TASKS:
            raise DomainError(f"Unsupported task type: {self.task_type}")
        if len(self.description) > 500:
            raise DomainError("Description must be at most 500 characters.")

    def rename(self, name: str) -> None:
        clean = name.strip()
        if not 1 <= len(clean) <= 80:
            raise DomainError("Project name must contain 1 to 80 characters.")
        self.name = clean
        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {"id": self.id.value, "name": self.name, "task_type": self.task_type,
                "description": self.description, "created_at": self.created_at,
                "updated_at": self.updated_at}

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(ProjectId(data["id"]), data["name"], data["task_type"],
                   data.get("description", ""), data["created_at"], data["updated_at"])
