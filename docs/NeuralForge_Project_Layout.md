# NeuralForge — Object-Oriented Monorepo Layout

This is the canonical proposed repository structure for the **complete production NeuralForge platform**. Every listed path is intentional. Comments state the responsibility and the object-oriented boundary expected in that file or directory. This is a layout/specification, not a claim that all application code has already been implemented.

## Object-oriented design rules

- Organize code around domain concepts and application use cases, not large utility modules or framework routes.
- Use encapsulated entities/value objects with explicit invariants; aggregates own state transitions. Do not expose mutable internal collections.
- Use application services/use cases to coordinate domain objects and ports. Keep business rules out of HTTP handlers, ORM models, UI components, and cloud SDK calls.
- Define abstract interfaces/ports at the boundary where the application needs a capability. Implement adapters for databases, queues, object stores, ML frameworks, cloud providers, trackers, identity providers, and external APIs.
- Prefer composition and dependency injection over inheritance. Use inheritance only for stable, substitutable contracts (e.g. an abstract connector or model adapter), never as a taxonomy-only convenience.
- Each concrete model/connector/provider implements a documented interface and advertises capabilities. No `if provider == ...` branching scattered through use cases.
- Separate domain entities from persistence records, API DTOs, and frontend view models; map explicitly between them.
- Use immutable value objects/config snapshots for versioned data. Side-effecting methods return explicit results/errors; no hidden global state.
- Inject clocks, ID generators, filesystem/object-store clients, random generators, and provider clients. This makes behavior testable and deterministic.
- No “God objects,” catch-all `utils.py`, or module-level service singletons. Keep classes cohesive and narrowly responsible.
- Treat plugins and user code as untrusted. An OO interface is not a security boundary; execution isolation belongs in sandbox infrastructure.

## Repository root

```text
neuralforge/                                      # Repository root; contains all product code, deployment assets, docs, and tests.
├── README.md                                     # Product summary, supported deployment modes, links to setup/development/security docs.
├── LICENSE                                       # Project license; must match approved licensing decision.
├── NOTICE                                        # Third-party notices and bundled asset/model notices.
├── CONTRIBUTING.md                               # Contribution workflow, OO/domain boundaries, testing and code review rules.
├── CODE_OF_CONDUCT.md                            # Community conduct policy.
├── SECURITY.md                                   # Vulnerability reporting, supported versions, security response policy.
├── CHANGELOG.md                                  # User-visible changes grouped by release/version.
├── VERSION                                       # Single source of truth or generated release version.
├── Makefile                                      # Thin developer command aliases; commands delegate to package scripts.
├── .editorconfig                                 # Shared whitespace and text encoding rules.
├── .gitignore                                    # Excludes secrets, local data, generated output, caches, and build products.
├── .dockerignore                                 # Keeps credentials, local datasets, tests, and irrelevant files out of images.
├── .env.example                                  # Names and safe example values only; never real credentials.
├── pyproject.toml                                # Python workspace/tool configuration and package metadata.
├── package.json                                  # JavaScript workspace scripts and package-manager configuration.
├── pnpm-workspace.yaml                           # Frontend/package workspace membership.
├── uv.lock                                       # Locked Python dependency graph; generated and reviewed.
├── pnpm-lock.yaml                                # Locked JavaScript dependency graph; generated and reviewed.
├── compose.yaml                                  # Local development topology; non-production defaults and no embedded secrets.
├── compose.test.yaml                             # Isolated test dependencies and test-only services.
├── Taskfile.yml                                  # Optional structured task runner; no business logic.
├── apps/                                         # Runnable deployable applications, each with an explicit entry point.
├── packages/                                     # Reusable libraries/contracts with no app-specific global state.
├── services/                                     # Independent runtime services where isolation/scaling is needed.
├── plugins/                                      # First-party example plugins and plugin development fixtures.
├── deploy/                                       # Production deployment definitions and infrastructure-as-code.
├── docs/                                         # Versioned user, admin, developer, API, and operations documentation.
├── tests/                                        # Cross-app integration, end-to-end, performance, security, and accessibility tests.
├── scripts/                                      # Safe, idempotent developer/release/maintenance commands.
├── .github/                                      # CI, release, dependency automation, issue templates, and PR templates.
└── artifacts/                                    # Empty tracked directory or documentation only; runtime artifacts are never committed.
```

## `apps/web` — Browser application

