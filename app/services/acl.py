import re
import os
class ACLAlreadyExists(Exception):
    pass

def create_acl(acl_name: str, backend_name: str):
    """
    Inserta una nueva ACL en el archivo haproxy.cfg antes de la primera ACL existente.

    Args:
        acl_name (str): Nombre de la ACL (dominio)
        backend_name (str): Nombre del backend a usar
    Raises:
        ACLAlreadyExists: Si ya existe una ACL con el mismo nombre
    """
    config_path = os.environ.get('HAPROXY_CFG_PATH')
    if not config_path:
        raise EnvironmentError("La variable de entorno HAPROXY_CFG_PATH no está definida.")

    acl_line_pattern = re.compile(r'use_backend\s+.+\s+if\s+\{.*hdr\(host\).*?-i\s+' + re.escape(acl_name) + r'\s*\}')

    with open(config_path, 'r') as f:
        lines = f.readlines()

    # Verificar si ya existe la ACL
    for line in lines:
        if acl_line_pattern.search(line):
            raise ACLAlreadyExists(f"La ACL '{acl_name}' ya está definida.")

    # Buscar la primera línea use_backend y su indentación
    insert_index = None
    indentation = ''
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("use_backend"):
            insert_index = idx
            indentation = line[:len(line) - len(stripped)]
            break

    new_acl_line = f'{indentation}use_backend {backend_name} if {{ hdr(host) -i {acl_name} }}\n'

    if insert_index is not None:
        lines.insert(insert_index, new_acl_line)
    else:
        # Si no existe ninguna ACL, lo agregamos al final sin indentación
        lines.append("\n" + new_acl_line)

    with open(config_path, 'w') as f:
        f.writelines(lines)

def modify_acl(old_acl: str, new_acl: str):
    config_path = os.environ.get('HAPROXY_CFG_PATH')
    if not config_path:
        raise EnvironmentError("La variable de entorno HAPROXY_CFG_PATH no está definida.")
    """
    Modifica el nombre de una ACL en el archivo haproxy.cfg.

    Args:
        old_acl (str): Nombre actual de la ACL (dominio).
        new_acl (str): Nuevo nombre de la ACL (dominio).

    Raises:
        ValueError: Si la ACL no se encuentra.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pattern = re.compile(rf'^(.*use_backend\s+\S+\s+if\s+\{{\s*hdr\(host\)\s+-i\s+){re.escape(old_acl)}(\s*\}}.*)$')

    found = False
    for idx, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            lines[idx] = f"{match.group(1)}{new_acl}{match.group(2)}\n"
            found = True
            break

    if not found:
        raise ValueError(f"ACL con nombre '{old_acl}' no encontrada en {config_path}.")

    with open(config_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

def delete_acl(acl_name: str):
    """
    Elimina una ACL del archivo haproxy.cfg.

    Args:
        acl_name (str): Nombre de la ACL a eliminar
    """
    config_path = os.environ.get('HAPROXY_CFG_PATH')
    acl_line_pattern = re.compile(r'use_backend\s+.+\s+if\s+\{.*hdr\(host\).*?-i\s+' + re.escape(acl_name) + r'\s*\}')

    with open(config_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        # Skip lines matching the ACL pattern (i.e., remove them)
        if not acl_line_pattern.search(line):
            new_lines.append(line)

    with open(config_path, 'w') as f:
        f.writelines(new_lines)