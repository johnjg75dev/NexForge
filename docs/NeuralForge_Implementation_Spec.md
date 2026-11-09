# NeuralForge — Full Production Product & Engineering Specification

**Status:** Authoritative build specification. **This is not an MVP brief.** Implement the complete product described here: all lifecycle modules, supported task families, integrations, collaboration, deployment, monitoring, SDK, CLI, and desktop/web experiences. No feature may be represented by a mock, fake data, disabled placeholder, TODO, simulated result, or nonfunctional button. A capability is complete only when its end-to-end behavior, error handling, persistence, tests, documentation, and operational requirements are implemented.

## 0. Delivery mandate and interpretation

Build **NeuralForge**, a production-grade, extensible neural-network development platform spanning idea → data → preparation → model → training → debugging → evaluation → deployment → monitoring. Deliver a coherent, working application rather than a visual prototype. Guided mode and Expert mode must operate on the same persisted project and execution services. UI, Python API, CLI, and generated project artifacts must use the same versioned configuration and semantics.

“Fully functioning” means each advertised integration or option connects to the real corresponding provider/library, validates prerequisites, performs the operation, persists results, and reports provider errors. No hard-coded metrics, fake cloud state, fabricated resource estimates, synthetic training progress, canned diagnosis presented as observed fact, or pretend export/deployment. Synthetic data is allowed only when explicitly selected and labeled synthetic. Recommendations and estimates must disclose their evidence, method, and uncertainty. External services require real credentials and connectivity; absence of credentials must produce a guided connection/configuration state, not a successful-looking simulation.

The product must be production-ready for supported deployment environments: secure defaults, authentication and authorization, migrations, backups, observability, bounded resource use, robust job recovery, deployment documentation, test suites, CI, accessibility, and operator runbooks. Production readiness does not mean every conceivable ML architecture can be built; it means every capability enumerated in this specification is implemented completely and the supported/unsupported boundaries are explicit.

### 0.1 Global requirements

1. Implement all sections in this document and the supplied original NeuralForge vision, except where this document narrows or clarifies semantics. Any omitted feature requires an explicit written change request; do not silently scope-reduce.
2. No demo-only screens, fake previews, TODO/FIXME placeholders in delivered workflows, mocked integrations in production code, or controls that do nothing. Test doubles are permitted only in automated tests and local development fixtures, visibly separated from production paths.
3. Every long-running operation is an observable durable job with cancellation, retries where safe, logs, progress, terminal state, and recovery policy.
4. All mutable project inputs are versioned. Runs, evaluations, exports, deployments, and monitoring records reference immutable input snapshots and checksums.
5. All user-visible estimates identify their derivation and assumptions; if the platform lacks sufficient information, show “not available” rather than a guess.
6. Users can export their project and leave the platform without proprietary lock-in: configurations, data references, source code, model artifacts, metrics, and documentation use documented open formats wherever possible.
7. Default operation is local/private. No user content is sent to an LLM, model hub, tracker, cloud, or telemetry provider unless the user explicitly enables that integration and understands what is transmitted.
8. Every module has operational, security, accessibility, localization-ready, and testing requirements—not just a happy-path UI.

## 1. Product, users, and interaction modes

### 1.1 Product promise

NeuralForge is one project-centric platform for ML practitioners from beginner to research/enterprise level. It combines data ingestion and quality, reproducible preprocessing, model construction, training orchestration, debugging, trustworthy evaluation, artifact management, deployment, monitoring, collaboration, and extensibility. The system must not equate high benchmark scores with production suitability or provide unqualified accuracy promises.

### 1.2 User roles

- **Owner:** manages organization/project, members, billing/configuration if applicable, secrets, deletion, and deployments.
- **Admin:** manages projects, roles, connectors, policy, and compute pools within authorized scope.
- **Editor:** changes project, data pipeline, models, training, evaluations, and deployments as permitted.
- **Runner:** starts/cancels runs and evaluates, without changing project governance or secrets.
- **Viewer:** read-only access to permitted project objects and reports.
- **Auditor:** read-only access to audit events and governed artifacts.
- **Local single-user:** all capabilities available locally; same data model and API, with a local owner identity.

Enforce authorization in backend services for every object and operation, not only in the UI. Role/permission matrix must be documented and tested.

### 1.3 Guided and Expert modes

Guided mode contains eight lifecycle phases: Goal, Data, Prepare, Design, Train, Debug & Improve, Evaluate, Deploy. Each phase includes contextual explanation, valid choices, computed preview, warnings, reversible navigation, and a saved configuration. Expert mode exposes all implemented controls, project resources, code/config views, experiment comparison, logs, and job management. Mode switching never forks or discards state. Users may enter any phase directly in Expert mode. Wizard completion is derived from verified persisted prerequisites, not a progress animation.

### 1.4 Product shell

