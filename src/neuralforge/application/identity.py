"""Local account/session application service; passwords never leave this boundary."""
import hashlib, hmac, secrets, time


class IdentityService:
    ITERATIONS = 310_000
    SESSION_SECONDS = 60 * 60 * 24 * 7

    def __init__(self, store): self.store = store

    def register(self, username: str, password: str):
        username = username.strip()
        if not 3 <= len(username) <= 64 or not all(c.isalnum() or c in "._-@" for c in username):
            raise ValueError("Username must be 3–64 characters and use letters, numbers, dot, dash, underscore, or @.")
        if len(password) < 12 or len(password) > 256:
            raise ValueError("Password must be between 12 and 256 characters.")
        config = self.store.get_global_config()
        if config.get("allow_registration", True) is not True:
            raise PermissionError("New account registration is disabled by the administrator.")
        if self.store.user_by_name(username): raise ValueError("That username is already registered.")
        salt=secrets.token_bytes(16)
        derived=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,self.ITERATIONS)
        encoded=f"pbkdf2_sha256${self.ITERATIONS}${salt.hex()}${derived.hex()}"
        user=self.store.register_user(username,encoded)
        return user,self._new_session(user["id"])

    def login(self, username: str, password: str, source: str = "unknown"):
        normalized=username.strip().casefold()
        subject_hash=hashlib.sha256(normalized.encode()).hexdigest()
        source_hash=hashlib.sha256(source.encode()).hexdigest()
        now=time.time()
        _,_,locked_until=self.store.login_lock_state(subject_hash,source_hash,now)
        if locked_until>now: raise PermissionError("Too many failed sign-in attempts. Try again later.")
        user=self.store.user_by_name(normalized)
        if not user or not self._verify(password,user["password_hash"]):
            locked=self.store.record_login_failure(subject_hash,source_hash,now,900,8,900)
            if locked>now: raise PermissionError("Too many failed sign-in attempts. Try again later.")
            raise PermissionError("Invalid username or password.")
        self.store.clear_login_failures(subject_hash,source_hash)
        safe={k:user[k] for k in ("id","username","role","created_at")}
        return safe,self._new_session(safe["id"])

    def change_password(self, user_id: str, current_password: str, new_password: str):
        user=self.store.get_user(user_id)
        if not user: raise KeyError(user_id)
        full=self.store.user_by_name(user["username"])
        if not self._verify(current_password,full["password_hash"]): raise PermissionError("Current password is incorrect.")
        if len(new_password)<12 or len(new_password)>256: raise ValueError("New password must be between 12 and 256 characters.")
        salt=secrets.token_bytes(16)
        derived=hashlib.pbkdf2_hmac("sha256",new_password.encode(),salt,self.ITERATIONS)
        self.store.update_password_hash(user_id,f"pbkdf2_sha256${self.ITERATIONS}${salt.hex()}${derived.hex()}")

    def authenticate(self, raw_token: str | None):
        if not raw_token: return None
        hashed=hashlib.sha256(raw_token.encode()).hexdigest()
        return self.store.session_user(hashed,time.time())

    def logout(self, raw_token: str | None):
        if raw_token: self.store.delete_session(hashlib.sha256(raw_token.encode()).hexdigest())

    def _new_session(self,user_id):
        token=secrets.token_urlsafe(48)
        self.store.create_session(hashlib.sha256(token.encode()).hexdigest(),user_id,time.time()+self.SESSION_SECONDS)
        return token

    @staticmethod
    def _verify(password,encoded):
        try:
            scheme,iterations,salt_hex,digest_hex=encoded.split("$")
            if scheme!="pbkdf2_sha256": return False
            actual=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt_hex),int(iterations)).hex()
            return hmac.compare_digest(actual,digest_hex)
        except (ValueError,TypeError): return False
