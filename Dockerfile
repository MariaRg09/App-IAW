# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que correrá Flask
EXPOSE 5000

# Comando para ejecutar servidor Gunicorn (recomendado en producción)
CMD ["gunicorn", "--chdir", "./app", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]