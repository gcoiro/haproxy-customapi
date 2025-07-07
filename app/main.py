from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.routes.acl import router as acl_router
from app.routes.backend import router as backend_router
from app.services.acl import (
    ACLAlreadyExists,
    create_acl,
    delete_acl,
    modify_acl,
)
from app.services.backend import (
    create_backend,
    delete_backend,
    modify_backend,
)


class ACLRequest(BaseModel):
    name: str
    backend: str


class BackendRequest(BaseModel):
    name: str
    servers: List[str]

app = FastAPI(
    title="HAProxy API",
    description="API para gestionar ACLs y Backends en HAProxy",
    version="1.0.0"
)

# Registrar routers
app.include_router(acl_router, prefix="/api/acl", tags=["ACL"])
app.include_router(backend_router, prefix="/api/backend", tags=["Backend"])

# Ruta básica para pruebas
@app.get("/")
def read_root():
    return {"message": "HAProxy API está corriendo"}


@app.post("/acl/create")
def create_acl_endpoint(request: ACLRequest):
    try:
        create_acl(request.name, request.backend)
    except ACLAlreadyExists:
        raise HTTPException(status_code=400, detail="ACL ya existe")
    return {"message": "ACL creada correctamente"}


@app.put("/acl/modify")
def modify_acl_endpoint(old_name: str, new_name: str):
    try:
        modify_acl(old_name, new_name)
    except ValueError:
        raise HTTPException(status_code=404, detail="ACL no encontrada")
    return {"message": "ACL modificada correctamente"}


@app.delete("/acl/delete")
def delete_acl_endpoint(name: str):
    delete_acl(name)
    return {"message": "ACL eliminada correctamente"}


@app.post("/backend/create")
def create_backend_endpoint(request: BackendRequest):
    if not create_backend(request.name, request.servers):
        raise HTTPException(status_code=400, detail="Backend ya existe")
    return {"message": "Backend creado correctamente"}


@app.put("/backend/modify")
def modify_backend_endpoint(request: BackendRequest):
    if not modify_backend(request.name, request.servers):
        raise HTTPException(status_code=404, detail="Backend no encontrado")
    return {"message": "Backend modificado correctamente"}


@app.delete("/backend/delete")
def delete_backend_endpoint(name: str):
    if not delete_backend(name):
        raise HTTPException(status_code=404, detail="Backend no encontrado")
    return {"message": "Backend eliminado correctamente"}