```text
apps/web/                                         # React/TypeScript SPA; presentation layer only, no business rules or direct DB access.
├── package.json                                  # Web app dependencies and app-specific scripts.
├── vite.config.ts                                # Build/dev config; host/origin policy appropriate to deployment.
├── tsconfig.json                                 # Strict TS settings; path aliases and compile constraints.
├── index.html                                    # Minimal app mount document and metadata.
├── public/                                       # Static first-party assets; no user data or secrets.
├── src/
│   ├── main.tsx                                  # Composition root: creates app providers and mounts root component.
│   ├── app/
│   │   ├── NeuralForgeApp.tsx                    # Root application shell component composed from layout and route objects.
│   │   ├── AppRouter.tsx                         # Route declarations and route guards; delegates authorization to API.
│   │   ├── AppProviders.tsx                      # UI-level dependency providers: query cache, i18n, theme, notifications.
│   │   ├── routeRegistry.ts                      # Typed route metadata and navigation definitions.
│   │   ├── permissions/                          # UI affordance policies mirroring (not replacing) backend permissions.
│   │   │   ├── PermissionViewPolicy.ts            # Interface for evaluating whether UI actions should be offered.
│   │   │   └── ApiBackedPermissionViewPolicy.ts   # Adapter using current identity/capability data; server remains authoritative.
│   │   └── errorHandling/                        # Error presentation and trace-ID workflows.
│   │       ├── UiError.ts                         # UI-safe error value object, excluding stack traces/secrets.
│   │       └── ErrorPresenter.ts                  # Maps API/domain error codes to accessible messages and recovery actions.
│   ├── routes/
│   │   ├── SignInRoute.tsx                        # OIDC sign-in start, callback completion, and safe failure display.
│   │   ├── OrganizationRoute.tsx                  # Organization/workspace selection and creation views.
│   │   ├── ProjectRoute.tsx                       # Project shell with child navigation and project context.
│   │   ├── ProjectOverviewRoute.tsx               # Derived project readiness, recent jobs, and real persisted activity.
│   │   ├── GuidedJourneyRoute.tsx                 # Wizard composition over the same project use cases as Expert mode.
│   │   ├── DataRoute.tsx                          # Dataset list, source connectors, profiles, and lineage entry points.
│   │   ├── PipelineRoute.tsx                      # Visual pipeline editor and validated preview orchestration.
│   │   ├── ModelRoute.tsx                         # Model catalog, recommendation, graph builder, and model versions.
│   │   ├── TrainingRoute.tsx                      # Training configuration and run submission.
│   │   ├── RunDetailRoute.tsx                     # Durable run status, event stream, logs, metrics, and controls.
│   │   ├── DebugRoute.tsx                         # Evidence-backed diagnoses and interactive debugging tools.
│   │   ├── EvaluationRoute.tsx                    # Metric selection, test evaluation, visualizations, and error explorer.
│   │   ├── DeploymentRoute.tsx                    # Export, optimize, stage, deploy, rollout, and rollback workflows.
│   │   ├── MonitoringRoute.tsx                    # Endpoint health, drift, alerts, incidents, and policy-controlled retraining.
│   │   ├── ExperimentsRoute.tsx                   # Search, compare, filter, and inspect immutable experiment runs.
│   │   ├── ArtifactsRoute.tsx                     # Authorized artifact browser/download and provenance.
│   │   ├── TeamRoute.tsx                          # Membership, roles, comments, notifications, and audit views.
│   │   └── SettingsRoute.tsx                      # Project/organization policy, integrations, quotas, and retention settings.
│   ├── features/                                  # Feature modules; each feature owns its UI models, use-case client, and components.
│   │   ├── guided/
│   │   │   ├── GuidedJourney.tsx                  # Wizard state renderer; state comes from persisted project readiness.
│   │   │   ├── JourneyStep.ts                     # UI step value object and prerequisite metadata.
│   │   │   ├── JourneyProgressPresenter.ts         # Derives visible progress from API-returned prerequisites.
│   │   │   └── steps/                             # One component per lifecycle phase; no independent state engine.
│   │   ├── data/
│   │   │   ├── DatasetCollection.tsx              # Dataset rows, actions, pagination, and empty/error states.
│   │   │   ├── ConnectorCatalog.tsx               # Capability-driven connector choices and setup requirements.
│   │   │   ├── ConnectorWizard.tsx                # Typed connector configuration forms; secrets use write-only fields.
│   │   │   ├── UploadDatasetForm.tsx              # Upload flow with constraints, progress, cancellation, and errors.
│   │   │   ├── DatasetProfileView.tsx              # Computed schema, statistics, caveats, and sample preview.
│   │   │   ├── DataQualityIssueList.tsx            # Quality findings with evidence and remediation links.
│   │   │   ├── DataLineageGraph.tsx                # Accessible lineage visualization plus tabular equivalent.
│   │   │   ├── PipelineCanvas.tsx                  # Node editor view; editing commands go through PipelineEditorModel.
│   │   │   ├── PipelineEditorModel.ts              # UI interaction model with undo/redo; server validates saved graph.
│   │   │   ├── PipelineNodeView.tsx                # Generic schema-driven node editor, not operator-specific business logic.
│   │   │   ├── PipelinePreviewPanel.tsx            # Real bounded preview results and transformation diagnostics.
│   │   │   └── SplitPreview.tsx                    # Split counts, boundaries, stratification, and leakage warnings.
│   │   ├── model/
│   │   │   ├── ArchitectureCatalog.tsx             # Capability API-driven catalog with framework/license requirements.
│   │   │   ├── RecommendationPanel.tsx              # Evidence, constraints, uncertainty, and override controls.
│   │   │   ├── ArchitectureGraphEditor.tsx         # Visual architecture graph editor and keyboard interactions.
│   │   │   ├── LayerInspector.tsx                   # Schema-driven layer properties and validation errors.
│   │   │   ├── TensorShapeOverlay.tsx               # Server/runtime-derived shape annotations.
│   │   │   ├── ModelSummaryPanel.tsx                # Computed parameters, memory/FLOPs where available, caveats.
│   │   │   ├── PretrainedModelPicker.tsx            # Real registry search, source/license/revision, and download consent.
│   │   │   └── ModelVersionHistory.tsx              # Immutable model versions, diffs, and provenance.
│   │   ├── training/
│   │   │   ├── TrainingConfigForm.tsx               # Server-schema-driven configuration and compatibility validation.
│   │   │   ├── ResourceSelector.tsx                 # Actual detected/local/cloud resource choices and cost guardrails.
│   │   │   ├── RunSubmissionPanel.tsx                # Effective config review, budget approval, and idempotent submission.
│   │   │   ├── RunDashboard.tsx                      # Live actual metrics/resources; no fabricated progress.
│   │   │   ├── MetricChart.tsx                      # Accessible chart component with table/download alternative.
│   │   │   ├── RunLogViewer.tsx                      # Bounded, permission-checked logs with secret-safe rendering.
│   │   │   ├── SamplePredictionViewer.tsx             # Optional consent-controlled examples from real run batches.
│   │   │   ├── RunControlBar.tsx                     # Pause/resume/cancel/retry only when server capability allows.
│   │   │   └── JobEventSubscription.ts                # Reconnectable event client with cursor and polling fallback.
│   │   ├── debug/
│   │   │   ├── DiagnosisList.tsx                     # Evidence-backed issue cards and explicit proposed changes.
│   │   │   ├── DiagnosisDetail.tsx                   # Rule/version/evidence/limitations and data/run links.
│   │   │   ├── ProposedFixReview.tsx                 # Config diff approval; starts a new immutable run/config.
│   │   │   ├── GradientAnalysisView.tsx              # Backend-computed gradient metrics and bounded visualizations.
│   │   │   ├── ActivationAnalysisView.tsx             # Model-supported activations and sample provenance.
│   │   │   ├── AttributionView.tsx                    # Method/model compatibility and attribution limitations.
│   │   │   ├── LossLandscapeView.tsx                  # Real computation settings, cost, and resulting surface.
│   │   │   ├── ErrorSliceExplorer.tsx                 # Slice filters, aggregation, pagination, and privacy controls.
│   │   │   └── HyperparameterStudyView.tsx            # Study config, trial states, budget, and best-trial provenance.
│   │   ├── evaluation/
│   │   │   ├── EvaluationConfigForm.tsx               # Valid metric selection for task/model/output capability.
│   │   │   ├── MetricReport.tsx                       # Metric definitions, values, aggregation, and undefined handling.
│   │   │   ├── ConfusionMatrix.tsx                    # Accessible confusion matrix with per-cell counts and labels.
│   │   │   ├── CurveChart.tsx                         # ROC/PR/calibration curves when mathematically valid.
│   │   │   ├── ResidualAnalysis.tsx                    # Regression residual and prediction analysis.
│   │   │   ├── FairnessAnalysis.tsx                    # Protected-attribute selection, metric definitions, caveats.
│   │   │   ├── RobustnessEvaluation.tsx                # Declared threat model and actual evaluation jobs.
│   │   │   ├── ErrorExplorer.tsx                       # Paginated real errors and safe sample rendering.
│   │   │   └── ReadinessReport.tsx                     # Evidence-backed pass/warn/fail/not-assessed checklist.
│   │   ├── deployment/
│   │   │   ├── ExportWizard.tsx                        # Capability-driven format selection, validation, and export job.
│   │   │   ├── OptimizationWizard.tsx                  # Calibration/source approval and before/after benchmark workflow.
│   │   │   ├── ServingTargetPicker.tsx                 # Real target capabilities/prerequisites and provider connection.
│   │   │   ├── DeploymentPlanReview.tsx                # Generated plan, security/cost diff, approval and rollback plan.
│   │   │   ├── DeploymentStatusView.tsx                # Provider-observed states, events, and operational actions.
│   │   │   ├── EndpointSmokeTest.tsx                   # Real authenticated inference smoke tests and response display.
│   │   │   └── RolloutControl.tsx                      # Canary/blue-green/rollback controls where provider supports them.
│   │   ├── monitoring/
│   │   │   ├── MonitorDashboard.tsx                    # Actual endpoint, drift, latency, performance, and resource data.
│   │   │   ├── DriftComparison.tsx                     # Baseline/window selection, methods, and sample counts.
│   │   │   ├── AlertPolicyEditor.tsx                   # Validated thresholds, delivery channels, escalation rules.
│   │   │   ├── IncidentTimeline.tsx                    # Immutable alert, acknowledgement, action, and resolution events.
│   │   │   └── RetrainingPolicyEditor.tsx               # Explicit approval, budget, validation, and rollback gates.
│   │   ├── experiments/
│   │   │   ├── ExperimentTable.tsx                     # Server-paginated searchable runs and saved views.
│   │   │   ├── RunComparison.tsx                       # Aligned metrics, config diffs, uncertainty and missing-data caveats.
│   │   │   ├── ExperimentCharts.tsx                    # Multi-run charts using selected metric definitions.
│   │   │   └── ExperimentTagsEditor.tsx                 # Version-safe tags, notes, and ownership metadata.
│   │   ├── collaboration/
│   │   │   ├── MemberManager.tsx                       # Role-aware member invite/remove and access review.
│   │   │   ├── CommentThread.tsx                       # Threaded comments, mentions, resolution and audit-safe edits.
│   │   │   ├── NotificationInbox.tsx                    # User-scoped event notifications and read state.
│   │   │   ├── RecipeBrowser.tsx                       # Licensed recipes with provenance and fork preview.
│   │   │   └── PresentationMode.tsx                    # Shareable permission-aware report presentation.
│   │   └── assistant/
│   │       ├── AssistantPanel.tsx                      # Optional provider-backed assistant; disabled absent setup/consent.
│   │       ├── ContextDisclosure.tsx                    # Exact data/context transmission preview and redaction controls.
│   │       ├── AssistantConversation.ts                 # UI conversation state; server owns provider calls and retention.
│   │       └── SuggestedChangeReview.tsx                # Untrusted generated suggestions as explicit diffs only.
│   ├── components/                                     # Generic reusable visual components, not domain workflow owners.
│   │   ├── layout/                                     # AppHeader, SideNavigation, ProjectHeader, ResponsiveShell.
│   │   ├── forms/                                      # Typed field wrappers, validation summary, secret input.
│   │   ├── charts/                                     # Chart primitives with accessible table equivalents.
│   │   ├── status/                                     # StatusBadge and progress components driven by domain states.
│   │   ├── dialogs/                                    # Confirmation, destructive action, and approval dialogs.
│   │   ├── data-display/                               # Tables, pagination, filters, empty/loading/error states.
│   │   └── accessibility/                             # Focus management, live regions, keyboard helpers.
│   ├── client/                                         # Typed API client and transport adapters.
│   │   ├── NeuralForgeApiClient.ts                     # Public typed client facade; no business logic.
│   │   ├── HttpTransport.ts                            # Authenticated HTTP, retries/idempotency and trace propagation.
│   │   ├── SseJobEventTransport.ts                     # SSE cursor/reconnect implementation.
│   │   ├── ApiErrorMapper.ts                            # Maps server error envelopes into typed client errors.
│   │   └── generated/                                  # Generated OpenAPI client/types; never hand-edited.
│   ├── viewModels/                                     # UI-specific immutable projections, distinct from API/domain entities.
│   ├── state/                                          # Query/cache and transient UI state; server remains source of truth.
│   ├── i18n/                                           # Translation catalogs, locale formatters, timezone utilities.
│   ├── theme/                                          # Design tokens, theme objects, contrast rules.
│   ├── styles/                                         # Global reset and layout-level styles.
│   └── test/                                           # Frontend test setup and accessibility helpers.
├── e2e/                                               # Web app-specific browser acceptance tests.
└── Dockerfile                                         # Non-root, minimal production web image.
```

