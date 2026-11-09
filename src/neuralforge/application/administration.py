"""Administration use case boundary for process-wide settings."""

class GlobalConfigurationService:
    """Enforces the global-admin role before reading or changing settings."""
    def __init__(self, store): self.store=store

    @staticmethod
    def _require_admin(actor):
        if not actor or actor.get("role")!="admin": raise PermissionError("Administrator access required.")

    def read(self, actor):
        self._require_admin(actor)
        return self.store.get_global_config()

    def update(self, actor, changes: dict):
        self._require_admin(actor)
        if not isinstance(changes,dict) or not changes: raise ValueError("Provide at least one configuration setting.")
        for key,value in changes.items(): self.store.set_global_config(key,value)
        return self.store.get_global_config()
