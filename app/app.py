from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# Configuración de la base de datos basada en Proxmox
DB_CONFIG = {
	'host': '10.3.29.20',
	'port': 33060,
	'user': 'user_gr6',
	'password': 'usuario',
	'database': 'gr6_db'
}

app.config['SQLALCHEMY_DATABASE_URI'] = (
	f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
	f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
app.config['SECRET_KEY'] = 'tu_clave_secreta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definición de modelos
class Usuario(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), unique=True, nullable=False)
	contraseña = db.Column(db.String(255), nullable=False)

class Taquilla(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	numero = db.Column(db.Integer, unique=True, nullable=False)
	estado = db.Column(db.Enum('libre', 'ocupada'), default='libre')

class Prestamo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
	taquilla_id = db.Column(db.Integer, db.ForeignKey('taquilla.id'))
	fecha_prestamo = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
	fecha_devolucion = db.Column(db.TIMESTAMP, nullable=True)

	usuario = db.relationship('Usuario', backref=db.backref('prestamos', lazy=True))
	taquilla = db.relationship('Taquilla', backref=db.backref('prestamos', lazy=True))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contraseña = request.form['contraseña']
        Usuario = Usuario.query.filter_by(nombre=nombre).first()
        if Usuario and check_password_hash(Usuario.contraseña, contraseña):
            session['Usuario_id'] = Usuario.id
            flash('Inicio de sesión con existo', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contraseña = generate_password_hash(request.form['contraseña'])
        if Usuario.query.filter_by(nombre=nombre).first():
            flash('El usuario ya existe', 'danger')
        else:
            new_user = Usuario(nombre=nombre, contraseña=contraseña)
            db.session.add(new_user)
            db.session.commit()
            flash('Registro realizado con exito, ahora inicia sesión', 'success')
            return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    Taquilla = Taquilla.query.all()
    return render_template('listar.html', Taquilla=Taquilla)

@app.route('/reservar/<int:taquilla_id>')
def reservar(taquilla_id):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    Taquilla = Taquilla.query.get(taquilla_id)
    if Taquilla and Taquilla.status == 'disponible':
        Taquilla.status = 'ocupado'
        Taquilla.usuario_id = session['usuario_id']
        db.session.commit()
        flash('Taquilla reservada con éxito', 'success')
    else:
        flash('No se puede reservar esta taquilla', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/liberar/<int:taquilla_id>')
def liberar(taquilla_id):
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    Taquilla = Taquilla.query.get(taquilla_id)
    if Taquilla and Taquilla.usuario_id == session['usuario_id']:
        Taquilla.status = 'disponible'
        Taquilla.usuario_id = None
        db.session.commit()
        flash('Taquilla liberada con éxito', 'success')
    else:
        flash('No puedes liberar esta taquilla', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