## `apps/api` — Control-plane API

```text
apps/api/                                              # HTTP and WebSocket/SSE adapters; contains no domain business rules.
├── pyproject.toml                                     # API-specific dependencies/config.
├── Dockerfile                                         # Hardened non-root API image.
├── src/neuralforge_api/
│   ├── __main__.py                                    # CLI entry point for API process only.
│   ├── composition/                                   # Dependency injection and runtime assembly.
│   │   ├── ApiCompositionRoot.py                      # Wires ports to configured adapters and use cases.
│   │   ├── Settings.py                                # Typed validated settings; secret references only.
│   │   └── Container.py                               # Scoped dependency container with explicit lifetimes.
│   ├── http/
│   │   ├── ApiApplication.py                          # ASGI app construction, middleware, routes, lifecycle.
│   │   ├── middleware/                                # Request ID, auth context, tenant context, rate-limit, security headers.
│   │   ├── dependencies/                              # Request-scoped authenticated actor and use-case providers.
│   │   ├── exception_handlers/                        # Stable error-envelope translation and trace-safe responses.
│   │   ├── v1/
│   │   │   ├── ApiV1Router.py                         # Versioned route composition.
│   │   │   ├── auth/                                  # OIDC start/callback/session/revocation endpoints.
│   │   │   ├── organizations/                         # Organization and membership endpoints/DTOs.
│   │   │   ├── projects/                              # Project CRUD, configuration, versions, settings endpoints.
│   │   │   ├── datasets/                              # Upload, connector, profile, quality, lineage endpoints.
│   │   │   ├── pipelines/                             # Pipeline version, validation, preview and execution endpoints.
│   │   │   ├── models/                                # Catalog, recommendations, graph validation, pretrained endpoints.
│   │   │   ├── runs/                                  # Run submission, state, controls, logs and event endpoints.
│   │   │   ├── studies/                               # HPO study and trial endpoints.
│   │   │   ├── evaluations/                           # Evaluation creation, metrics, slices and report endpoints.
│   │   │   ├── artifacts/                             # Authorized metadata and short-lived download access.
│   │   │   ├── deployments/                           # Export/deploy/rollout/rollback endpoints.
│   │   │   ├── monitoring/                            # Monitor/alert/incident/retraining policy endpoints.
│   │   │   ├── collaboration/                         # Comments, mentions, recipes, membership, presentation endpoints.
│   │   │   ├── plugins/                               # Registry, install, policy, and lifecycle endpoints.
│   │   │   ├── assistant/                             # Consent-aware provider-backed assistant endpoint.
│   │   │   ├── audit/                                 # Permission-scoped audit query endpoints.
│   │   │   ├── capabilities/                          # Dynamic support matrix and prerequisite discovery.
│   │   │   └── health/                                # Liveness, readiness, version, dependency health endpoints.
│   │   ├── schemas/                                   # HTTP request/response DTOs; no ORM/domain entity leakage.
│   │   ├── mappers/                                   # Explicit DTO ↔ application command/result mappings.
│   │   ├── openapi/                                   # API description customization and examples.
│   │   └── streaming/                                 # SSE/WebSocket auth, cursor, heartbeat, backpressure adapters.
│   ├── security/
│   │   ├── OidcAuthenticationAdapter.py                # Validates OIDC tokens and maps identity claims.
│   │   ├── AuthorizationContextFactory.py              # Builds actor/tenant/permission context from trusted identity.
│   │   ├── CsrfProtection.py                           # CSRF checks for cookie-authenticated unsafe operations.
│   │   ├── RateLimitPolicy.py                          # Route/tenant/actor limits backed by shared store.
│   │   └── SecurityHeadersPolicy.py                    # CSP, HSTS, frame and content-type policies.
│   └── observability/
│       ├── RequestTelemetry.py                         # Request metrics and traces with redaction.
│       └── HealthCheckRegistry.py                      # Readiness probes for configured dependencies.
└── tests/                                              # API route, auth, authorization, schema and contract tests.
```

## `packages/domain` — Pure domain model

