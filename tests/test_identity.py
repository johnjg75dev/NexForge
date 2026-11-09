import hashlib,time
import pytest
from neuralforge.adapters.sqlite_store import SQLiteStore
from neuralforge.application.identity import IdentityService
from neuralforge.application.use_cases import ProjectService


def test_register_login_session_admin_and_registration_policy(tmp_path):
    store=SQLiteStore(tmp_path/"db.sqlite")
    identity=IdentityService(store)
    admin,token=identity.register("admin_user","a-long-password-123")
    assert admin["role"]=="admin"
    assert identity.authenticate(token)["id"]==admin["id"]
    user,second=identity.register("second_user","another-long-password-456")
    assert user["role"]=="user"
    logged,login_token=identity.login("ADMIN_USER","a-long-password-123")
    assert logged["id"]==admin["id"]
    assert identity.authenticate(login_token)
    identity.logout(login_token)
    assert identity.authenticate(login_token) is None
    owner_id=admin["id"]
    _,change_token=identity.login("admin_user","a-long-password-123","change-test")
    identity.change_password(owner_id,"a-long-password-123","replacement-password-789")
    assert identity.authenticate(change_token) is None
    assert identity.login("admin_user","replacement-password-789")[0]["id"]==owner_id
    store.set_global_config("allow_registration",False)
    with pytest.raises(PermissionError): identity.register("third_user","third-long-password-789")


def test_login_throttling_blocks_repeated_failures(tmp_path):
    store=SQLiteStore(tmp_path/"db.sqlite")
    identity=IdentityService(store)
    identity.register("secure_user","secure-password-123")
    for _ in range(7):
        with pytest.raises(PermissionError, match="Invalid username"):
            identity.login("secure_user","wrong-password-123","test-client")
    with pytest.raises(PermissionError, match="Too many"):
        identity.login("secure_user","wrong-password-123","test-client")
    with pytest.raises(PermissionError, match="Too many"):
        identity.login("secure_user","secure-password-123","test-client")


def test_projects_private_until_shared_and_role_enforced(tmp_path):
    store=SQLiteStore(tmp_path/"db.sqlite")
    identity=IdentityService(store)
    owner,_=identity.register("owner_user","owner-long-password-123")
    reader,_=identity.register("reader_user","reader-long-password-456")
    project=ProjectService(store).create("Private project","tabular_classification",owner_id=owner["id"])
    assert not store.can_access(project.id.value,reader["id"])
    store.share_project(project.id.value,"reader_user","viewer")
    assert store.can_access(project.id.value,reader["id"])
    assert not store.can_access(project.id.value,reader["id"],write=True)
    assert store.can_access(project.id.value,owner["id"],write=True)
    assert [p.id.value for p in store.list_for_user(reader["id"])]==[project.id.value]
