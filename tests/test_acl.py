import os
import shutil
import tempfile
import pytest
from unittest import mock
from app.services.acl import create_acl,modify_acl,delete_acl,ACLAlreadyExists
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
        create_acl("nuevo.com", "backend_nuevo")

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
        create_acl("example_new.com", "backend1")
        try:
            # Segundo intento: debe lanzar ACLAlreadyExists
            create_acl("example_new.com", "backend1")
        except ACLAlreadyExists:
            logger.info("✅ ACLAlreadyExists lanzada correctamente para 'example_new.com'")
            return  # éxito del test

        # Si llegamos aquí, falló porque no se lanzó la excepción
        pytest.fail("❌ No se lanzó ACLAlreadyExists en la segunda inserción")

def test_modify_existing_acl(copy_test_haproxy_cfg):
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": copy_test_haproxy_cfg}):
        # Crear ACL inicial
        create_acl("old.com", "backend_old")
        # Modificar la ACL
        modify_acl("old.com", "new.com")

        with open(copy_test_haproxy_cfg) as f:
            contents = f.read()
        logger.info("\n===== Resultado del haproxy.cfg modificado =====")
        logger.info(contents)
        logger.info("==============================================\n")

        assert "hdr(host) -i new.com" in contents
        assert "hdr(host) -i old.com" not in contents

def test_modify_acl_not_found(copy_test_haproxy_cfg):
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": copy_test_haproxy_cfg}):
        try:
            modify_acl("nonexistent.com", "new.com")
        except ValueError as e:
            logger.info(f"✅ Se lanzó correctamente ValueError: {e}")
            return
        pytest.fail("❌ No se lanzó ValueError al intentar modificar una ACL inexistente")

def test_modify_only_target_acl(copy_test_haproxy_cfg):
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": copy_test_haproxy_cfg}):
        # Crear dos ACLs distintas
        create_acl("target.com", "backend_target")
        create_acl("other.com", "backend_other")

        modify_acl("target.com", "updated.com")

        with open(copy_test_haproxy_cfg) as f:
            contents = f.read()
        logger.info("\n===== Validando que solo se modificó la ACL correcta =====")
        logger.info(contents)
        logger.info("==============================================\n")

        assert "hdr(host) -i updated.com" in contents
        assert "hdr(host) -i target.com" not in contents
        assert "hdr(host) -i other.com" in contents

def test_delete_acl(copy_test_haproxy_cfg):
    with mock.patch.dict(os.environ, {"HAPROXY_CFG_PATH": copy_test_haproxy_cfg}):
        # Primero: agregamos dos ACLs al archivo
        create_acl("delete.com", "backend_delete")
        create_acl("keep.com", "backend_keep")

        # Luego eliminamos la ACL "delete.com"
        delete_acl("delete.com")

        with open(copy_test_haproxy_cfg) as f:
            contents = f.read()
        logger.info("\n===== Resultado del haproxy.cfg tras eliminar ACL =====")
        logger.info(contents)
        logger.info("==============================================\n")

        # Validamos que la ACL eliminada no está y la otra sí
        assert "hdr(host) -i delete.com" not in contents
        assert "backend_delete" not in contents
        assert "hdr(host) -i keep.com" in contents
        assert "backend_keep" in contents