Provide organization/workspace selector (multi-tenant server), project selector, global search, notifications, user/profile/security menu, help/docs, mode switch, and status/health indicators. Project workspace navigation: Overview, Data, Model, Training, Debug, Evaluation, Deployments, Monitoring, Experiments, Artifacts, Collaborators, Settings. Persistent job center lists active/recent jobs across projects the user can access. Responsive desktop and tablet layouts; mobile is for viewing/approvals, not full architecture editing.

## 2. System architecture and deployment topology

### 2.1 Required service boundaries

Implement a versioned API and independently scalable services/processes:

- Web frontend (React/TypeScript or equivalent supported framework).
- API service (FastAPI or equivalent typed API; OpenAPI contract).
- Identity/authentication service integration (OIDC; local development identity provider supported without bypassing production authentication).
- Relational metadata database (PostgreSQL in production; SQLite only for an explicitly supported single-user local install).
- Durable task queue and scheduler (Redis-compatible queue or equivalent with persistence/visibility; production queue configuration documented).
- Worker pools for data profiling/preprocessing, training, hyperparameter search, evaluation, export, deployment, and monitoring; resource classes and concurrency limits are configurable.
- Artifact store abstraction supporting local filesystem for single-user installation and S3-compatible object storage for server deployment, with encryption and lifecycle policies.
- Secret manager abstraction; production secrets encrypted at rest and never returned to clients.
- Optional model-serving runtime and telemetry pipeline, deployed independently from control plane.

Use modular monolith/service decomposition based on operational need; do not create unnecessary microservices. Each job must be idempotent or have an explicit deduplication/recovery strategy. All services expose health/readiness endpoints and structured logs, metrics, and traces.

### 2.2 Supported installations

1. **Local desktop/workstation:** packaged local services or supported desktop shell; binds loopback by default; user data remains local.
2. **Self-hosted team:** Docker Compose for development and a documented Kubernetes production deployment; TLS ingress, OIDC, PostgreSQL, durable queue, object storage, secrets, backups, and monitoring required.
3. **Managed cloud:** deployable reference configuration for AWS, GCP, and Azure with provider-specific identity, object storage, secrets, GPU worker pools, networking, and cost controls. Cloud resources are created only after explicit user consent and credentials.

Provide Docker images, Compose files, Kubernetes Helm chart/manifests, environment variable reference, upgrade/migration procedures, disaster-recovery runbook, and supported version matrix. Do not claim a cloud provider supported until deployment and integration tests pass on it.

### 2.3 Backend/framework adapters

PyTorch is the primary complete adapter. Implement TensorFlow/Keras and JAX adapters as real adapters for the common model/train/evaluate/export contracts, with documented feature compatibility per operation. ONNX is an interoperable import/export/runtime format where supported by operators. Capability discovery is machine-readable and drives UI availability. Unsupported combinations must be rejected with a specific capability error before a job starts; never silently fall back to a different framework or method.

## 3. Canonical domain model, state, and configuration

### 3.1 Core entities

Organization, user, membership, workspace, project, dataset, dataset version, connector, data snapshot, pipeline definition/version, split manifest, model definition/version, pretrained source, training configuration, run, trial, checkpoint, evaluation, report, artifact, deployment, deployment revision, endpoint, monitor, alert, comment, recipe, plugin, secret reference, audit event, and background job. Each has UUID/ULID stable identifiers, tenant scope, created/updated timestamps, owner, status, and explicit retention/deletion semantics.

### 3.2 Immutable run provenance

A run captures: project ID; dataset versions and checksums; source connector and snapshot reference; pipeline version and fitted preprocessing state; split manifest and seed; model architecture and weight origin; framework/library versions; full effective hyperparameters; code/plugin versions; device, driver, accelerator and resource limits; environment/container digest; deterministic settings; start/end times; per-step metrics; checkpoint checksums; logs; and initiating user. Changes create a new version/run. Run metadata can be exported as a reproducibility manifest.

### 3.3 Config contracts

All configurations have a JSON Schema (and generated typed models), explicit schema version, default values, validation rules, deprecation/migration strategy, and round-trip tests. YAML is a human-editable representation of canonical JSON. Unknown fields fail validation unless a named extension namespace owns them. Include generated effective config and diff for every run. Config edits are saved transactionally and preserve previous versions.

### 3.4 State machines

Define server-validated states and transitions for project readiness, ingestion, pipeline validation, run, trial, evaluation, export, deployment, endpoint, and monitor. Long-running jobs: queued, waiting_for_resource, running, cancelling, cancelled, succeeded, failed, timed_out, interrupted. Illegal transitions return conflict errors. Job state survives process restarts. Reconciliation detects orphaned workers and stale leases. Idempotency keys prevent duplicate user submissions on retries.

## 4. Data Engine

### 4.1 Connectors and ingestion

Implement real connectors with test coverage and documented auth setup for:

- Local uploads: CSV, TSV, JSON/JSONL, Parquet, HDF5, common image/audio folder structures, and supported tabular formats. Validate file size, archive expansion, path traversal, decompression bombs, schema, encoding, and row/record bounds.
- SQL: PostgreSQL, MySQL, SQLite, and SQL Server through read-only credential profiles; allow query/table selection, pagination/streaming, schema preview, incremental snapshot where supported. Credentials are secret references and never logged.
- NoSQL: MongoDB connector with projection/filter and sampling limits.
- Object storage: S3, GCS, Azure Blob; prefix/object selection, version/generation-aware snapshot, least-privilege credential guidance.
- REST APIs: configurable endpoint, auth (OAuth2/API key/basic where appropriate), pagination, rate limiting, schema mapping, retry/backoff; SSRF protections and host allowlist controls.
- Streaming: Kafka and Google Pub/Sub ingestion with consumer group, offsets, checkpointed bounded windows, schema evolution and exactly-once claims only if truly provided by connector semantics.
- Public datasets: Hugging Face Datasets and Kaggle APIs with license display/acceptance, user credentials, dataset revision pinning, terms acknowledgement, and no credential sharing.
- Synthetic data: explicit generators for tabular classification/regression, time series, text templates, image patterns; seedable; every artifact marked `synthetic=true` and excluded from real-world performance claims.
- Web collection utilities: only user-specified permitted sources; robots/terms/legal compliance warning, rate limits, domain allowlists, content provenance. No arbitrary open-web crawling.

Connector catalog advertises supported features, credential requirements, limits, and setup. Connector errors are actionable, retriable where appropriate, and preserve offset/checkpoint. Provide connection test and data preview before ingestion.

### 4.2 Data profiling and EDA

Profile type inference and summary stats with sampling strategy and uncertainty disclosure for very large data. Include row/column count, nulls, duplicates, cardinality, numeric quantiles/distributions, categorical frequencies, time range/gaps, class balance, text token/length/vocabulary summaries, vision dimensions/color/channel/corruption summaries, audio duration/sample rate/channel/corruption summaries, graph nodes/edges/components/degree distribution, and stream throughput/lag where applicable. Include histograms, box/QQ plots where meaningful, correlation/covariance with appropriate caveats, outlier candidates, slice previews, and data-quality checks. Charts must remain usable on large datasets and provide accessible data tables and downloads.

Profile calculations must be deterministic for fixed snapshot/sample seed and report sample size, method, and completion. Do not load an unbounded dataset into API memory. Sensitive columns may be marked; previews and reports respect access controls and masking.

### 4.3 Data quality, governance, and lineage

Schema contracts; type/range/null/uniqueness constraints; duplicate detection; invalid-record quarantine; drift comparison between dataset versions; target-label validation; feature/label leakage warnings; privacy-sensitive field discovery as heuristic; lineage graph from source → transformations → splits → run → model → deployment. Users can acknowledge warnings, but dangerous errors (empty target, invalid split, malformed examples) block execution. All data-affecting actions are audit logged.

### 4.4 Preprocessing and visual pipeline builder

Implement editable DAG with typed nodes, ports, validation, versioning, deterministic execution, preview, cache invalidation, and reusable subpipelines. Core operators: missing-value strategies; duplicate handling; categorical encoders; scaling/normalization; date/time decomposition; text cleaning/tokenization/vectorization/embeddings; image resize/crop/normalize/augmentation; audio resampling/feature extraction (MFCC, spectrogram); graph feature construction; resampling/class weights; feature selection; dimensionality reduction; custom user-defined transforms through a sandboxed, explicitly enabled plugin/runtime with resource and network restrictions. Python transform execution is not permitted in the API process.

The pipeline must support train-only fit/transform semantics, leakage-safe fit scopes, persisted fitted state, deterministic cache keys, schema propagation, dry-run validation, sampled previews and reproducible execution. Every node reports input/output dimensions, null/invalid changes, resource estimate when benchmarked, and errors. Transform order and parameters are visible and serializable. Augmentation is training-only unless explicitly specified.

### 4.5 Splitting and loaders

Random, stratified, group, time-based, spatial, and user-defined manifest splits; train/validation/test and K-fold cross-validation; split preview and persisted row/entity IDs or stable hash rules. Prevent entity leakage in group split and future leakage in time split; show boundary dates and class distributions. Explicitly handle rare labels and impossible folds. Dataloader settings include batch size, workers, prefetch, pinned memory, streaming/shuffle buffers, distributed sampler, bucketing, and class weights. Recommend values only using hardware/dataset observations with stated assumptions. Multi-GPU and streaming loaders must be genuinely supported by selected backend.

## 5. Model Builder and architecture library

### 5.1 Architecture catalog

