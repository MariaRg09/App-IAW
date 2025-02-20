# MYSQL con Docker
Este documento explica cómo desplegar un contenedor de MySQL utilizando Docker de manera genérica.

# Requisitos
Descargar Docker si no lo tienes desde el [sitio oficial de Docker](http://docker.com/products/docker-desktop/ )

## Pasos para crear un contenedor MySQL

## 1. Descargar la imagen de MySQL
Ejecuta el siguiente comando para obtener la imagen oficial de MySQL:
$ docker pull mysql:latest

## 2. Crear y ejecutar el contenedor de MySQL
Ejecuta un contenedor en segundo plano con el nombre 'mysql', montando un volumen y exponiendo el puerto 33060:

$ docker run -dit --name mysql -v mysql-data:/var/lib/mysql -p 33060:3306 mysql:latest

## 3. Verificar que el contenedor esté corriendo
$ docker ps

## 4. Iniciar el servidor MySQL en modo seguro
$ docker exec -it mysql mysqld_safe & 
o
$ docker exec -it mysql bash
$$ mysqld_safe &
## 5. Acceder a la consola de MySQL como usuario root
$ docker exec -it mysql mysql -uroot -p
o
$ docker exec -it mysql bash
$$ mysqld_safe &
$$ mysql -uroot -p

## 6. Apagar el servidor MySQL de forma segura
$ docker exec -it mysql mysqladmin -uroot -p shutdown

