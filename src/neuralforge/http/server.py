"""Small local HTTP adapter for the first working vertical slice."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from neuralforge.adapters.sqlite_store import SQLiteStore
from neuralforge.application.use_cases import ProjectService, CsvDatasetService
from neuralforge.application.training import LocalTrainingService
from neuralforge.application.identity import IdentityService
from neuralforge.application.administration import GlobalConfigurationService
from neuralforge.domain.projects import DomainError
from neuralforge.web.app import HTML


class NeuralForgeHandler(BaseHTTPRequestHandler):
    server_version = "NeuralForge/0.1"

    def _json(self, status, payload, session_token=None, clear_session=False):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if session_token: self.send_header("Set-Cookie",f"nf_session={session_token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={self.server.identity.SESSION_SECONDS}")
        if clear_session: self.send_header("Set-Cookie","nf_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length", "0"))
        max_bytes=self.server.store.get_global_config().get("max_upload_bytes",CsvDatasetService.MAX_BYTES)
        if length > max_bytes:
            raise ValueError(f"Request body exceeds configured upload limit ({max_bytes // (1024*1024)} MiB).")
        return self.rfile.read(length)

    def _user(self):
        cookie=self.headers.get("Cookie", "")
        token=None
        for part in cookie.split(";"):
            key,sep,value=part.strip().partition("=")
            if key=="nf_session" and sep: token=value
        return self.server.identity.authenticate(token)

    def _require_user(self):
        user=self._user()
        if user is None:
            self._json(401,{"error":{"code":"AUTH_REQUIRED","message":"Sign in to continue."}})
            return None
        return user

    def _set_session_cookie(self, token):
        self.send_header("Set-Cookie",f"nf_session={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={self.server.identity.SESSION_SECONDS}")

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path not in ("/", "/api/health", "/api/auth/me"):
            user=self._require_user()
            if user is None: return
        else: user=self._user()
        if parsed.path == "/":
            import html
            app_name=self.server.store.get_global_config().get("application_name","NeuralForge")
            body = HTML.replace("NeuralForge",html.escape(str(app_name))).encode()
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        if parsed.path == "/api/health": return self._json(200, {"status": "ok", "version": "0.2.0"})
        if parsed.path == "/api/auth/me": return self._json(200, {"user": ({k:user[k] for k in ("id","username","role")} if user else None)})
        if parsed.path == "/api/admin/config":
            if user["role"]!="admin": return self._json(403,{"error":{"code":"FORBIDDEN","message":"Administrator access required."}})
            return self._json(200,{"config":self.server.administration.read(user)})
        if parsed.path == "/api/projects": return self._json(200, {"projects": [{**p.to_dict(),"can_manage":self.server.store.is_owner(p.id.value,user["id"]),"can_write":self.server.store.can_access(p.id.value,user["id"],write=True)} for p in self.server.store.list_for_user(user["id"])]})
        if parsed.path.startswith("/api/runs/"):
            run = self.server.store.get_run(parsed.path.rsplit("/",1)[-1])
            if not run or not self.server.store.can_access(run["project_id"],user["id"]): return self._json(404,{"error":{"code":"NOT_FOUND","message":"Run not found."}})
            return self._json(200, {"run": run})
        if parsed.path.startswith("/api/projects/") and parsed.path.endswith("/runs"):
            project_id = parsed.path.split("/")[3]
            if not self.server.store.can_access(project_id,user["id"]): return self._json(404,{"error":{"code":"NOT_FOUND","message":"Project not found."}})
            return self._json(200, {"runs": self.server.store.list_runs(project_id)})
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 4 and parts[:2] == ["api", "projects"] and parts[3] == "datasets":
            if not self.server.store.can_access(parts[2],user["id"]): return self._json(404,{"error":{"code":"NOT_FOUND","message":"Project not found."}})
            return self._json(200, {"datasets": [p.to_dict() for p in self.server.datasets.repository.list_profiles(parts[2])]})
        self._json(404, {"error": {"code": "NOT_FOUND", "message": "Resource not found."}})

    def _origin_allowed(self):
        origin=self.headers.get("Origin")
        if origin and urlparse(origin).netloc != self.headers.get("Host"):
            self._json(403,{"error":{"code":"CSRF_REJECTED","message":"Cross-origin state-changing request rejected."}})
            return False
        if self.headers.get("Sec-Fetch-Site")=="cross-site":
            self._json(403,{"error":{"code":"CSRF_REJECTED","message":"Cross-site request rejected."}})
            return False
        return True

    def do_POST(self):
        if not self._origin_allowed(): return
        parsed = urlparse(self.path)
        try:
            if parsed.path in ("/api/auth/register", "/api/auth/login"):
                payload=json.loads(self._body() or b"{}")
                if parsed.path.endswith("register"):
                    user,token=self.server.identity.register(payload.get("username",""),payload.get("password",""))
                else:
                    source=self.client_address[0] if self.client_address else "unknown"
                    user,token=self.server.identity.login(payload.get("username",""),payload.get("password",""),source)
                return self._json(200 if parsed.path.endswith("login") else 201,{"user":{k:user[k] for k in ("id","username","role")}},session_token=token)
            user=self._require_user()
            if user is None: return
            if parsed.path == "/api/auth/password/change":
                payload=json.loads(self._body() or b"{}")
                self.server.identity.change_password(user["id"],payload.get("current_password",""),payload.get("new_password",""))
                return self._json(200,{"password_changed":True},clear_session=True)
            if parsed.path == "/api/auth/logout":
                self.server.identity.logout(_cookie_value(self.headers.get("Cookie",""),"nf_session"))
                return self._json(200,{"logged_out":True},clear_session=True)
            if parsed.path == "/api/projects":
                payload = json.loads(self._body() or b"{}")
                project = self.server.projects.create(payload.get("name", ""), payload.get("task_type", ""), payload.get("description", ""), owner_id=user["id"])
                return self._json(201, {"project": project.to_dict()})
            parts = parsed.path.strip("/").split("/")
            if len(parts)==4 and parts[:2]==["api","projects"] and parts[3]=="share":
                if not self.server.store.is_owner(parts[2],user["id"]): return self._json(403,{"error":{"code":"FORBIDDEN","message":"Only the project owner can manage sharing."}})
                payload=json.loads(self._body() or b"{}")
                self.server.store.share_project(parts[2],payload.get("username",""),payload.get("role","viewer"))
                return self._json(200,{"shared":True})
            if len(parts) == 4 and parts[:2] == ["api", "datasets"] and parts[3] == "target":
                source=self.server.store.dataset_source(parts[2])
                if not source or not self.server.store.can_access(source["project_id"],user["id"],write=True): return self._json(404,{"error":{"code":"NOT_FOUND","message":"Dataset not found."}})
                payload = json.loads(self._body())
                self.server.store.set_target(parts[2], payload.get("target_column", ""))
                return self._json(200, {"target_column": payload.get("target_column")})
            if len(parts) == 4 and parts[:2] == ["api", "projects"] and parts[3] == "train":
                if not self.server.store.can_access(parts[2],user["id"],write=True): return self._json(404,{"error":{"code":"NOT_FOUND","message":"Project not found."}})
                payload = json.loads(self._body() or b"{}")
                run = self.server.training.start(parts[2], payload.get("dataset_id", ""), payload.get("target_column", ""), payload.get("config", {}))
                return self._json(202, {"run": run})
            if len(parts) == 4 and parts[:2] == ["api", "projects"] and parts[3] == "datasets":
                if not self.server.store.can_access(parts[2],user["id"],write=True): return self._json(404,{"error":{"code":"NOT_FOUND","message":"Project not found."}})
                query = parse_qs(parsed.query)
                filename = query.get("filename", ["upload.csv"])[0]
                profile = self.server.datasets.ingest(parts[2], filename, self._body())
                return self._json(201, {"dataset": profile.to_dict()})
            self._json(404, {"error": {"code": "NOT_FOUND", "message": "Resource not found."}})
        except PermissionError as exc:
            self._json(403, {"error":{"code":"FORBIDDEN","message":str(exc)}})
        except KeyError as exc:
            self._json(404, {"error": {"code": "NOT_FOUND", "message": f"Unknown project: {exc.args[0]}"}})
        except (ValueError, DomainError, json.JSONDecodeError) as exc:
            self._json(422, {"error": {"code": "VALIDATION_ERROR", "message": str(exc)}})
        except Exception as exc:
            self.log_error("Request failed: %s", exc)
            self._json(500, {"error": {"code": "INTERNAL_ERROR", "message": "Unexpected server error."}})

    def do_PATCH(self):
        if not self._origin_allowed(): return
        user=self._require_user()
        if user is None: return
        path=urlparse(self.path).path
        if path=="/api/admin/config":
            try:
                payload=json.loads(self._body() or b"{}")
                return self._json(200,{"config":self.server.administration.update(user,payload)})
            except PermissionError as exc: return self._json(403,{"error":{"code":"FORBIDDEN","message":str(exc)}})
            except (ValueError,json.JSONDecodeError) as exc: return self._json(422,{"error":{"code":"VALIDATION_ERROR","message":str(exc)}})
        parts = path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "projects"]:
            return self._json(404, {"error": {"code": "NOT_FOUND", "message": "Resource not found."}})
        if not self.server.store.can_access(parts[2],user["id"],write=True): return self._json(404,{"error":{"code":"NOT_FOUND","message":"Project not found."}})
        try:
            payload = json.loads(self._body())
            project = self.server.projects.rename(parts[2], payload.get("name", ""))
            self._json(200, {"project": project.to_dict()})
        except KeyError:
            self._json(404, {"error": {"code": "NOT_FOUND", "message": "Project not found."}})
        except (ValueError, DomainError, json.JSONDecodeError) as exc:
            self._json(422, {"error": {"code": "VALIDATION_ERROR", "message": str(exc)}})

    def do_DELETE(self):
        if not self._origin_allowed(): return
        user=self._require_user()
        if user is None: return
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "projects"]:
            return self._json(404, {"error": {"code": "NOT_FOUND", "message": "Resource not found."}})
        if not self.server.store.is_owner(parts[2],user["id"]): return self._json(404,{"error":{"code":"NOT_FOUND","message":"Project not found."}})
        if self.server.projects.delete(parts[2]): self._json(200, {"deleted": True})
        else: self._json(404, {"error": {"code": "NOT_FOUND", "message": "Project not found."}})

    def log_message(self, fmt, *args):
        print("[http] " + fmt % args)


def create_server(host="127.0.0.1", port=8765, data_dir=None):
    root = Path(data_dir or os.environ.get("NEURALFORGE_HOME", "~/.neuralforge")).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    store = SQLiteStore(root / "neuralforge.sqlite3")
    server = ThreadingHTTPServer((host, port), NeuralForgeHandler)
    server.daemon_threads = True
    server.store = store
    server.identity = IdentityService(store)
    server.projects = ProjectService(store)
    server.datasets = CsvDatasetService(store, root)
    server.training = LocalTrainingService(store, root)
    return server