Implement the task/model families in the original specification and make capability availability truthful: MLP/TabNet/TabTransformer; CNN/ResNet/EfficientNet/ConvNeXt/ViT/Swin/UNet/DeepLab/object detection families; text CNN/RNN/LSTM/GRU/BiLSTM/transformer/encoder-decoder/causal language models and supported Hugging Face models; audio CNN/CRNN/Conformer/Whisper-compatible models and speech synthesis where dependencies permit; GCN/GAT/GraphSAGE/GIN/knowledge embeddings; time-series LSTM/TCN/N-BEATS/transformers; recommender two-tower/Wide&Deep/NCF/sequential; VAE/GAN/diffusion/flow/autoregressive models; anomaly detection; contrastive/Siamese/multitask/mixture-of-experts; RL DQN/PPO/A3C/SAC; multimodal CLIP-style models; AutoML/NAS adapters. Each catalog entry specifies task compatibility, framework, dependency/license, input contract, output contract, pretrained availability, hardware needs, implementation maturity, and export compatibility.

Architecture entries must be real implementations backed by supported open-source libraries or first-party code, version-pinned and license-reviewed. A catalog item is not “implemented” merely because a library exists: provide NeuralForge config mapping, validation, training/evaluation lifecycle integration, checkpoint/artifact handling, diagnostics, and at least one integration test. For an architecture or task combination that cannot meet that standard, do not expose it as supported; document the exact limitation. The user’s complete listed catalog is the intended supported product surface, delivered in release slices, not a reason to show fake options.

### 5.2 Visual architecture designer

Node-based editable graph for supported modules with type/shape inference, connection validation, branch/merge/residual support, nested modules, search/zoom/minimap, undo/redo, keyboard accessibility, and deterministic graph-to-code serialization. Node parameters have schemas and contextual documentation. Display tensor shapes at each edge, parameter counts, trainable/frozen counts, estimated FLOPs and memory only when computed using the selected runtime and clearly labeled as estimates. Graph saves are versioned and round-trip to generated code/config. Custom Python layers run in a sandbox with no ambient credentials/network, resource limits, dependency allowlist, and explicit security warning.

### 5.3 Recommendation engine

Recommendations are reproducible ranked candidates based on task, modality, sample/feature dimensions, class imbalance, sequence/image dimensions, latency/size/compute budget, available accelerator, supported licenses, and optional prior runs. Show features used, constraints, evidence/source, confidence/uncertainty, and explain that expected performance is not guaranteed. Accuracy/time estimates are derived from a measured benchmark with comparable hardware/data, or omitted. Never generate unsupported specific accuracy claims. User can override every recommendation.

### 5.4 Pretrained models

Real integrations with Hugging Face Hub, TorchVision, timm, and framework-specific supported registries. Pin model revision and license; display model card/source, file size, task, input processing, and security scan status if scanner exists. Support cache, authentication, offline mode, partial loading with explicit unmatched/missing tensors, frozen layers, and provenance. Do not download without user action and storage/network confirmation. Safe loading formats only; reject untrusted pickle checkpoints by default. Custom local weights require explicit trusted-file confirmation and supported format validation.

## 6. Training Engine and experiment tracking

### 6.1 Training features

Real implementations for optimizer families (SGD/momentum, Adam, AdamW, RMSprop, Adagrad, LBFGS where compatible); schedulers (step, cosine, plateau, cyclic, warmup schedules); task-appropriate losses; weight decay/L1; dropout/norm; label smoothing; mixup/cutmix where applicable; early stopping; gradient clipping/accumulation; mixed precision; gradient checkpointing; transfer learning; curriculum; self-supervised pretraining; knowledge distillation; class weighting/resampling; and custom validated callback interface. Each option includes applicability checks, config schema, and tests. Unsupported combinations fail validation before queueing.

### 6.2 Execution resources

Detect CPU, CUDA, ROCm, Apple MPS where available; report actual driver/runtime and usable memory. Support multi-GPU local, DDP, FSDP and DeepSpeed where environment-compatible; CPU fallback requires explicit confirmation when a requested accelerator is unavailable. Cloud resources: provision AWS/GCP/Azure instances and spot/preemptible options via real provider APIs; show price source/time/currency and estimate breakdown; require user confirmation of cost limits and permissions; enforce budgets, quotas, idle shutdown, interruption recovery, and deletion. Auto-scaling must be bounded by policy; no resource is created without approval. Display live GPU/VRAM/CPU/RAM/disk/network utilization from actual telemetry.

### 6.3 Run controls and live dashboard

Durable jobs, queue priorities, concurrency quotas, resource reservation, pause/resume at checkpoint-safe points, cancel, retry-from-checkpoint, clone/fork, and stop-on-budget. Dashboard streams epoch/step losses, all configured metrics, learning rate, throughput, ETA with method/confidence, device utilization, samples and predictions when privacy/settings permit, logs, diagnostics, and checkpoint status. Event stream has sequence IDs, reconnection, replay window, backpressure, and polling fallback. A progress indicator advances only from worker events. Errors show concise explanation and trace ID; authorized users can retrieve detailed logs.

### 6.4 Tracking and comparison

