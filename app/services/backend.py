import os
from typing import List


def _load_cfg():
    path = os.environ.get('HAPROXY_CFG_PATH')
    if not path:
        raise EnvironmentError("La variable de entorno HAPROXY_CFG_PATH no está definida.")
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return path, lines


def create_backend(name: str, servers: List[str]) -> bool:
    path, lines = _load_cfg()

    header = f"backend {name}"
    for line in lines:
        if line.strip().startswith('backend ') and line.strip().split()[1] == name:
            return False

    new_block = [header + "\n"]
    for srv in servers:
        new_block.append(f"    {srv}\n")
    new_block.append("\n")

    # Buscar el lugar donde insertar el backend
    insert_idx = len(lines)
    idx = insert_idx - 1

    # Ir hacia arriba hasta encontrar una línea en blanco (solo "\n")
    while idx >= 0 and lines[idx].strip() != "":
        idx -= 1
    insert_idx = idx + 1

    lines[insert_idx:insert_idx] = new_block

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    return True


def _find_backend_block(lines: List[str], name: str):
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('backend ') and line.strip().split()[1] == name:
            start = i
            break
    if start is None:
        return None, None

    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].strip().startswith('backend '):
            end = j
            break
    return start, end


def modify_backend(name: str, servers: List[str]) -> bool:
    path, lines = _load_cfg()
    loc = _find_backend_block(lines, name)
    if loc == (None, None):
        return False
    start, end = loc

    new_block = [f"backend {name}\n"]
    for srv in servers:
        new_block.append(f"    {srv}\n")
    new_block.append("\n")

    lines[start:end] = new_block
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    return True


def delete_backend(name: str) -> bool:
    path, lines = _load_cfg()
    loc = _find_backend_block(lines, name)
    if loc == (None, None):
        return False
    start, end = loc
    del lines[start:end]
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    return True
