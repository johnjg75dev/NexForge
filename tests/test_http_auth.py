import json, threading, urllib.request, urllib.error
from neuralforge.http.server import create_server


def request(base,path,method="GET",payload=None,cookie=None):
    data=json.dumps(payload).encode() if payload is not None else None
    headers={"Content-Type":"application/json"} if data else {}
    if cookie: headers["Cookie"]=cookie
    req=urllib.request.Request(base+path,data=data,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req) as response: return response.status,json.loads(response.read()),response.headers
    except urllib.error.HTTPError as exc: return exc.code,json.loads(exc.read()),exc.headers


def test_http_signup_login_and_private_project_boundary(tmp_path):
    server=create_server("127.0.0.1",0,tmp_path)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f"http://127.0.0.1:{server.server_address[1]}"
    try:
        status,_,_=request(base,"/api/projects")
        assert status==401
        status,body,headers=request(base,"/api/auth/register","POST",{"username":"owner","password":"owner-password-123"})
        assert status==201 and body["user"]["role"]=="admin"
        owner_cookie=headers.get("Set-Cookie").split(";",1)[0]
        status,created,_=request(base,"/api/projects","POST",{"name":"Private","task_type":"tabular_classification"},owner_cookie)
        assert status==201
        status,_,_=request(base,"/api/auth/register","POST",{"username":"reader","password":"reader-password-456"})
        assert status==201
        status,body,headers=request(base,"/api/auth/login","POST",{"username":"reader","password":"reader-password-456"})
        reader_cookie=headers.get("Set-Cookie").split(";",1)[0]
        status,projects,_=request(base,"/api/projects",cookie=reader_cookie)
        assert status==200 and projects["projects"]==[]
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2)