Built-in experiment store is authoritative. Integrations with W&B, MLflow, TensorBoard, and user-configured tracking endpoints are opt-in and tested. Log complete run config and metrics, artifact references, tags, notes, charts, and environment. Compare runs with aligned axes/metrics, missing-data explanation, config diff, statistical repetitions, and filters. Search and filter by task/model/user/time/metric/tag. HPO with Optuna (random/grid/Bayesian/TPE, Hyperband/ASHA where supported) and population-based training: real trial scheduling, prunable trials, resource budgets, resumability, study persistence, and best-trial artifact. Never label a single stochastic run as statistically conclusive.

## 7. Debug Hub

### 7.1 Diagnostics

Rule engine consumes recorded training state and data profile; every finding includes severity, evidence/threshold, scope, explanation, confidence/limitations, recommendation, applicability, and safe config diff. Implement detection for vanishing/exploding gradients, over/underfit, data/feature leakage signals, class imbalance, dead activations, label noise candidates, mode collapse, catastrophic forgetting, learning-rate instability/stagnation, inadequate/excessive capacity, data pipeline corruption, metric misuse, and resource bottlenecks. These are signals, not certain causal conclusions. Findings link to the exact run/step/data slice. Any fix requires user review and creates a new config/run; no mutation of historical run.

### 7.2 Interactive tools

Gradient norms/histograms, activation statistics/maps, loss landscape using documented perturbation method, attention visualization when architecture provides it, error slicing/clustering, feature attribution (SHAP, LIME, Integrated Gradients, Grad-CAM, Captum as applicable), calibration diagnostics, and prediction inspection. Sampling and compute limits are visible; outputs are cached against data/model/version. Explanations must distinguish attribution from causation. Test explanation shape, determinism where expected, and failure behavior.

### 7.3 Hyperparameter optimization and model comparison

Integrated study management with objective/direction, parameter distributions/conditional spaces, sampler/pruner, trial limits, compute/time budget, constraints, parallelism and resumability. Comparison shows full provenance, uncertainty where repeated seeds exist, and selected metric definitions. No default silently optimizes on test data; optimization target is validation metric only.

### 7.4 Context-aware assistant

Provide an optional AI assistant with provider abstraction and explicit user-configured provider/model/key. Off by default. Before sending project context, show exactly what project metadata, code, data samples, metrics, or logs will be transmitted; allow per-request redaction and no-data mode. Do not send raw datasets by default. Assistant responses cite local project evidence and distinguish observations from suggestions. Generated code is untrusted and never executed automatically. One-click suggestions produce a proposed diff requiring confirmation. Include rate limits, retention setting, auditability, provider failure handling, privacy policy, and prompt-injection defenses for imported docs/data. Non-LLM deterministic diagnostics remain available without the assistant.

## 8. Evaluation Engine

Implement task-specific metrics and correct aggregation: classification (accuracy, precision, recall, F-beta, F1, ROC-AUC, PR-AUC, log loss, MCC, Cohen’s kappa, per-class and macro/micro/weighted); regression (MSE/RMSE/MAE/R²/MAPE/RMSLE/explained variance/max/quantile loss); generation/NLP (BLEU, ROUGE, METEOR, perplexity, BERTScore, WER/CER, CIDEr/SPICE as task-appropriate); vision (PSNR, SSIM, FID, IS, LPIPS, mAP, IoU, Dice); audio (MOS only with valid protocol, PESQ/STOI/WER/CER); RL (return, win rate, constraint violations); anomaly (precision/recall@k, PR-AUC). Record metric version, implementation, aggregation, undefined-case handling, and inputs.

Visualizations: confusion matrix, ROC/PR and calibration curves, learning curves, residual/predicted-vs-actual/error plots, embedding projection, per-class charts, generated sample galleries, slice-based evaluation, fairness/bias analysis with defined protected attributes and metrics, robustness/adversarial evaluation in a declared threat model, statistical significance tests (including assumptions), confidence intervals, and OOD detection. Each chart has accessible tabular data and export.

Error explorer supports actual/predicted class, error kind, confidence, data slice/time/source/features, text/image/audio preview with permissions, attribution, nearest similar examples where supported, pagination, and export. Test partition stays sealed from tuning by default; any user override is explicitly warned and audited.

Production readiness report evaluates configurable task thresholds, calibration, per-class constraints, fairness criteria, latency/throughput on target hardware, artifact size, robustness checks, data provenance, license/privacy checks, and deployment policy. Each line is `pass`, `warning`, `fail`, or `not assessed`, backed by measured evidence and method. No universal “production-ready” guarantee.

## 9. Deployment Engine

### 9.1 Export formats

Real tested export adapters: ONNX, TorchScript where supported, TensorFlow SavedModel, TFLite, CoreML, TensorRT, OpenVINO, WebGPU-compatible browser runtime, C/C++ packaging, Python package, Docker image, Hugging Face model card/bundle. Each adapter checks operator support, dynamic shapes, preprocessing inclusion, precision, parity, and license. Export runs on a worker, produces artifact manifest/checksums, records conversion versions/warnings, runs numerical parity tests on representative samples with user-selected tolerances, and fails clearly on unsupported operators. Never claim successful export if parity/validation failed.

