# App-IAW
Este es un repositorio para la aplicación de IAW que es Préstamo Taquillas.

# Introducción
El sistema de Préstamo de Taquillas es una aplicación web desarrollada con Flask y SQLAlchemy que permite a los usuarios gestionar el uso de taquillas de manera eficiente. Su propósito es facilitar la reserva y liberación de taquillas dentro de una institución, como un gimnasio, una escuela o una empresa, garantizando un control adecuado sobre su disponibilidad.

## Funcionalidad

La aplicación permite a los usuarios:

🔹 **Funcionalidad**  
- 🔑 **Inicio de sesión** y registro de usuarios  
- 🔒 **Reserva de taquillas**, cambiando su estado a "ocupado". 
- 🔓 **Liberación de taquillas**, permitiendo su uso por otro usuario. 
- 📊 **Visualización del estado de taquillas**  
- **Cerrar sesión** para garantizar la seguridad de la cuenta.

# Desarrollo de la aplicación

## Requisitos

1. Tener Docker instalado.
2. Tener un contendor con la imagen MYSQL.
3. Tener [Visual Studio Code](https://code.visualstudio.com/download) instalado.

Adjunto una [guía de Docker y MySQL](Documentos/DockerYMysql.md) para hacer los pasos en caso de que no lo tengais. 

## Pasos

### *Paso 1: Crear directorio, entorno virtual e instalar paquetes necesarios.*

1. Creamos un directorio donde estará el entorno virtual y todo lo que tiene que ver con la aplicación, en nuestro caso se llamará **flask_mysql_app**.
```bash
$ mkdir flask_mysql_app
```
2. Creamos un entorno virtual llamado ```venv```:
```bash
$ python3 -m venv taquillas-env
```
3. Activamos el entorno (comando en Linux):
```bash
$ source taquillas-env/bin/activate
```
4. Instalamos flask, pymysql, werkzeug y jinja2:
```bash
(taquillas-env)$ pip install flask pymysql 
```
***NOTA**: Al ejecutar este comando se instala flask, pymysql, Werkzeug,Jinja2, itsdangerous, click, blinker y MarkupSafe por predeterminado.*

O bien podemos instalar los paquetes que hay dentro del archivo [requirements.txt](requirements.txt).
```bash
(taquillas-env)$ pip install -r requirements.txt
```
### *Paso 2: Configurar base de datos a utilizar*

Una vez creado el entorno y las librerías que usaremos, debemos definir la conexión de la base de datos. Para ello, hacemos lo sigueinte:

1. Entramos en el contenedor con imagen **mysql**.
```bash
$ docker exec -it mysql bash
```
2. Creamos un archivo ```config.py``` donde estará definida la conexión.
```bash
$ nano config.py
```
3. Contenido del archivo **config.py**.
```bash
DB_CONFIG= {
    'host': '10.3.29.20',
    'port': 33060,
    'user': 'user_gr6',
    'password': 'usuario',
    'database': 'gr6_db'
}
```

***NOTA**: Os proporciono lo que debe contener el archivo [config.py](app/config.py)*

3. Creamos un archivo para comprobar la conectividad de la base de datos llamado **test_db.py**.
```python
import pymysql
from config import DB_CONFIG

def test_connection():
    """ Prueba la conexión con la base de datos MySQL """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print(f"Conexión exitosa a la base de datos: {db_name[0]}")
        conn.close()
    except pymysql.MySQLError as e:
        print(f"Error al conectar con MySQL: {e}")

if __name__ == "__main__":
    test_connection()
```
4. Ejecutamos el script test_db.py para probar la conexión.
```bash
$ python test_db.py
```
5. Accedemos a la base de datos proporcionada utilizando los datos del archivo **config.py**.
```bash
$ mysql -h 10.3.29.20 -P 33060 -u user_gr6 -p
```
5. 1. Utilizamos la base de datos creada anteriormente.
```mysql
mysql> USE gr6_db;
```
5. 2.  Creamos las tablas que la aplicación va a utilizar.
```mysql

mysql> CREATE TABLE usuarios (
     > id INT AUTO_INCREMENT PRIMARY KEY,
     > nombre VARCHAR(100) NOT NULL,
     > contraseña VARCHAR(255) NOT NULL
     > );

mysql> CREATE TABLE taquillas (
     > id INT AUTO_INCREMENT PRIMARY KEY,
     > numero INT UNIQUE NOT NULL,
     > estado ENUM('libre', 'ocupada') DEFAULT 'libre'
     > );

mysql> CREATE TABLE prestamos (
     > id INT AUTO_INCREMENT PRIMARY KEY,
     > usuario_id INT,
     > taquilla_id INT,
     > fecha_prestamo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     > fecha_devolucion TIMESTAMP NULL,
     > FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
     > FOREIGN KEY (taquilla_id) REFERENCES taquillas(id)
     > );

```
**NOTA**: Se encuentran en el archivo [db_init.sql](app/db_init.sql).

### *Paso 3: Crear las Rutas en Flask*

A continuación, desarrollamos las rutas de la aplicación con Flask y Python. Para ello, debemos crear un archivo llamado ```app.py``` que contendrá todas las rutas.


```python
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Taquilla, Prestamo

app = Flask(__name__)
app.config.from_pyfile("config.py")

# Configuración de la base de datos basada en Proxmox
DB_CONFIG = {
    "host": "10.3.29.20",
    "port": 33060,
    "user": "user_gr6",
    "password": "usuario",
    "database": "gr6_db",
}

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
app.config["SECRET_KEY"] = "tu_clave_secreta"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Ahora sí inicializamos SQLAlchemy
db.init_app(app)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form["nombre"]
        contraseña = request.form["contraseña"]
        if not nombre or not contraseña:
            flash("Faltan datos en el formulario", "danger")
            return redirect(url_for("login"))

        usuario = Usuario.query.filter_by(nombre=nombre).first()  # Cambié 'usuario' por 'Usuario'
        if Usuario and check_password_hash(Usuario.contraseña, contraseña):
            session["usuario_id"] = Usuario.id
            flash("Inicio de sesión con éxito", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")
    return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        contraseña = generate_password_hash(request.form["contraseña"])

        if Usuario.query.filter_by(nombre=nombre).first():
            flash("El usuario ya existe", "danger")
        else:
            new_user = Usuario(nombre=nombre, contraseña=contraseña)
            db.session.add(new_user)
            db.session.commit()
            flash("Registro realizado con exito, ahora inicia sesión", "success")
            return redirect(url_for("login"))
    return render_template("registro.html")


@app.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for("login"))
    Taquilla = Taquilla.query.all()
    return render_template("listar.html", Taquilla=Taquilla)


@app.route("/reservar/<int:taquilla_id>")
def reservar(taquilla_id):
    if "usuario_id" not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for("login"))
    Taquilla = Taquilla.query.get(taquilla_id)
    if Taquilla and Taquilla.status == "disponible":
        Taquilla.status = "ocupado"
        Taquilla.usuario_id = session["usuario_id"]
        db.session.commit()
        flash("Taquilla reservada con éxito", "success")
    else:
        flash("No se puede reservar esta taquilla", "danger")
    return redirect(url_for("dashboard"))


@app.route("/liberar/<int:taquilla_id>")
def liberar(taquilla_id):
    if "usuario_id" not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for("login"))
    Taquilla = Taquilla.query.get(taquilla_id)
    if Taquilla and Taquilla.usuario_id == session["usuario_id"]:
        Taquilla.status = "disponible"
        Taquilla.usuario_id = None
        db.session.commit()
        flash("Taquilla liberada con éxito", "success")
    else:
        flash("No puedes liberar esta taquilla", "danger")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    flash("Has cerrado sesión", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

```
***NOTA:** Podemos encontrar el código COMPLETO en [app.py](app/app.py).*

### Paso 4: Configurar docker-compose.yml*

Para este paso, crearemos un archivo llamado [```compose.yml```](compose.yml)en el cual se define cómo se ejecutarán los contenedores de la base de datos y de Flask.

Este archivo contendrá lo siguiente:
```yaml
services:
  db:
    image: mysql:8.0-debian
    container_name: gr6_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: usuario
      MYSQL_DATABASE: gr6_db
      MYSQL_USER: user_gr6
      MYSQL_PASSWORD: usuario
    ports:
      - "33070:33060"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./app/db_init.sql:/docker-entrypoint-initdb.d/db_init.sql

  flask-app:
    build: .
    container_name: flask_lockers
    restart: always
    depends_on:
      - db
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=10.3.29.20
      - DB_PORT=33060
      - DB_USER=user_gr6
      - DB_PASSWORD=usuario
      - DB_NAME=gr6_db
    env_file:
      - taquillas-env

volumes:
  mysql_data:
```
## Despliegue de la aplicación en Docker


Ahora que tenemos los archivos listos, seguimos los siguientes pasos:

### *Paso 1: Clonación del repositorio con los archivos*
Hacemos una clonación del repositorio donde está la aplicación y los archivos necesarios.
```bash
$ git clone https://github.com/MariaRg09/App-IAW.git
```
### *Paso 2. Accede a la carpeta del repositorio.*
Ahora accedemos al directorio del repositorio, en este caso **App-IAW**.
```bash
$ cd App-IAW
```
### *Paso 3: Crear Dockerfile.*

Una vez dentro del directorio, creamos un **Dockerfile**. Este archivo define cómo se construirá el contenedor para la aplicación, por lo que debe estar en el mismo directorio que **app.py**.

El [```Dockerfile```](Dockerfile) contendrá lo siguiente:
```Dockerfile
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
```
### *Paso 4: Construir la imagen Docker.*

Realizado los pasos anteriores, vamos a construir la imagen. Para ello, es necesario irnos a la consola ya con la ruta de la aplicaión para lanzar el siguiente comando  ```docker build -t nombre_de_usuario_de_github/nombre_del_repositorio .``` , en este caso sería asi:

```bash
$ docker build -t alvarofdz/app-iaw .
```
### Paso 5: Publicación en docker hub

Lo primero que hay que hacer es crear una cuenta en https://hub.docker.com. Una vez la tengas, en la consola escribe el siguiente comando para iniciar sesión.

```bash
$ docker login
```

Luego, utilizamos el comando docker push para subir la imagen. La sintasis del comando es ```docker push nombre_de_usuario_de_Github/nombre_del_repositorio```. Por ejemplo, en nuestro caso sería así: 

```bash 
$ docker push alvarofdz/app-iaw
```
El proceso puede durar unos instantes hasta que complete.

Cuando haya terminado el proceso, puedes ver en la página de [hub.docker.com](https://hub.docker.com) que tu imagen acaba de ser publicada.

## Despliegue de la aplicación en PyhtonAnywhere

Para poder desplegar la aplicación en PythonAnywhere, creamos una cuenta en la pagina web de [PyhtonAnywhere](https://www.pythonanywhere.com) y vamos a usar el **Beginner** que es gratuito.


### *Creación de una nueva aplicación web*

En el apartado **Web** le damos a *Añadir una nueva aplicación web*.

Luego, nos saldrá *Selecciona un framework web de Python* elegimos la opción de ```Flask```.

Después, tendremos que *Elegir una version de Python*. Escogeis la que querais pero es mejor la versión ```Python 3.10``` al ser la más reciente en la lista.

A continuación, tendremos que guardarla en una **ruta**. Aquí, elegiremos una ruta válida para  la aplicación con el extensión ```.py```

***NOTA:** Si la ruta ya existe, el contenido será reescrito con la de la nueva app.*

### *Despliegue de nuestra aplicación*

En la pestaña **Consoles** podemos abrir consolas con las posibles consolas python, bash o  mysql. 

Vamos a abrir una consola ```bash``` para comenzar el despliegue. Una vez dentro, seguimos esto pasos.

### *Paso 1: clonar nuestro repositorio*

Primero, es importante que copiemos el **enlace HTTP** del repositorio de GitHub para realizar el git clone.

```bash
$ git clone https://github.com/MariaRg09/App-IAW.git
```

### *Paso 2: Configurar el entorno virtual*

Una vez clonado el repositorio donde está todo, accedemos a el y creamos un entorno virtual llamado env-taquillas.
```bash
$ python3.10 -m venv env-taquillas
```
Activamos el entorno.

```bash
$ source env-taquillas/bin/activate
```

E instalamos las librerías y módulos que harán falta a traves del requirement del repositorio.

```bash
(env-taquillas)
$ pip install -r requirements.txt
```

### *Paso 3:Configurar el archivo WSGI*

PythonAnywhere utiliza un archivo WSGI para arrancar la aplicación. Debemos editarlo para apuntar a nuestra aplicación.

En la pestaña **Web** en la sección Code, editamos los apartados de **Source Code** y **Working directory**. 

En **Source Code** tiene que estar la ruta donde se encuentra la aplicacion, es decir, ruta/directorio/app.py y en **Working Directory** la ruta del directorio donde está la aplicacion, es decir, /ruta/directorio_de_la_aplicacion.

En **WSGI configuration file** tiene que estar definido el directorio donde se encuentra nuestra aplicación. Para ello, editamos la línea:

```python
from flask_app import app as application
```
En nuestro caso cambiamos el nombre de “flask_app” por “app”.

### *Paso 4: Conectar a la base de dats*

En la pestaña **Databases** del dashboard, vamos a crear una base de datos mysql.
 
Antes, introducimos una contraseña para iniciar un servidor MySQL.

Una vez que hemos iniciado el servidor MySLQ, podremos crear la base de datos.

### *Paso 5: Verificar el despliegue*

Para visualizar el despliegue de la aplicación, tendremos que poner en el navegador ```https://username.pythonanywhere.com```, en mi caso:
```html
https://aferesc.pythonanywhere.com/
```