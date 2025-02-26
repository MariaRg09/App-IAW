from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# Modelo de Usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    locker = db.relationship('Locker', backref='user', uselist=False)

# Modelo de Taquilla
class Locker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    status = db.Column(db.String(20), default='disponible')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Inicio de sesión con existo', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'danger')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registro realizado con exito, ahora inicia sesión', 'success')
            return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    lockers = Locker.query.all()
    return render_template('listar.html', lockers=lockers)

@app.route('/reservar/<int:locker_id>')
def reservar(locker_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    locker = Locker.query.get(locker_id)
    if locker and locker.status == 'disponible':
        locker.status = 'ocupado'
        locker.user_id = session['user_id']
        db.session.commit()
        flash('Taquilla reservada con éxito', 'success')
    else:
        flash('No se puede reservar esta taquilla', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/liberar/<int:locker_id>')
def liberar(locker_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    locker = Locker.query.get(locker_id)
    if locker and locker.user_id == session['user_id']:
        locker.status = 'disponible'
        locker.user_id = None
        db.session.commit()
        flash('Taquilla liberada con éxito', 'success')
    else:
        flash('No puedes liberar esta taquilla', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
