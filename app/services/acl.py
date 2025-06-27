import re
import os
class ACLAlreadyExists(Exception):
    pass

def add_acl_to_config(acl_name: str, backend_name: str):
    """
    Inserta una nueva ACL en el archivo haproxy.cfg antes de la primera ACL existente.

    Args:
        acl_name (str): Nombre de la ACL (dominio)
        backend_name (str): Nombre del backend a usar
    Raises:
        ACLAlreadyExists: Si ya existe una ACL con el mismo nombre
    """
    config_path = os.environ.get('HAPROXY_CFG_PATH')
    acl_line_pattern = re.compile(r'use_backend\s+.+\s+if\s+\{.*hdr\(host\).*?-i\s+' + re.escape(acl_name) + r'\s*\}')
    new_acl_line = f'use_backend {backend_name} if {{ hdr(host) -i {acl_name} }}\n'

    with open(config_path, 'r') as f:
        lines = f.readlines()

    # Verificar si ya existe la ACL
    for line in lines:
        if acl_line_pattern.search(line):
            raise ACLAlreadyExists(f"La ACL '{acl_name}' ya está definida.")

    # Buscar la primera línea de tipo use_backend (asumimos que representa una ACL)
    insert_index = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("use_backend"):
            insert_index = idx
            break

    if insert_index is not None:
        lines.insert(insert_index, new_acl_line)
    else:
        # Si no existe ninguna ACL, lo agregamos al final
        lines.append("\n" + new_acl_line)

    with open(config_path, 'w') as f:
        f.writelines(lines)


def remove_acl_from_config(acl_name: str):
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