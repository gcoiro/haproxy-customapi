FROM python:3.11-slim

WORKDIR /app

COPY docker/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY README.md .

ENV HAPROXY_CFG_PATH=/usr/local/etc/haproxy/haproxy.cfg
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