```text
packages/domain/                                        # Framework-free business entities and invariants.
├── pyproject.toml
└── src/neuralforge_domain/
    ├── common/
    │   ├── Entity.py                                   # Base identity/equality behavior for entities; no persistence coupling.
    │   ├── AggregateRoot.py                            # Domain event collection and aggregate boundary behavior.
    │   ├── ValueObject.py                              # Immutable equality-by-value contract.
    │   ├── DomainEvent.py                              # Typed event base with event ID/time/tenant metadata.
    │   ├── DomainError.py                              # Stable domain error base and error codes.
    │   ├── Identifier.py                               # Typed UUID/ULID value objects for aggregate IDs.
    │   ├── TimeRange.py                                # Validated UTC interval value object.
    │   ├── ResourceBudget.py                           # Validated compute/time/storage/cost limit value object.
    │   └── Page.py                                     # Pagination value object and bounded page invariants.
    ├── identity/
    │   ├── User.py                                     # User identity/profile entity; excludes credentials/secrets.
    │   ├── Organization.py                             # Tenant aggregate and policy ownership.
    │   ├── Membership.py                               # User-to-organization/project role assignment entity.
    │   ├── Role.py                                     # Role value object and permission mapping reference.
    │   └── ActorContext.py                             # Immutable actor, tenant, scopes and request correlation context.
    ├── projects/
    │   ├── Project.py                                  # Project aggregate; owns lifecycle/config version references.
    │   ├── ProjectName.py                              # Validated normalized/display project name value object.
    │   ├── ProjectDescription.py                       # Bounded optional description value object.
    │   ├── ProjectReadiness.py                         # Derived readiness prerequisites, never UI-maintained truth.
    │   ├── ProjectSettings.py                          # Versioned project policies and retention/quota references.
    │   └── ProjectVersion.py                           # Immutable project snapshot reference/value object.
    ├── data/
    │   ├── Dataset.py                                  # Dataset aggregate and immutable version lifecycle.
    │   ├── DatasetVersion.py                           # Source checksum, schema, profile and source revision snapshot.
    │   ├── DataSource.py                               # Discriminated source reference; credentials are secret IDs only.
    │   ├── DataSchema.py                               # Typed columns/fields and compatibility invariants.
    │   ├── ColumnDefinition.py                         # Column identity/display name/type/semantic annotations.
    │   ├── DatasetProfile.py                           # Immutable computed statistics with method/sample provenance.
    │   ├── DataQualityFinding.py                       # Evidence-backed quality issue and severity.
    │   ├── DataLineage.py                              # Typed source-to-artifact lineage edges and provenance.
    │   ├── DataSnapshot.py                             # Point-in-time dataset snapshot and content identity.
    │   ├── ConnectorConfiguration.py                   # Validated connector settings containing secret references only.
    │   ├── DataSplitManifest.py                        # Stable train/validation/test or fold membership definition.
    │   └── SensitiveFieldAnnotation.py                 # User-confirmed sensitivity/masking policy value object.
    ├── pipelines/
    │   ├── Pipeline.py                                 # Pipeline aggregate with immutable versions and graph invariants.
    │   ├── PipelineVersion.py                          # Immutable node graph plus schema version.
    │   ├── PipelineNode.py                             # Typed node identity, operator type, parameter snapshot, ports.
    │   ├── PipelineEdge.py                             # Validated typed connection between node ports.
    │   ├── PipelineGraph.py                            # Acyclic/allowed-cycle graph validation and traversal.
    │   ├── FittedTransformState.py                     # Train-fitted transform state reference/checksum.
    │   ├── PipelinePreview.py                          # Bounded preview result with sample method and warnings.
    │   └── PipelineValidationResult.py                 # Structured errors/warnings and schema compatibility.
    ├── models/
    │   ├── ModelDefinition.py                          # Architecture aggregate and immutable model versions.
    │   ├── ModelVersion.py                             # Graph/config/code digest/framework/library provenance.
    │   ├── ArchitectureDescriptor.py                   # Catalog entry: task, modality, capabilities, requirements/license.
    │   ├── ArchitectureGraph.py                        # Typed model node graph and topology invariants.
    │   ├── LayerDefinition.py                          # Layer config value object and typed shape contract.
    │   ├── TensorShape.py                              # Dimension/unknown/batch shape value object and compatibility rules.
    │   ├── ModelCapability.py                          # Framework/task/export/training feature capability value object.
    │   ├── PretrainedModelReference.py                 # Registry, revision, license, checksum and origin provenance.
    │   ├── WeightInitialization.py                     # Validated initialization strategy and parameters.
    │   └── ModelRecommendation.py                      # Ranked choice, evidence, constraints and uncertainty metadata.
    ├── training/
    │   ├── TrainingConfiguration.py                    # Immutable validated effective run configuration.
    │   ├── OptimizerConfiguration.py                  # Optimizer type and typed hyperparameters.
    │   ├── SchedulerConfiguration.py                  # Scheduler type, trigger and parameters.
    │   ├── LossConfiguration.py                       # Task-compatible loss and reduction configuration.
    │   ├── RegularizationConfiguration.py              # Typed regularization settings with applicability checks.
    │   ├── ResourceRequest.py                          # Device/pool/GPU/CPU/memory/time/cost request.
    │   ├── Run.py                                      # Run aggregate; owns legal state transitions and provenance.
    │   ├── RunStatus.py                                # Explicit job status enum and allowed transition rules.
    │   ├── RunProgress.py                              # Actual step/epoch progress and event sequence.
    │   ├── RunMetric.py                                # Named typed metric sample with step/split/timestamp.
    │   ├── Checkpoint.py                               # Atomic checkpoint metadata/checksum/best/final designation.
    │   ├── ExperimentTag.py                            # Validated searchable tag value object.
    │   └── TrainingEnvironment.py                      # Framework/hardware/driver/container provenance snapshot.
    ├── optimization/
    │   ├── HyperparameterStudy.py                      # Study aggregate, objective, budget, sampler/pruner references.
    │   ├── Trial.py                                    # Trial aggregate/state/config/metrics/checkpoint references.
    │   ├── ParameterDistribution.py                    # Typed categorical/int/float/conditional search space.
    │   └── OptimizationBudget.py                       # Trial/time/compute/cost cap value object.
    ├── diagnostics/
    │   ├── DiagnosticFinding.py                        # Evidence, rule version, confidence/limits and recommendations.
    │   ├── DiagnosticRuleDefinition.py                 # Rule identity/version/severity and applicability contract.
    │   ├── ProposedConfigurationChange.py              # Explicit immutable before/after diff requiring approval.
    │   └── DiagnosticEvidence.py                       # Metric/data references proving a finding.
    ├── evaluation/
    │   ├── Evaluation.py                               # Evaluation aggregate tied to immutable model/data/split.
    │   ├── EvaluationConfiguration.py                 # Metric set, slices, threshold and statistical method config.
    │   ├── MetricDefinition.py                         # Metric formula/version/direction/validity requirements.
    │   ├── MetricResult.py                             # Value, support, aggregation, undefined reason and provenance.
    │   ├── PredictionRecordReference.py                # Secure reference to paginated prediction/error data.
    │   ├── EvaluationSlice.py                          # Defined subgroup/slice predicate and support count.
    │   ├── ReadinessCheck.py                           # Evidence-backed pass/warn/fail/not-assessed item.
    │   └── Report.py                                   # Immutable report metadata and artifact reference.
    ├── artifacts/
    │   ├── Artifact.py                                 # Artifact metadata, owner, type, size/checksum and access policy.
    │   ├── ArtifactManifest.py                         # File list, serialization versions and integrity metadata.
    │   ├── ExportRequest.py                            # Target format/options/validation tolerances.
    │   └── ExportResult.py                             # Actual output, warnings, parity result and provenance.
    ├── deployment/
    │   ├── Deployment.py                               # Deployment aggregate and staged revision lifecycle.
    │   ├── DeploymentRevision.py                       # Immutable image/config/model/infra revision.
    │   ├── DeploymentTarget.py                         # Provider/runtime capability and prerequisite value object.
    │   ├── Endpoint.py                                 # Endpoint identity, health, auth and model-version reference.
    │   ├── RolloutPolicy.py                            # Canary/blue-green traffic and rollback constraints.
    │   ├── DeploymentStatus.py                         # Provider-observed deployment state and transitions.
    │   └── InferenceContract.py                        # Versioned validated input/output schema.
    ├── monitoring/
    │   ├── Monitor.py                                  # Monitor aggregate, source endpoint and retention configuration.
    │   ├── DriftMeasurement.py                         # Method, baseline/window, sample counts, result and uncertainty.
    │   ├── AlertPolicy.py                              # Threshold, window, notification and escalation rules.
    │   ├── Alert.py                                    # Alert lifecycle, evidence, acknowledgement and resolution.
    │   ├── Incident.py                                 # Incident timeline and linked deployment/run actions.
    │   └── RetrainingPolicy.py                         # Trigger, approvals, budgets, validation/rollback gates.
    ├── collaboration/
    │   ├── Comment.py                                 # Threaded comment entity with edit/resolve invariants.
    │   ├── Mention.py                                 # User/project mention value object.
    │   ├── Recipe.py                                  # Versioned shareable configuration/template with license.
    │   └── Notification.py                            # User-scoped event and delivery/read state.
    ├── plugins/
    │   ├── PluginDescriptor.py                         # Signed plugin identity, version, permissions and compatibility.
    │   ├── PluginPermission.py                         # Declarative permission scope value object.
    │   ├── PluginInstallation.py                       # Tenant installation state, pinning and revocation.
    │   └── PluginTrustStatus.py                        # Signature, scan, allowlist and provenance state.
    ├── governance/
    │   ├── Permission.py                              # Atomic permission identifier.
    │   ├── AccessPolicy.py                             # Resource/action/actor authorization policy abstraction.
    │   ├── AuditEvent.py                               # Immutable security/business audit record metadata.
    │   ├── RetentionPolicy.py                          # Typed retention/deletion rules.
    │   └── BudgetPolicy.py                             # Tenant/project compute and spend limits.
    └── events/                                        # Typed domain event classes emitted by aggregates.
```