### 9.2 Optimization

Real dynamic/static INT8, FP16, structured/unstructured pruning, distillation workflow, operator fusion, compilation and target-specific optimization. Each optimization records calibration data source, method, resulting accuracy/latency/size and comparison against original. Benchmark on actual selected hardware with warmup/repeats and confidence summary. Quantization calibration data must be authorized, representative, and leakage-safe.

### 9.3 Serving targets

Generate and test REST (FastAPI), gRPC, WebSocket/streaming, batch, edge devices, browser, iOS/Android, serverless and Kubernetes manifests where supported. Every serving bundle includes schema validation, authentication configuration, request size/rate limits, batching, health/readiness, model/version identity, structured logs, observability hooks, graceful shutdown, and reproducible container build. Inference preprocessing must match training exactly. Provide staging deployment, smoke test, approval gate, rollout/rollback, blue-green/canary options, secret configuration, and cleanup. Public deployment requires explicit endpoint/network/security confirmation.

### 9.4 Monitoring and drift

Post-deployment telemetry with configurable privacy-preserving feature/prediction capture; input schema violations, data/prediction drift (PSI/KL/KS or appropriate modality measure), delayed-label performance, latency/throughput/errors/resource use, fairness slices, alert thresholds, notification integrations, incident timeline, and model version. Monitoring retention and sampling are user-controlled. Auto-retrain is disabled by default; when enabled, requires trigger policy, data approval, validation gates, human approval option, budget limits, and rollback. Never retrain or deploy a replacement without configured authorization.

## 10. Orchestration, version control, and collaboration

### 10.1 Project workspace and versioning

Project file/API view includes config, data references, pipelines, model code/config, runs, checkpoints, evaluations, exports, deploy manifests, docs, and generated README. Git integration uses user-provided repository credentials through secret manager, branch/commit preview, conflict handling, and opt-in config commits; never commit raw data/secrets by default. Dataset/model versioning tracks immutable content hashes and external source revisions; optional DVC-compatible remote. Seed/determinism settings captured. Checkpoints atomically stored and retention policy configurable. Time-travel compares project versions; fork/branch clones config references without duplicating large immutable artifacts unless requested.

### 10.2 Collaboration

Multi-user projects; RBAC; shared run/evaluation dashboards; comments on project/data/run/metric/artifact with threaded resolution; mentions and notifications; team experiment comparisons; recipe/template publication and fork with license/provenance; presentation mode; autogenerated documentation and architecture diagrams; CI/CD API and webhooks. Conflict-safe editing with optimistic concurrency/version checks; clear merge/reload behavior. Audit logs capture actor, action, object, timestamp, request ID, and before/after diff where appropriate. Admin retention/export/deletion controls.

## 11. Plugin SDK and marketplace

Versioned SDK interfaces for DataConnector, ModelArchitecture, CustomMetric, DebugRule, DeploymentTarget, Visualizer, Preprocessor, Optimizer/Scheduler, and NotificationProvider. Plugins declare compatibility, dependencies, permissions, license, capabilities, schemas, entry points, and tests. Run third-party plugins isolated in a sandbox/container with least privilege, resource limits, no host credentials, network denied by default, signature/provenance verification, allowlisting, version pinning, and kill/revoke mechanism. Marketplace supports discovery, signed packages, versions, reviews/moderation, vulnerability policy, license information, install/update/uninstall/rollback, and organization allowlists. Plugin failure cannot corrupt control-plane state. Provide SDK docs, template, test harness, compatibility CI, example plugins that are real and tested. No unreviewed plugin executes automatically.

## 12. Python API, CLI, and notebooks

Ship versioned Python package `neuralforge` and CLI `nf` with consistent capabilities:

- `nf auth login/logout/status`, `nf org`, `nf project create/list/show/delete`.
- `nf data connect/import/profile/pipeline/split`.
- `nf model list/recommend/build/import/export`.
- `nf run start/list/show/logs/cancel/resume/fork`.
- `nf hpo start/show/stop`.
- `nf evaluate`, `nf report`, `nf artifact`, `nf deploy`, `nf monitor`, `nf plugin`, `nf config validate`, `nf doctor`.

Python API should provide typed project/data/model/trainer/evaluation/deployment objects and asynchronous job handles, local and remote client modes, exception hierarchy, retries/idempotency, pagination, streaming events, and version compatibility checks. Jupyter magics (`%%neuralforge train`, etc.) are optional only if implemented and documented end-to-end. The code example in the source specification is illustrative; correct invalid Python syntax and provide executable tutorials tested in CI. Package extras are explicit and versioned. No credentials embedded in notebooks/config files.

## 13. Knowledge base and documentation

