from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.backend import create_backend, modify_backend, delete_backend

router = APIRouter()

class BackendRequest(BaseModel):
    name: str
    servers: List[str]

@router.post('/create-backend')
def create_backend_route(request: BackendRequest):
    success = create_backend(request.name, request.servers)
    if not success:
        raise HTTPException(status_code=400, detail='Backend ya existe')
    return {'message': 'Backend creado correctamente'}

@router.put('/modify-backend')
def modify_backend_route(request: BackendRequest):
    success = modify_backend(request.name, request.servers)
    if not success:
        raise HTTPException(status_code=404, detail='Backend no encontrado')
    return {'message': 'Backend modificado correctamente'}

@router.delete('/delete-backend')
def delete_backend_route(name: str):
    success = delete_backend(name)
    if not success:
        raise HTTPException(status_code=404, detail='Backend no encontrado')
    return {'message': 'Backend eliminado correctamente'}
