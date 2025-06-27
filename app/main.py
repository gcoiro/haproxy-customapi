from fastapi import FastAPI
from app.routes.acl import router as acl_router
from app.routes.backend import router as backend_router

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