## `packages/application` — Use cases and ports

```text
packages/application/                                  # Framework-independent orchestration over domain objects.
├── pyproject.toml
└── src/neuralforge_application/
    ├── ports/                                         # Interfaces defined by the application, implemented by adapters.
    │   ├── repositories/                              # Repository interfaces per aggregate, not generic ORM leakage.
    │   │   ├── ProjectRepository.py                   # Project aggregate persistence/query contract.
    │   │   ├── DatasetRepository.py                   # Dataset/version/profile persistence contract.
    │   │   ├── PipelineRepository.py                  # Pipeline version and fitted state persistence contract.
    │   │   ├── ModelRepository.py                     # Model definition/version persistence contract.
    │   │   ├── RunRepository.py                       # Run/progress/metric/checkpoint metadata persistence contract.
    │   │   ├── EvaluationRepository.py                # Evaluation and report persistence contract.
    │   │   ├── DeploymentRepository.py                # Deployment/revision/endpoint persistence contract.
    │   │   ├── MonitoringRepository.py                # Monitor/alert/incident persistence contract.
    │   │   ├── OrganizationRepository.py              # Tenant/member/role persistence contract.
    │   │   └── AuditRepository.py                     # Append-only audit persistence/query contract.
    │   ├── storage/                                   # Object-store, file, and secret abstractions.
    │   │   ├── ArtifactStore.py                       # Safe put/get/delete/stream and signed-download capability contract.
    │   │   ├── DatasetStore.py                        # Immutable source snapshot storage contract.
    │   │   ├── CheckpointStore.py                     # Atomic checkpoint and retention operations.
    │   │   ├── SecretStore.py                         # Write/read-by-reference/rotate secret contract; no secret listing.
    │   │   └── TemporaryWorkspace.py                  # Isolated job scratch lifecycle contract.
    │   ├── jobs/                                      # Queue/scheduler abstractions.
    │   │   ├── JobQueue.py                            # Durable enqueue/claim/ack/retry contract.
    │   │   ├── JobLease.py                            # Lease renewal and fencing token value contract.
    │   │   ├── JobEventPublisher.py                   # Ordered event publish/replay contract.
    │   │   ├── ResourceScheduler.py                   # Capacity-aware placement and quotas contract.
    │   │   └── Clock.py                               # UTC clock abstraction.
    │   ├── security/                                  # Identity and policy ports.
    │   │   ├── IdentityProvider.py                    # OIDC/SAML identity verification contract.
    │   │   ├── AuthorizationService.py                # Resource/action authorization contract.
    │   │   └── AuditWriter.py                         # Append-only audit event contract.
    │   ├── data/                                      # Connector and transform extension ports.
    │   │   ├── DataConnector.py                       # Connect/test/preview/snapshot connector interface.
    │   │   ├── DataReader.py                          # Bounded streaming record reader interface.
    │   │   ├── DataProfiler.py                        # Modality-specific profiling contract.
    │   │   ├── TransformOperator.py                   # Typed fit/transform/preview operator contract.
    │   │   └── DatasetSplitter.py                     # Validated split generation contract.
    │   ├── ml/                                        # Framework-neutral ML capability ports.
    │   │   ├── FrameworkAdapter.py                    # Capability discovery and model lifecycle contract.
    │   │   ├── ModelFactory.py                        # Validated architecture construction contract.
    │   │   ├── Trainer.py                             # Train/evaluate/checkpoint/cancel contract.
    │   │   ├── MetricCalculator.py                    # Task/metric computation contract.
    │   │   ├── Explainer.py                           # Attribution/activation explanation contract.
    │   │   ├── ModelExporter.py                       # Format export plus parity validation contract.
    │   │   └── ResourceProbe.py                       # Real device/runtime telemetry contract.
    │   ├── external/                                  # External provider/tracker/notification ports.
    │   │   ├── CloudComputeProvider.py                # Provision/status/terminate cloud resources contract.
    │   │   ├── DeploymentProvider.py                   # Deploy/rollout/rollback/status contract.
    │   │   ├── ExperimentTracker.py                   # Opt-in metrics/config/artifact tracking contract.
    │   │   ├── NotificationProvider.py                # Signed/validated outbound notification contract.
    │   │   ├── ModelRegistry.py                       # Search/download/revision/license registry contract.
    │   │   └── AssistantProvider.py                   # Consent-scoped inference provider contract.
    │   └── events/                                    # Event bus/outbox contracts.
    │       ├── DomainEventPublisher.py                # Reliable event publication contract.
    │       └── TransactionalOutbox.py                 # Atomic persistence + event dispatch contract.
    ├── use_cases/                                     # One class per cohesive application action/transaction.
    │   ├── organizations/                             # Create organization, invite member, change role, audit access.
    │   ├── projects/                                  # Create/update/archive/delete/fork/restore project.
    │   ├── connectors/                                # Configure/test connector and manage secret references.
    │   ├── datasets/                                  # Upload/ingest/profile/version/compare/delete dataset.
    │   ├── pipelines/                                 # Validate/save/preview/execute/version pipeline.
    │   ├── models/                                    # Catalog/recommend/build/import/pretrain/version model.
    │   ├── training/                                  # Validate/submit/control/recover/fork training run.
    │   ├── studies/                                   # Create/start/stop/resume HPO and retrieve trial results.
    │   ├── diagnostics/                               # Diagnose run/data and propose—not silently apply—changes.
    │   ├── evaluations/                               # Evaluate, slice, compare, generate report/readiness result.
    │   ├── artifacts/                                 # List, authorize, verify, expire and download artifacts.
    │   ├── deployments/                               # Export/optimize/stage/deploy/rollout/rollback/terminate.
    │   ├── monitoring/                                # Configure monitors, measure drift, alert, approve retraining.
    │   ├── collaboration/                             # Comment, resolve, notify, publish/fork recipe.
    │   ├── plugins/                                   # Validate/sign/approve/install/revoke/execute plugin jobs.
    │   ├── assistant/                                 # Disclose context, redact, call provider, store permitted result.
    │   ├── configuration/                             # Validate, migrate, diff, export effective config.
    │   └── audit/                                     # Query authorized immutable audit records.
    ├── policies/                                      # Application policies, not HTTP-specific auth code.
    │   ├── AccessPolicyEvaluator.py                   # Evaluates actor/resource/action via authorization port.
    │   ├── CapabilityPolicy.py                        # Checks framework/task/operation compatibility.
    │   ├── QuotaPolicy.py                             # Enforces project/org budgets before expensive work.
    │   ├── RetentionPolicy.py                         # Calculates safe expiry/deletion eligibility.
    │   └── DataDisclosurePolicy.py                    # Determines what context may leave the installation.
    ├── commands/                                      # Immutable typed input commands for use cases.
    ├── results/                                       # Typed outputs; no HTTP response coupling.
    ├── mappers/                                       # Persistence/API-free mappings between domain and results.
    └── errors/                                        # Application-level not-found/conflict/authorization errors.
```

## `packages/infrastructure` — Concrete adapters

