from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.acl import create_acl, delete_acl, modify_acl

router = APIRouter()

class ACLRequest(BaseModel):
    name: str
    condition: str

@router.post("/create")
def create_acl_route(request: ACLRequest):
    success = create_acl(request.name, request.condition)
    if not success:
        raise HTTPException(status_code=400, detail="No se pudo crear la ACL")
    return {"message": "ACL creada correctamente"}

@router.delete("/delete")
def delete_acl_route(name: str):
    success = delete_acl(name)
    if not success:
        raise HTTPException(status_code=404, detail="ACL no encontrada")
    return {"message": "ACL eliminada correctamente"}

@router.put("/modify")
def modify_acl_route(name: str, new_condition: str):
    success = modify_acl(name, new_condition)
    if not success:
        raise HTTPException(status_code=404, detail="No se pudo modificar la ACL")
    return {"message": "ACL modificada correctamente"}