In-product searchable documentation covers concepts, task recipes, data connectors, model catalog, configuration, APIs, security/privacy, troubleshooting, licensing, and deployment. Version docs against application release. Include interactive examples backed by actual supported capability, not fabricated output. Contextual help links to relevant docs. Generated README/model cards include provenance, intended use, evaluation limitations, data license, known risks, and deployment details.

## 14. Security, privacy, compliance, and safety

- OIDC SSO; optional enterprise SAML through supported identity broker; MFA policy delegated/configurable. Secure session handling, CSRF protection, OAuth state/PKCE, secure cookies, rate limits, brute-force protection, account lifecycle.
- Tenant isolation enforced in DB queries, object store paths/policies, queues, caches, logs, and artifact downloads. Authorization tests attempt cross-tenant access for every resource class.
- Secrets encrypted with KMS/Vault or local OS key store; secret values write-only; rotation and revocation; never in config, logs, telemetry, URLs, or source control.
- TLS for all network traffic; encryption at rest for metadata/artifacts where deployment supports it; key rotation and backup encryption.
- Strict upload and archive limits, MIME/content validation, malware scanning integration when configured, safe deserialization, SSRF protection, sandboxing, path traversal protection, formula injection protections, XSS escaping, SQL parameterization, command injection protections, CSRF/CORS policy, dependency/SBOM scanning.
- Data retention/deletion, export, consent, purpose/lineage, user access, privacy policy, optional PII detection/masking. Do not claim legal compliance certification without independent audit.
- Threat model covers malicious datasets, notebooks/plugins, prompt injection, compromised workers, cross-tenant leakage, supply chain, cloud credential abuse, and model artifact tampering.
- Publish security contact, vulnerability disclosure process, dependency update cadence, incident response, audit trail, backup/restore and disaster recovery procedures.

## 15. Operations, observability, and SLOs

Structured JSON logs with correlation/request/job IDs and redaction. OpenTelemetry traces across API/queue/worker/provider calls. Metrics for request latency/errors, queue depth/wait, job success/failure/cancel, worker utilization, GPU/CPU/memory/disk, upload volume, export/deploy failures, and provider throttles. Alerts and dashboards with runbooks. Configure log retention and avoid logging raw examples by default.

Define and publish SLOs before release: API availability/latency, job queue delay, job event freshness, recovery point/time, artifact durability, and support response. Defaults must be measurable and deployment-specific; do not hard-code unsupported guarantees. Resource quotas and per-tenant budgets apply to upload size, concurrency, GPU hours, storage, API rates, and cloud spend. Backpressure prevents queue overload. Provide graceful degradation and maintenance mode.

## 16. UI/accessibility/localization

Use design system with responsive layouts, consistent typography/color/tokens, accessible charts, keyboard interactions, reduced-motion respect, focus management, semantic landmarks, screen-reader labels, WCAG 2.2 AA target. No information conveyed solely by color. Forms have inline validation and summaries. Long operations include cancellation and retained navigation. Localization-ready string catalogs, locale-aware numbers/dates, timezone handling, and units; English initially complete. Support dark/light themes and high contrast. The visual model editor and charts must be usable without a mouse where technically applicable.

## 17. Testing and quality gates

### 17.1 Required test layers

- Unit: schemas, migrations, connectors, transformations, leakage controls, splits, every model/loss/metric combination, diagnostics, state machines, permission rules, security utilities, export parity, deployment manifests.
- Integration: each supported backend/task end-to-end with small fixtures; real connector integration tests in provider test accounts or containerized compatible services; queue restart/retry/cancellation; database/object-store migrations; tracking integrations; cloud provisioning and cleanup; monitoring/alert delivery; plugin sandbox; OIDC flow.
- System/E2E: create organization/project → connect/import data → profile → build pipeline → build model → train → debug → evaluate → compare → export → deploy staging → send inference → monitor/drift alert → rollback. Cover guided and expert paths and permission-denied paths.
- Performance/load: large uploads, high-cardinality data, concurrent jobs, event throughput, project/search listing, API saturation, queue fairness, artifact download, dashboard responsiveness. Set budgets by reference hardware and publish results.
- Security: SAST, dependency/SBOM, secret scanning, DAST, tenancy/IDOR, upload fuzzing, prompt injection, SSRF, plugin escape tests, authorization matrix, backup restore.
- Accessibility: automated checks plus keyboard and screen-reader critical-path review.

### 17.2 Release gates

No release with failing tests, unreviewed critical/high vulnerabilities, data-loss risk, untested migration, broken rollback, incomplete translations in critical flows, inaccessible primary path, or a listed feature lacking end-to-end acceptance. CI runs format, lint, static types, tests, build, SBOM, security scans. Integration tests requiring cloud credentials run in protected release pipelines; lack of credentials does not convert them into passing tests.

## 18. API and event contracts

