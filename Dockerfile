# Utilizamos una imagen base de Python (versión 3.9 en este ejemplo)
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . .

# Exponer el puerto en el que se ejecutará la aplicación (ajusta según tu app)
EXPOSE 8000

# Comando para iniciar la aplicación (asegúrate de que "app.py" sea el entry point y defina la variable "app")
CMD ["python", "app.py"]

