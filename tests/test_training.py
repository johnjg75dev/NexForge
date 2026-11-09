import time
from neuralforge.adapters.sqlite_store import SQLiteStore
from neuralforge.application.use_cases import ProjectService, CsvDatasetService
from neuralforge.application.training import LocalTrainingService


def test_real_mlp_classification_run_persists_metrics_and_artifact(tmp_path):
    store=SQLiteStore(tmp_path/"db.sqlite")
    project=ProjectService(store).create("Iris-like", "tabular_classification")
    rows=["x,color,label"]
    for i in range(40):
        rows.append(f"{i if i<20 else i+30},{'blue' if i<20 else 'red'},{'A' if i<20 else 'B'}")
    dataset=CsvDatasetService(store,tmp_path).ingest(project.id.value,"fixture.csv",("\n".join(rows)+"\n").encode())
    trainer=LocalTrainingService(store,tmp_path)
    run=trainer.start(project.id.value,dataset.dataset_id,"label",{"epochs":30,"hidden_layers":[8],"seed":4})
    deadline=time.time()+45
    while time.time()<deadline:
        saved=store.get_run(run["id"])
        if saved["status"] in ("succeeded","failed"): break
        time.sleep(.1)
    assert saved["status"]=="succeeded", saved["error"]
    assert "accuracy" in saved["result"]["metrics"]
    assert (tmp_path/saved["result"]["model_artifact"]).exists()
