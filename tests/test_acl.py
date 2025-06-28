import os
import shutil
import tempfile
import pytest
from unittest import mock
from app.services.acl import add_acl_to_config, ACLAlreadyExists
import logging
logger=logging.getLogger(__name__)

@pytest.fixture
def copy_test_haproxy_cfg():
    # Copia el archivo base a uno temporal
    temp_path = tempfile.NamedTemporaryFile(delete=False).name
    shutil.copy("tests/haproxy.cfg", temp_path)
    yield temp_path
    os.remove(temp_path)

def test_add_new_acl(copy_test_haproxy_cfg):
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": copy_test_haproxy_cfg}):
        add_acl_to_config("nuevo.com", "backend_nuevo")

        with open(copy_test_haproxy_cfg) as f:
            contents = f.read()
        logger.info("\n===== Resultado del haproxy.cfg temporal =====")
        logger.info(contents)
        logger.info("==============================================\n")
        assert "backend_nuevo" in contents
        assert "hdr(host) -i nuevo.com" in contents

def test_conflict_acl(copy_test_haproxy_cfg):
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": copy_test_haproxy_cfg}):
        # Primero: inserta la ACL una vez correctamente
        add_acl_to_config("example_new.com", "backend1")
        try:
            # Segundo intento: debe lanzar ACLAlreadyExists
            add_acl_to_config("example_new.com", "backend1")
        except ACLAlreadyExists:
            logger.info("✅ ACLAlreadyExists lanzada correctamente para 'example_new.com'")
            return  # éxito del test

        # Si llegamos aquí, falló porque no se lanzó la excepción
        pytest.fail("❌ No se lanzó ACLAlreadyExists en la segunda inserción")