```text
packages/infrastructure/                               # Implements application ports; external SDKs stay behind adapters.
├── pyproject.toml
└── src/neuralforge_infrastructure/
    ├── composition/
    │   ├── InfrastructureSettings.py                  # Validates DB, object store, queue, provider and security settings.
    │   └── InfrastructureCompositionRoot.py            # Constructs adapters selected by explicit configuration.
    ├── persistence/
    │   ├── sqlalchemy/                                # PostgreSQL/SQLite persistence adapter implementation.
    │   │   ├── DatabaseEngineFactory.py                # Creates bounded connection pools and transaction settings.
    │   │   ├── UnitOfWork.py                           # Explicit transaction boundary and repository lifecycle.
    │   │   ├── mappings/                               # ORM persistence records and domain mappers.
    │   │   │   ├── ProjectRecord.py                    # DB-only project row mapping.
    │   │   │   ├── DatasetRecord.py                    # DB-only dataset/version row mapping.
    │   │   │   ├── RunRecord.py                        # DB-only run/status/lease/metric metadata mapping.
    │   │   │   └── ...                                 # One record/mapping per persisted aggregate/value set.
    │   │   ├── repositories/                           # Concrete implementations of repository ports.
    │   │   ├── migrations/                             # Ordered schema migrations; reversible where feasible.
    │   │   └── TransactionalOutboxRepository.py         # Atomic domain event/outbox persistence.
    │   ├── object_storage/
    │   │   ├── LocalArtifactStore.py                    # Safe local filesystem adapter for single-user install.
    │   │   ├── S3ArtifactStore.py                       # S3 adapter with tenant policy, encryption and multipart support.
    │   │   ├── GcsArtifactStore.py                      # GCS adapter with generation checks and encryption config.
    │   │   ├── AzureBlobArtifactStore.py                # Azure Blob adapter with versioning and access policy.
    │   │   ├── SafePathResolver.py                      # Prevents traversal and enforces storage-root containment.
    │   │   └── ContentChecksumService.py                # Streaming checksum and integrity verification.
    │   ├── secrets/
    │   │   ├── LocalKeyringSecretStore.py               # OS keyring-backed local secret adapter.
    │   │   ├── VaultSecretStore.py                      # Vault/KMS-backed production secret adapter.
    │   │   └── SecretReferenceMapper.py                 # Maps opaque references; never serializes values to API DTOs.
    │   ├── queues/
    │   │   ├── RedisJobQueue.py                         # Durable Redis-compatible queue implementation with leases.
    │   │   ├── JobEventStore.py                         # Ordered persistent event replay implementation.
    │   │   └── RedisResourceScheduler.py                # Worker slots, quotas, resource labels and fair scheduling.
    │   ├── identity/
    │   │   ├── OidcIdentityProvider.py                  # OIDC discovery/JWKS/token validation adapter.
    │   │   └── LocalIdentityProvider.py                 # Loopback-only local install identity; unavailable in server prod.
    │   ├── connectors/                                  # Each connector is a separate class/module behind DataConnector.
    │   │   ├── local/                                   # CSV/TSV/JSON/JSONL/Parquet/HDF5 and modality file readers.
    │   │   ├── sql/                                     # PostgreSQL, MySQL, SQLite, SQL Server read-only connectors.
    │   │   ├── nosql/                                   # MongoDB connector with bounded projection/query support.
    │   │   ├── object_store/                            # S3/GCS/Azure connectors with pinned object revisions.
    │   │   ├── rest/                                    # Safe REST pagination/auth/retry connector.
    │   │   ├── streaming/                               # Kafka/PubSub offset/checkpoint-aware connector.
    │   │   ├── public_datasets/                          # Hugging Face/Kaggle license/revision-aware clients.
    │   │   ├── web_collection/                           # Domain-allowlisted, rate-limited fetch adapters.
    │   │   └── synthetic/                               # Explicit seeded synthetic generators and metadata marker.
    │   ├── ml/                                          # Actual framework implementation adapters.
    │   │   ├── pytorch/                                 # PyTorch model factory, trainer, checkpoint and runtime probes.
    │   │   ├── tensorflow/                              # Keras model/trainer/checkpoint/export adapter.
    │   │   ├── jax/                                     # JAX model/train/checkpoint adapter.
    │   │   ├── onnx/                                    # ONNX checker/runtime/interoperability adapter.
    │   │   ├── architectures/                           # First-party registered implementations by modality/family.
    │   │   ├── metrics/                                 # Versioned metric calculators by task and modality.
    │   │   ├── explainability/                          # SHAP/Captum/LIME/Grad-CAM adapters with compatibility checks.
    │   │   └── export/                                  # Real format converters and numerical parity validator.
    │   ├── cloud/                                       # AWS/GCP/Azure provider SDK adapters and cleanup/reconciliation.
    │   ├── deployment/                                  # Kubernetes, Docker, serverless, edge, browser and mobile targets.
    │   ├── tracking/                                    # W&B, MLflow, TensorBoard, and custom tracker adapters.
    │   ├── registries/                                  # Hugging Face, TorchVision/timm and supported model registries.
    │   ├── notifications/                               # Email, webhook, Slack/Teams or other configured channels.
    │   ├── assistant/                                   # Provider-specific LLM adapters with disclosure/redaction wrapper.
    │   └── observability/                               # OpenTelemetry exporters and provider health adapters.
    └── security/
        ├── ArchiveInspectionService.py                  # Archive member count/size/path/decompression safety checks.
        ├── UploadContentValidator.py                    # Validates supported formats independent of filename/MIME claims.
        ├── SandboxExecutor.py                           # Starts isolated plugin/custom-transform execution environment.
        ├── SecretRedactor.py                            # Redacts configured secret values/patterns from logs/errors.
        └── ArtifactSignatureVerifier.py                  # Validates signed manifests/checksums before trusted operations.
```

## `apps/worker` — Durable background job runtime

```text
apps/worker/                                           # Worker process; leases, executes, emits events and acknowledges jobs.
├── pyproject.toml                                     # Worker runtime dependencies.
├── Dockerfile                                         # Non-root worker image; no host Docker socket by default.
├── src/neuralforge_worker/
│   ├── __main__.py                                    # Worker entry point with signal handling and graceful shutdown.
│   ├── composition/                                   # Worker-specific dependency wiring and resource profile selection.
│   ├── runtime/
│   │   ├── WorkerSupervisor.py                        # Claims jobs, renews leases, enforces shutdown and concurrency.
│   │   ├── JobHandlerRegistry.py                      # Maps typed job kinds to handler classes.
│   │   ├── JobExecutionContext.py                     # Actor, tenant, trace, budget, cancellation and event publisher context.
│   │   ├── CancellationToken.py                       # Thread/process-safe cooperative cancellation abstraction.
│   │   ├── WorkerHeartbeat.py                         # Liveness and lease renewal service.
│   │   ├── RetryPolicy.py                             # Per-job safe retry/backoff and deduplication policy.
│   │   └── OrphanJobReconciler.py                     # Finds stale jobs and applies documented recovery transitions.
│   ├── handlers/
│   │   ├── IngestDatasetJobHandler.py                 # Executes bounded connector snapshot ingestion.
│   │   ├── ProfileDatasetJobHandler.py                # Runs modality-specific profile calculation.
│   │   ├── ExecutePipelineJobHandler.py               # Executes versioned pipeline with fit-scope isolation.
│   │   ├── TrainModelJobHandler.py                    # Trains, checkpoints, logs, and handles cancellation.
│   │   ├── HyperparameterStudyJobHandler.py            # Schedules/prunes trials under study budget.
│   │   ├── DiagnoseRunJobHandler.py                    # Applies versioned diagnostic rules to recorded evidence.
│   │   ├── EvaluateModelJobHandler.py                 # Computes metrics/slices/reports on declared split.
│   │   ├── ExplainPredictionJobHandler.py              # Executes compatible attribution with resource limits.
│   │   ├── ExportModelJobHandler.py                   # Converts artifact and validates numerical parity.
│   │   ├── OptimizeModelJobHandler.py                 # Quantization/pruning/distillation/benchmark tasks.
│   │   ├── ProvisionResourceJobHandler.py              # Provisions cloud compute under approved budget/consent.
│   │   ├── DeployModelJobHandler.py                   # Stages deployment and runs smoke/security checks.
│   │   ├── MonitorEndpointJobHandler.py               # Collects endpoint metrics and drift windows.
│   │   ├── DeliverNotificationJobHandler.py            # Performs retryable notification delivery.
│   │   └── ExecutePluginJobHandler.py                  # Runs plugin only in isolated sandbox with declared permissions.
│   ├── policies/
│   │   ├── WorkerResourcePolicy.py                     # Enforces per-job CPU/memory/GPU/time/disk limits.
│   │   └── TenantQuotaEnforcer.py                      # Enforces compute and spend quota at execution time.
│   └── observability/
│       ├── WorkerMetrics.py                            # Queue/job/resource metrics.
│       └── WorkerLogContext.py                         # Structured job-scoped logs with redaction.
└── tests/                                              # Job handler, retry, lease loss, cancellation and restart tests.
```