Provide `/api/v1` REST APIs, OpenAPI schema, generated clients, pagination/filter/sort, idempotency keys, optimistic concurrency/ETags, standardized error envelope, versioning and deprecation policy. Use consistent `401/403/404/409/413/422/429/5xx` semantics and trace IDs. SSE or WebSocket for jobs with sequence IDs, resumable cursor, bounded replay, heartbeat, auth and tenant isolation; polling fallback. Webhooks are signed, retryable, deduplicated and have secret rotation.

Expose capability discovery endpoint describing task, framework, architecture, metric, export, provider and plugin support, prerequisites, and versions. API must not leak internal stack traces or secret references.

## 19. Source repository and deliverables

Deliver:

1. Production web application and API.
2. Worker/scheduler services and supported adapters.
3. Python package, CLI, docs, and generated API clients.
4. Local install, Docker Compose development, production Kubernetes/Helm and cloud reference configurations.
5. Database migrations, backup/restore scripts, sample policy/configs.
6. CI workflows, release/versioning process, SBOM, security and operations runbooks.
7. Full user/admin/developer/plugin documentation and tutorials.
8. Automated unit/integration/E2E/performance/accessibility/security test suites.
9. Reference projects/datasets explicitly labeled as sample or synthetic, not as evidence of model quality.
10. License inventory for source, dependencies, pretrained models, and generated artifacts.

Recommended repo layout:

```text
apps/web/ apps/api/ apps/worker/ apps/desktop/
packages/ui/ packages/config-schema/ packages/python-sdk/ packages/plugin-sdk/
services/identity-adapter/ services/model-serving/
charts/neuralforge/ deploy/terraform/aws/ deploy/terraform/gcp/ deploy/terraform/azure/
docs/ tests/e2e/ tests/performance/ tests/security/
```

Equivalent organization is acceptable if service ownership and dependency boundaries are documented.

## 20. Completion and release acceptance

A production release is complete only when:

1. Every capability enumerated in this document is implemented end-to-end or the release is explicitly labeled incomplete and not accepted as fulfilling this specification. No stubs or simulated functionality.
2. All advertised task/model/framework combinations pass compatibility tests for data, train, checkpoint, evaluate, and applicable export/deploy lifecycle.
3. Each listed connector and provider integration passes real contract/integration tests; credentials and failure modes are documented.
4. Guided and Expert modes share state and complete the same lifecycle without losing user work.
5. Jobs are durable, observable, cancellable, recoverable, quota-controlled, and correctly audited.
6. Reproducibility and data-leakage invariants pass automated tests.
7. Security controls and tenant isolation pass negative tests and independent review; backup restoration and upgrade/rollback are demonstrated.
8. All reports and recommendations derive from real recorded evidence; estimates include methodology; unavailable facts are not fabricated.
9. Exported models pass parity checks and generated serving applications pass smoke, auth, schema, and security checks.
10. Monitoring, alerting, drift calculations, rollback, and opt-in retraining gates are verified against deployed test endpoints.
11. Python API/CLI and UI are behaviorally consistent, documented, versioned, and tested.
12. All required CI quality gates pass; operational SLOs, capacity limits, incident runbooks, and support processes are published.

## 21. Delivery sequencing without scope reduction

Implement in release increments to manage engineering risk, but the final contracted product includes the entire specification. Each increment must be a usable, production-quality subset with no fake UI. Maintain a public capability matrix indicating complete/in progress/not yet released and keep unimplemented capabilities out of selectable UI/API discovery. Do not declare the project complete until every planned capability has passed its end-to-end acceptance criteria. Release slices are not permission to replace later functionality with stubs or to call the first slice the finished product.

Suggested dependency order:
1. Identity, tenancy, persistence, audit, config schemas, API contracts, job system, storage, observability.
2. Core data connectors, profiling, quality, pipeline, split/versioning.
3. Framework adapters, model catalog, visual builder, pretrained lifecycle.
4. Training, resource pools/cloud, tracking, HPO, collaboration.
5. Diagnostics, explainability, evaluation/fairness/robustness.
6. Export/optimization/serving/cloud deployment/monitoring.
7. SDK/marketplace, CLI/Python/Jupyter, assistant, desktop packaging, enterprise hardening.
8. Full end-to-end, security, performance, disaster recovery, accessibility, and provider certification.

## 22. Authoritative product boundary

The original NeuralForge specification’s breadth is intentional. The product is a complete platform, not only the initial text/tabular workflow. All original named modules are in scope: Wizard/Guided mode, Expert workspace, Data Engine, Model Builder, Train Engine, Debug Hub, Evaluation Engine, Deployment Engine, orchestration/versioning, AI assistant and knowledge base, architecture/task families, plugin SDK/marketplace, collaboration, cloud/GPU manager, Python API/CLI/notebooks, and roadmap features. This document supplies production semantics and acceptance requirements. Where a named item depends on hardware, credentials, licensing, or a provider, implement the real integration and a complete prerequisite/failure UX; do not substitute a simulation.
