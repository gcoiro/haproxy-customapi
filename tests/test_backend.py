import os
import shutil
import tempfile
import pytest
from unittest import mock
from app.services.backend import create_backend, modify_backend, delete_backend
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def copy_test_haproxy_cfg():
    temp_path = tempfile.NamedTemporaryFile(delete=False).name
    shutil.copy("tests/haproxy.cfg", temp_path)
    yield temp_path
    os.remove(temp_path)


def test_create_backend(copy_test_haproxy_cfg):
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": copy_test_haproxy_cfg}):
        create_backend("backend_new", ["server srv1 1.1.1.1:80 check"])

        with open(copy_test_haproxy_cfg) as f:
            contents = f.read()
        logger.info("\n===== Resultado del haproxy.cfg tras crear backend =====")
        logger.info(contents)
        logger.info("==============================================\n")

        assert "backend backend_new" in contents
        assert "server srv1 1.1.1.1:80 check" in contents


def test_modify_backend(copy_test_haproxy_cfg):
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": copy_test_haproxy_cfg}):
        create_backend("to_mod", ["server old 1.1.1.1:80"])
        modify_backend("to_mod", ["server new 2.2.2.2:80"])

        with open(copy_test_haproxy_cfg) as f:
            contents = f.read()
        logger.info("\n===== Resultado del haproxy.cfg tras modificar backend =====")
        logger.info(contents)
        logger.info("==============================================\n")

        assert "server new 2.2.2.2:80" in contents
        assert "server old 1.1.1.1:80" not in contents


def test_delete_backend(copy_test_haproxy_cfg):
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": copy_test_haproxy_cfg}):
        create_backend("to_del", ["server s 1.1.1.1:80"])
        delete_backend("to_del")

        with open(copy_test_haproxy_cfg) as f:
            contents = f.read()
        logger.info("\n===== Resultado del haproxy.cfg tras eliminar backend =====")
        logger.info(contents)
        logger.info("==============================================\n")

        assert "backend to_del" not in contents
