# MYSQL con Docker
Este documento explica cómo desplegar un contenedor de MySQL utilizando Docker de manera genérica.

# Requisitos
Descargar Docker si no lo tienes desde el [sitio oficial de Docker](http://docker.com/products/docker-desktop/ )

## Pasos para crear un contenedor MySQL

## 1. Descargar la imagen de MySQL
Ejecuta el siguiente comando para obtener la imagen oficial de MySQL:
```
$ docker pull mysql:latest
```
## 2. Crear y ejecutar el contenedor de MySQL
Ejecuta un contenedor en segundo plano con el nombre 'mysql', montando un volumen y exponiendo el puerto 33060:
```bash
$ docker run -dit --name mysql -v mysql-data:/var/lib/mysql -p 33060:3306 mysql:latest
```

## 3. Verificar que el contenedor esta corriendo
Comprobamos que están funcionando:
```bash
$ docker ps
```
## 4. Iniciar el servidor MySQL en modo seguro
Para iniciar el servidor MySQL en modo seguro, ejecutamos:
```bash
$ docker exec -it mysql mysqld_safe &
```
O bien:
```bash
$ docker exec -it mysql bash

$ mysqld_safe &
```
**NOTA**: No todas las imagenes de MySQL incluyen **mysqld_safe**.

## 5. Acceder a la consola de MySQL como usuario root
Para acceder a la consola de MySQL como usuario root, podemos usar lo siguiente: 
```bash
$ docker exec -it mysql mysql -uroot -p
```
O si prefieres entrar al contenedor y luego ejecutar MySQL:

```bash
$ docker exec -it mysql bash

$ mysqld_safe &

$ mysql -uroot -p
```

**NOTA**: La contraseña del usuario **root** es 'usuario'. 

## 6. Apagar el servidor MySQL de forma segura
Para apagar el servidor MySQL de forma segura:
```bash
$ docker exec -it mysql mysqladmin -uroot -p shutdown
```
