import pytest
from neuralforge.domain.projects import Project, ProjectId, DomainError
from neuralforge.adapters.sqlite_store import SQLiteStore
from neuralforge.application.use_cases import ProjectService, CsvDatasetService


def test_project_validation_and_rename():
    project = Project(ProjectId.new(), "  churn ", "tabular_classification")
    assert project.name == "churn"
    project.rename("renamed")
    assert project.name == "renamed"
    with pytest.raises(DomainError): Project(ProjectId.new(), "", "tabular_classification")


def test_project_persistence(tmp_path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    service = ProjectService(store)
    created = service.create("Demo", "tabular_regression")
    assert store.get(created.id.value).name == "Demo"
    assert len(service.list()) == 1
    assert service.delete(created.id.value)
    assert store.get(created.id.value) is None


def test_csv_profile_and_safe_file_storage(tmp_path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    project = ProjectService(store).create("Data", "tabular_classification")
    service = CsvDatasetService(store, tmp_path)
    profile = service.ingest(project.id.value, "../unsafe.csv", b"age,label\n20,yes\n30,no\n30,no\n")
    assert profile.row_count == 3
    assert profile.duplicate_rows == 1
    assert profile.filename == "unsafe.csv"
    assert profile.columns[0].inferred_type == "numeric"
    assert (tmp_path / "datasets" / project.id.value / f"{profile.dataset_id}.csv").exists()


def test_csv_rejects_inconsistent_rows(tmp_path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    project = ProjectService(store).create("Data", "tabular_regression")
    with pytest.raises(ValueError, match="Row 2"):
        CsvDatasetService(store, tmp_path).ingest(project.id.value, "bad.csv", b"a,b\n1\n")