## `services/model-serving` — Generated/runtime inference service

```text
services/model-serving/                                # Separately deployable inference runtime, independent of control plane.
├── pyproject.toml                                     # Runtime dependencies per supported framework/export format.
├── Dockerfile                                         # Minimal non-root serving image and health checks.
├── src/neuralforge_serving/
│   ├── ServingApplication.py                          # Application lifecycle, dependency wiring and shutdown behavior.
│   ├── ModelArtifactLoader.py                         # Verifies manifest/checksums and safe-loads supported artifacts.
│   ├── InferenceContractValidator.py                  # Validates request schema and model-version compatibility.
│   ├── InferenceService.py                            # Batching, preprocessing parity, model execution and response mapping.
│   ├── AuthenticationPolicy.py                        # Configurable API auth/rate/tenant policy adapter.
│   ├── RequestSizePolicy.py                            # Bounds payload and batch sizes.
│   ├── HealthService.py                               # Liveness/readiness/model-loaded/version checks.
│   ├── TelemetryRecorder.py                            # Privacy-configured latency/errors/prediction telemetry.
│   ├── routes/                                        # REST/gRPC/WebSocket/batch route adapters.
│   └── providers/                                     # Framework-specific loaded model runtime adapters.
└── tests/                                              # Contract, parity, load, auth, schema and failure tests.
```

## `packages/sdk-python`, `apps/cli`, and `apps/desktop`

```text
packages/sdk-python/                                   # Public supported Python client/API; no server internals exposed.
├── pyproject.toml                                     # Published package metadata and optional dependency extras.
├── src/neuralforge/
│   ├── __init__.py                                    # Stable public API exports and package version.
│   ├── client/                                        # Local/remote clients, auth, transport and retries.
│   ├── entities/                                      # Typed client-side domain representations, immutable where appropriate.
│   ├── resources/                                     # Project/Dataset/Run/Study/Deployment resource objects with methods.
│   ├── jobs/                                          # Async job handles, event iteration, cancellation and wait semantics.
│   ├── builders/                                      # Fluent validated pipeline/model/training configuration builders.
│   ├── exceptions/                                    # Typed public exception hierarchy mapped from API error codes.
│   ├── generated/                                     # Generated API schemas/client portions, not manually edited.
│   └── notebook/                                      # Tested notebook display helpers and magics, if enabled.
├── tests/                                              # API compatibility, local mode, remote mode and tutorial tests.
└── README.md                                           # Public SDK reference and executable code-first tutorial.

apps/cli/                                               # `nf` terminal application; composes SDK objects, no duplicate business logic.
├── pyproject.toml                                     # CLI package metadata.
├── src/neuralforge_cli/
│   ├── NeuralForgeCli.py                              # CLI composition root and command registration.
│   ├── commands/                                      # One command class per cohesive operation; delegates to SDK.
│   ├── presenters/                                   # Human-readable, JSON and machine-readable output presenters.
│   ├── prompts/                                      # Typed interactive input flows; noninteractive flags always available.
│   └── configuration/                               # Safe config file discovery, validation and secret reference handling.
└── tests/                                              # Command behavior, exit codes, redaction and machine-output tests.

apps/desktop/                                            # Optional desktop shell for local-first install; same web/API/domain services.
├── package.json                                      # Desktop shell dependencies and signing/build commands.
├── src/main/                                         # OS window, secure IPC bridge, local service lifecycle manager.
├── src/preload/                                      # Minimal allowlisted browser-to-native IPC surface.
├── src/renderer/                                     # Reuses web app packages; no Node privileges in renderer.
├── packaging/                                        # Signed installers, updates, permissions and uninstall behavior.
└── tests/                                              # IPC security, upgrade, data migration and lifecycle tests.
```

## `packages/contracts` — Shared contracts and generated schemas

```text
packages/contracts/                                    # Versioned language-neutral schemas/contracts.
├── openapi/                                           # OpenAPI source for REST API; generated docs/clients derive from this.
├── json-schema/                                       # Config, plugin manifest, inference input/output, report schemas.
├── events/                                            # Versioned event envelopes and payload schemas.
├── capability-matrix/                                 # Machine-readable task/framework/feature compatibility definitions.
├── error-codes/                                       # Stable API/domain error code catalog and remediation semantics.
└── generators/                                        # Reproducible code generation scripts with drift checks.
```

## `packages/plugins` and `plugins/examples`

```text
packages/plugin-sdk/                                   # Public contracts, validators, sandbox protocol and developer test harness.
├── src/neuralforge_plugin_sdk/
│   ├── Plugin.py                                      # Typed base contract and lifecycle; no host process privileges.
│   ├── DataConnectorPlugin.py                         # Connector plugin input/output protocol.
│   ├── ModelArchitecturePlugin.py                     # Architecture construction and capability contract.
│   ├── MetricPlugin.py                                # Deterministic metric protocol and schema.
│   ├── DebugRulePlugin.py                             # Evidence-backed diagnostic rule protocol.
│   ├── TransformPlugin.py                             # Bounded fit/transform/preview protocol.
│   ├── DeploymentTargetPlugin.py                      # Export/deploy/health/rollback protocol.
│   ├── VisualizerPlugin.py                            # Declarative safe visualization output protocol.
│   ├── PluginManifest.py                              # Signed manifest parser and compatibility/permission validation.
│   ├── SandboxClient.py                               # Restricted RPC client to isolated host runtime.
│   └── testing/                                       # Contract fixtures and plugin conformance test base classes.
└── tests/                                              # SDK API stability and sandbox protocol tests.

plugins/examples/                                       # Real, minimal, reviewed plugins used as SDK examples.
├── median_imputer/                                    # Example transform plugin with tests, manifest and security declaration.
├── balanced_accuracy_metric/                          # Example custom metric with mathematical edge-case tests.
└── README.md                                          # Build/sign/test/install workflow and threat model.
```

## `deploy` — Operations and infrastructure

```text
deploy/
├── local/
│   ├── compose.yaml                                   # Complete local multi-service stack with health checks and named volumes.
│   ├── compose.gpu.yaml                               # Explicit optional GPU runtime overlay with prerequisites.
│   └── local-data-policy.md                           # Local storage, backup, permission and deletion guidance.
├── kubernetes/
│   ├── helm/neuralforge/                              # Helm chart for API, workers, web, serving, migrations, policies.
│   ├── base/                                          # Versioned Kubernetes resources and secure defaults.
│   ├── policies/                                      # NetworkPolicy, PodSecurity, resource quotas, RBAC.
│   ├── autoscaling/                                   # Queue/GPU-aware worker autoscaling policies and limits.
│   └── examples/                                      # Environment overlays; placeholders are clearly marked and unusable until configured.
├── terraform/
│   ├── aws/                                           # VPC, EKS, RDS, S3, KMS, Secrets Manager, GPU pools, IAM.
│   ├── gcp/                                           # VPC, GKE, Cloud SQL, GCS, KMS, Secret Manager, GPU pools, IAM.
│   └── azure/                                         # VNet, AKS, PostgreSQL, Blob, Key Vault, GPU pools, managed identity.
├── observability/
│   ├── dashboards/                                    # Versioned API/queue/worker/GPU/deployment dashboards.
│   ├── alerts/                                        # Actionable alert rules with runbook links.
│   └── otel-collector/                                # Redacting telemetry collector configuration.
├── backup/                                            # Backup/restore and disaster recovery scripts and policies.
├── security/                                          # TLS, key rotation, network boundaries and hardening examples.
└── runbooks/                                          # Incident, upgrade, restore, worker stuck, provider outage procedures.
```

## `docs` — Documentation hierarchy

