from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)

class Taquilla(db.Model):
    __tablename__ = 'taquillas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    estado = db.Column(db.Enum('libre', 'ocupada', name='estado_taquilla'), default='libre')

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    taquilla_id = db.Column(db.Integer, db.ForeignKey('taquillas.id'), nullable=False)
    fecha_prestamo = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_devolucion = db.Column(db.DateTime, nullable=True)
    usuario = db.relationship('Usuario', backref='prestamos')
    taquilla = db.relationship('Taquilla', backref='prestamos')