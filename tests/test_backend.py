import os
import shutil
import tempfile
from unittest import mock

from app.services.backend import create_backend, modify_backend, delete_backend


def temp_cfg_path():
    temp_path = tempfile.NamedTemporaryFile(delete=False).name
    shutil.copy("tests/haproxy.cfg", temp_path)
    return temp_path


def read_file(path):
    with open(path) as f:
        return f.read()


def test_create_backend():
    cfg = temp_cfg_path()
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": cfg}):
        create_backend("backend_new", ["server srv1 1.1.1.1:80 check"])
        contents = read_file(cfg)
        assert "backend backend_new" in contents
        assert "server srv1 1.1.1.1:80 check" in contents
    os.remove(cfg)


def test_modify_backend():
    cfg = temp_cfg_path()
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": cfg}):
        create_backend("to_mod", ["server old 1.1.1.1:80"])
        modify_backend("to_mod", ["server new 2.2.2.2:80"])
        contents = read_file(cfg)
        assert "server new 2.2.2.2:80" in contents
        assert "server old 1.1.1.1:80" not in contents
    os.remove(cfg)


def test_delete_backend():
    cfg = temp_cfg_path()
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": cfg}):
        create_backend("to_del", ["server s 1.1.1.1:80"])
        delete_backend("to_del")
        contents = read_file(cfg)
        assert "backend to_del" not in contents
    os.remove(cfg)
