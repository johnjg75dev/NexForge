"""Real local CPU neural-network training service for tabular tasks.

This adapter uses scikit-learn's MLP implementation for the initial execution
slice. It is not presented as framework-neutral or GPU-capable.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import csv, json, traceback


class LocalTrainingService:
    def __init__(self, store, storage_root: Path, workers=1):
        self.store, self.storage_root = store, Path(storage_root)
        self.pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="nf-train")

    def start(self, project_id: str, dataset_id: str, target: str, config: dict):
        from neuralforge.domain.projects import Project
        project = self.store.get(project_id)
        if not project: raise KeyError(project_id)
        source = self.store.dataset_source(dataset_id)
        if not source or source["project_id"] != project_id: raise KeyError(dataset_id)
        if not target: raise ValueError("Select a target column before training.")
        profile = json.loads(source["profile_json"])
        if target not in [c["name"] for c in profile["columns"]]: raise ValueError("Target column is not in this dataset.")
        epochs = int(config.get("epochs", 100))
        if not 1 <= epochs <= 1000: raise ValueError("Epochs must be between 1 and 1000.")
        hidden = config.get("hidden_layers", [64, 32])
        if not isinstance(hidden, list) or not 1 <= len(hidden) <= 5 or any(not isinstance(x, int) or not 1 <= x <= 2048 for x in hidden):
            raise ValueError("Hidden layers must be a list of 1 to 5 widths, each from 1 to 2048.")
        if project.task_type == "text_classification":
            text_candidates = [c["name"] for c in profile["columns"] if c["name"] != target and c["inferred_type"] == "categorical"]
            text_column = config.get("text_column")
            if not text_column or text_column not in text_candidates: raise ValueError("Choose a text input column (currently inferred as categorical text).")
        else: text_column = None
        now = datetime.now(timezone.utc).isoformat()
        run = {"id": str(uuid4()), "project_id": project_id, "dataset_id": dataset_id,
               "target_column": target, "task_type": project.task_type, "status": "queued",
               "config": {"epochs": epochs, "hidden_layers": hidden, "seed": int(config.get("seed",42)),
                          "validation_fraction": 0.2, "text_column": text_column},
               "created_at": now, "updated_at": now}
        self.store.add_run(run)
        self.pool.submit(self._execute, run)
        return self.store.get_run(run["id"])

    def _execute(self, run):
        run_id = run["id"]
        self.store.update_run(run_id, "running")
        try:
            import numpy as np
            from sklearn.compose import ColumnTransformer
            from sklearn.impute import SimpleImputer
            from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, mean_absolute_error, mean_squared_error, r2_score
            from sklearn.model_selection import train_test_split
            from sklearn.neural_network import MLPClassifier, MLPRegressor
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import OneHotEncoder, StandardScaler
            source = self.store.dataset_source(run["dataset_id"])
            path = self.storage_root / "datasets" / run["project_id"] / source["stored_name"]
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
            target = run["target_column"]
            y_raw = [r[target] for r in rows]
            if any(v is None or v.strip()=="" for v in y_raw): raise ValueError("Target contains missing values; configure target cleaning before training.")
            task = run["task_type"]
            numeric, categorical = [], []
            for name in rows[0].keys():
                if name == target: continue
                vals=[r[name].strip() for r in rows if r[name].strip()]
                try:
                    [float(v) for v in vals]
                    numeric.append(name)
                except ValueError:
                    categorical.append(name)
            if task == "text_classification":
                text_column=run["config"]["text_column"]
                features=[(r[text_column] or "") for r in rows]
                from sklearn.feature_extraction.text import TfidfVectorizer
                X=np.array(features, dtype=object).reshape(-1,1)
                prep=ColumnTransformer([("text",TfidfVectorizer(max_features=50000, ngram_range=(1,2)),0)], remainder="drop")
            else:
                if not numeric and not categorical: raise ValueError("No feature columns remain after excluding the target.")
                import pandas as pd
                X=pd.DataFrame([{name:r[name] for name in numeric+categorical} for r in rows], columns=numeric+categorical)
                for column in numeric: X[column]=pd.to_numeric(X[column], errors="coerce")
                transformers=[]
                if numeric: transformers.append(("numeric",Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler())]),numeric))
                if categorical: transformers.append(("categorical",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("encode",OneHotEncoder(handle_unknown="ignore", max_categories=100))]),categorical))
                prep=ColumnTransformer(transformers)
            seed=run["config"]["seed"]
            if task == "tabular_regression":
                y=np.asarray([float(v) for v in y_raw])
                if len(y)<5: raise ValueError("At least 5 rows are required for a train/validation split.")
                stratify=None
                estimator=MLPRegressor(hidden_layer_sizes=tuple(run["config"]["hidden_layers"]), max_iter=run["config"]["epochs"], random_state=seed, early_stopping=True, n_iter_no_change=10)
            else:
                labels=sorted(set(y_raw))
                if len(labels)<2: raise ValueError("Classification requires at least two target classes.")
                counts={label:y_raw.count(label) for label in labels}
                if min(counts.values()) < 2: raise ValueError("Every class needs at least two rows for a stratified train/validation split.")
                from sklearn.preprocessing import LabelEncoder
                label_encoder=LabelEncoder()
                y=label_encoder.fit_transform(y_raw)
                stratify=y
                estimator=MLPClassifier(hidden_layer_sizes=tuple(run["config"]["hidden_layers"]), max_iter=run["config"]["epochs"], random_state=seed, early_stopping=True, n_iter_no_change=10)
            indices=np.arange(len(y))
            train_idx,val_idx=train_test_split(indices,test_size=0.2,random_state=seed,stratify=stratify)
            model=Pipeline([("preprocess",prep),("model",estimator)])
            model.fit(_take(X,train_idx),y[train_idx])
            pred=model.predict(_take(X,val_idx))
            if task=="tabular_regression":
                mse=float(mean_squared_error(y[val_idx],pred))
                result={"metrics":{"mae":float(mean_absolute_error(y[val_idx],pred)),"mse":mse,"rmse":float(mse**0.5),"r2":float(r2_score(y[val_idx],pred))},"train_rows":len(train_idx),"validation_rows":len(val_idx),"target":target,"task_type":task,"model":"sklearn MLPRegressor","classes":[]}
            else:
                labels=list(label_encoder.classes_)
                y_true=label_encoder.inverse_transform(y[val_idx])
                y_pred=label_encoder.inverse_transform(pred)
                result={"metrics":{"accuracy":float(accuracy_score(y_true,y_pred)),"macro_f1":float(f1_score(y_true,y_pred,average="macro",zero_division=0)),"weighted_f1":float(f1_score(y_true,y_pred,average="weighted",zero_division=0))},"confusion_matrix":confusion_matrix(y_true,y_pred,labels=labels).tolist(),"classification_report":classification_report(y_true,y_pred,labels=labels,output_dict=True,zero_division=0),"classes":labels,"train_rows":len(train_idx),"validation_rows":len(val_idx),"target":target,"task_type":task,"model":"sklearn MLPClassifier"}
            run_dir=self.storage_root/"runs"/run_id
            run_dir.mkdir(parents=True,exist_ok=True)
            import joblib
            joblib.dump(model,run_dir/"model.joblib")
            result["model_artifact"]=f"runs/{run_id}/model.joblib"
            result["seed"]=seed
            self.store.update_run(run_id,"succeeded",result=result)
        except Exception as exc:
            run_dir=self.storage_root/"runs"/run_id
            run_dir.mkdir(parents=True,exist_ok=True)
            (run_dir/"error.log").write_text(traceback.format_exc()[-20000:],encoding="utf-8")
            self.store.update_run(run_id,"failed",error=str(exc)[:1000])


def _take(X, indices):
    import numpy as np
    if hasattr(X, "iloc"): return X.iloc[indices]
    if isinstance(X, np.ndarray): return X[indices]
    return [X[int(i)] for i in indices]
