FROM python:3.10-slim
WORKDIR /app
#   Se copia requirements desde la misma carpeta donde está el Dockerfile
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt
# Se Copia el contenido de la carpeta app
COPY ./app ./app 
EXPOSE 8000
# El comando de inicio también cambia la ruta
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]