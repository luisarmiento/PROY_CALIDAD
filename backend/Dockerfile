FROM python:3.10-slim

WORKDIR /app

# Copia el requirements (está en la misma carpeta que el Dockerfile)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia TODO el contenido de la carpeta backend al contenedor
COPY . .

EXPOSE 8000

# El comando se mantiene igual porque al copiar todo, 'app' queda en la raíz de /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]