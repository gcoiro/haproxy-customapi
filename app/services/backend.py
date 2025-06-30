import os
from typing import List

PLACEHOLDER = "########NOTHING HERE##########"


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

    insert_idx = None
    for i, line in enumerate(lines):
        if PLACEHOLDER in line:
            insert_idx = i
            break
    if insert_idx is None:
        lines.extend(new_block)
    else:
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
        stripped = lines[j].strip()
        if stripped.startswith('backend ') or PLACEHOLDER in stripped:
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
