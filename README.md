# haproxy-customapi

API Customizada de HAPROXY utilizando FastAPI. Este proyecto expone rutas para administrar ACLs y backends dentro de un archivo `haproxy.cfg`.

## Tests

Para ejecutar las pruebas utiliza:

```bash
PYTHONPATH=. pytest -q
```

## Docker

Se provee un `Dockerfile` en la carpeta `docker/`.

Construir la imagen:

```bash
docker build -t haproxy-customapi -f docker/Dockerfile .
```

Ejecutar el contenedor:

```bash
docker run -p 8000:8000 haproxy-customapi
```

## Kubernetes

Dentro de la carpeta `k8s/` se incluyen los manifiestos básicos para desplegar la aplicación.

Aplicar el deployment y service:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

El servicio expone el puerto `8000` dentro del clúster (tipo `ClusterIP`).