```text
docs/
├── index.md                                           # Documentation home and supported product/version matrix.
├── user/
│   ├── guided-workflow.md                             # Complete beginner lifecycle, prerequisites and recovery paths.
│   ├── expert-workspace.md                            # Project workspace, configs, runs and controls.
│   ├── data-connectors/                               # One setup/use/limits/security document per connector.
│   ├── data-pipelines.md                              # Operators, fit scopes, splits, preview and lineage.
│   ├── model-catalog.md                               # Every supported architecture, constraints and licenses.
│   ├── training.md                                    # Hyperparameters, resources, checkpoint/recovery semantics.
│   ├── debugging.md                                   # Rule methods, evidence and explanation limitations.
│   ├── evaluation.md                                  # Metric formula/version, task applicability and test-set guidance.
│   ├── deployment.md                                  # Export, parity, serving, rollout, rollback and cost/security.
│   ├── monitoring.md                                  # Drift, delayed labels, alerting, retention and retraining approval.
│   └── privacy-and-data.md                            # Data flow, telemetry, assistant disclosure and deletion/export.
├── admin/
│   ├── installation-local.md                          # Supported local setup and data location.
│   ├── installation-kubernetes.md                     # Production sizing, TLS, OIDC, storage and worker pools.
│   ├── cloud-providers/                               # Validated AWS/GCP/Azure deployment guides.
│   ├── identity-and-rbac.md                           # OIDC/SAML setup, role matrix and policy configuration.
│   ├── quotas-retention.md                            # Compute/storage/cost controls and lifecycle rules.
│   ├── backup-restore.md                              # Tested backup/restore instructions and RPO/RTO definitions.
│   ├── upgrades.md                                    # Migration, compatibility, rollback and zero/low-downtime process.
│   └── operations.md                                  # Dashboards, alerts, logs, capacity and incident response.
├── developer/
│   ├── architecture.md                                # Domain boundaries, dependency direction, composition roots.
│   ├── domain-model.md                                # Aggregates, invariants, state machines and events.
│   ├── api.md                                         # OpenAPI, errors, auth, pagination, events and deprecation.
│   ├── python-sdk.md                                  # Typed API, resource methods, async jobs and compatibility.
│   ├── cli.md                                         # Commands, exit codes and scripting output.
│   ├── plugin-sdk.md                                  # Contracts, permissions, sandbox, signing and conformance tests.
│   ├── testing.md                                     # Unit/integration/E2E/security/performance test strategy.
│   └── contributing.md                                # Change workflow and definition of done.
├── reference/
│   ├── configuration-schema.md                        # Config schema/version/default/migration reference.
│   ├── capability-matrix.md                           # Generated support matrix by framework/task/operation.
│   ├── environment-variables.md                       # All settings, defaults, sensitivity and deployment applicability.
│   ├── error-catalog.md                               # Error codes, cause and remediation.
│   └── licensing.md                                   # Product/dependency/model/data license inventory and obligations.
└── decisions/                                         # Accepted architecture decision records (ADRs), one decision per file.
```

## `tests` — Cross-cutting verification

```text
tests/
├── contract/                                          # API/event/plugin contract tests across implementations.
├── integration/
│   ├── connectors/                                    # Real or containerized connector integration tests.
│   ├── database/                                      # Migration, transaction, concurrency and restore tests.
│   ├── queue/                                         # Lease, retry, cancellation, replay and recovery tests.
│   ├── frameworks/                                    # Supported model/task/framework lifecycle tests.
│   ├── exports/                                       # Artifact parity tests on representative inputs.
│   ├── deployment/                                    # Provider staging, health, rollout, rollback and cleanup tests.
│   ├── tracking/                                      # Opt-in external tracker integration tests.
│   └── identity/                                      # OIDC/SAML, role and tenant boundary tests.
├── e2e/
│   ├── journeys/                                      # Full data-to-deployment user journeys for each supported task family.
│   ├── guided-mode/                                   # Wizard persistence/backtracking/error recovery tests.
│   ├── expert-mode/                                   # Direct workflow, config, comparison and artifact tests.
│   ├── collaboration/                                 # Concurrent edits/comments/permissions/notifications tests.
│   └── fixtures/                                      # Small licensed fixtures; synthetic fixtures labeled and seeded.
├── performance/                                      # Load, resource, event throughput and large-data benchmark suites.
├── security/
│   ├── tenancy/                                       # Cross-tenant object, artifact, queue/cache and event isolation tests.
│   ├── uploads/                                       # Fuzz/archive/path/MIME/decompression tests.
│   ├── plugins/                                       # Sandbox escape, privilege and resource exhaustion tests.
│   ├── assistant/                                     # Context disclosure, prompt injection and redaction tests.
│   └── api/                                           # IDOR, CSRF, SSRF, rate, auth and input validation tests.
├── accessibility/                                     # Keyboard, screen-reader, contrast and automated axe checks.
└── fixtures/                                          # Factory classes/builders for domain entities and test data.
```

## `scripts` and `.github`

```text
scripts/
├── dev.py                                            # Developer environment checks and local startup orchestration.
├── migrate.py                                        # Explicit database migration command with backup checks.
├── generate_contracts.py                             # Regenerates clients/schemas and fails on uncommitted drift.
├── verify_capabilities.py                            # Checks every advertised capability has implementation/tests/docs.
├── build_sbom.py                                     # Produces software bill of materials.
├── verify_release.py                                 # Release gate runner; no skipped mandatory test classes.
├── backup.py                                         # Encrypted consistent backup operation.
├── restore.py                                        # Restore validation and recovery workflow.
└── cleanup_cloud.py                                  # Audited provider resource reconciliation; dry-run default.

.github/
├── workflows/
│   ├── pull-request.yml                              # Format, lint, type, unit, build, SAST and dependency checks.
│   ├── integration.yml                               # Container/provider integration test workflows.
│   ├── e2e.yml                                       # Browser/system journey workflows.
│   ├── security.yml                                  # Secret, dependency, SBOM, container and policy scanning.
│   ├── release.yml                                   # Signed versioned packages/images/charts and provenance.
│   └── docs.yml                                      # Link/schema/example validation for documentation.
├── dependabot.yml                                    # Automated dependency update policy with grouped updates.
├── CODEOWNERS                                        # Domain/service ownership requirements for review.
├── ISSUE_TEMPLATE/                                   # Bug, security-safe issue, feature and connector templates.
└── PULL_REQUEST_TEMPLATE.md                          # Change scope, tests, migration/security/accessibility checklist.
```

## Required naming and implementation conventions

- Python classes use `PascalCase.py` file names for one primary class, or package directories for cohesive families; public methods and types have explicit annotations.
- TypeScript components/classes use `PascalCase.tsx/.ts`; pure functions use camelCase and remain small. Domain behavior lives in typed domain/application packages, not React components.
- A repository interface is named for its aggregate (for example, `RunRepository`), with concrete adapters named by technology. Do not create a generic repository that hides important aggregate queries.
- A use case is a class named as an action (`StartTrainingRun`, `EvaluateModel`, `CreateDatasetSnapshot`) with one public `execute` method and typed command/result.
- External SDK exceptions are translated at adapter boundaries into stable application/domain error types; UI never parses provider stack traces.
- Keep dependency direction inward: `domain` depends on no app/infrastructure libraries; `application` depends on domain and ports; infrastructure implements ports; API/worker/CLI/desktop are composition/presentation layers.
- Every persistent aggregate has a repository contract, migration, domain tests, authorization policy, audit behavior, and deletion/retention policy.
- Every background operation has a job type, handler class, idempotency/retry/cancel/timeout policy, event schema, resource policy, and integration tests.
- Every advertised capability is represented in capability discovery and has implementation, docs, tests, dependency/license metadata, and an end-to-end path.
- Avoid empty files in a working implementation. This document's tree specifies intended files; a generated scaffold must not create misleading empty modules. Create files when implementing their responsibility.

## Completion checklist for using this layout

1. Confirm architecture decisions and dependency versions in ADRs before generating code.
2. Generate the project scaffold with package metadata, lint/type/test configuration, CI, and a working health check.
3. Implement domain entities and state transitions before persistence/API/UI workflows.
4. Implement ports and adapters through dependency injection; test adapters independently and against their contracts.
5. Add each vertical capability with domain, application, adapter, API, UI, documentation, migration, authorization, audit, and tests together.
6. Keep the capability registry authoritative; the UI must never advertise a capability absent from its implementation/test state.
7. Use this file as the repository structure contract; deviations require an ADR explaining why responsibilities and OO boundaries remain intact.
