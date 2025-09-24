from flask import Flask, jsonify
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, render_template

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///archivos.db'
db = SQLAlchemy(app)

class ArchivoDB(db.Model):
    __tablename__ = 'archivos_db'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, unique=True, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, nullable=False)

# Carpeta específica que quieres escanear
CARPETA_OBJETIVO = '/Users/oscar/Documents/MisProyectos/python/mi_api_archivos/archivos/'

@app.route('/archivos-info', methods=['GET'])
def archivos_info():
    print(f"Verificando carpeta: {CARPETA_OBJETIVO}")
    if not os.path.isdir(CARPETA_OBJETIVO):
        print("Carpeta no encontrada")
        return jsonify({'error': f'La carpeta "{CARPETA_OBJETIVO}" no existe'}), 400

    archivos = []
    for nombre_archivo in os.listdir(CARPETA_OBJETIVO):
        ruta_completa = os.path.join(CARPETA_OBJETIVO, nombre_archivo)
        if os.path.isfile(ruta_completa):
            tamaño = os.path.getsize(ruta_completa)
            ultima_modificacion = os.path.getmtime(ruta_completa)
            fecha_formateada = datetime.fromtimestamp(ultima_modificacion).strftime('%Y-%m-%d %H:%M:%S')

            archivos.append({
                'nombre': nombre_archivo,
                'tamaño_bytes': tamaño,
                'ultima_modificacion': fecha_formateada
            })

    return jsonify({'archivos': archivos})


@app.route('/comparar-archivos', methods=['GET'])
def comparar_archivos():
    resultados = []

    for nombre_archivo in os.listdir(CARPETA_OBJETIVO):
        ruta_completa = os.path.join(CARPETA_OBJETIVO, nombre_archivo)
        if os.path.isfile(ruta_completa):
            fecha_archivo = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
            registro = ArchivoDB.query.filter_by(nombre=nombre_archivo).first()

            if registro:
                actualizado = fecha_archivo < registro.fecha_actualizacion
                resultados.append({
                    'archivo': nombre_archivo,
                    'fecha_archivo': fecha_archivo.strftime('%Y-%m-%d %H:%M:%S'),
                    'fecha_db': registro.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S'),
                    'requiere_actualizacion': actualizado
                })
            else:
                resultados.append({
                    'archivo': nombre_archivo,
                    'fecha_archivo': fecha_archivo.strftime('%Y-%m-%d %H:%M:%S'),
                    'fecha_db': None,
                    'requiere_actualizacion': True  # No existe en DB, se considera desactualizado
                })

    return jsonify({'comparaciones': resultados})
    	
@app.route('/tabla-archivos')
def tabla_archivos():
    comparaciones = []

    for nombre_archivo in os.listdir(CARPETA_OBJETIVO):
        ruta_completa = os.path.join(CARPETA_OBJETIVO, nombre_archivo)
        if os.path.isfile(ruta_completa):
            fecha_archivo = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
            registro = ArchivoDB.query.filter_by(nombre=nombre_archivo).first()

            if registro:
                actualizado = fecha_archivo < registro.fecha_actualizacion
                comparaciones.append({
                    'archivo': nombre_archivo,
                    'fecha_archivo': fecha_archivo.strftime('%Y-%m-%d %H:%M:%S'),
                    'fecha_db': registro.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S'),
                    'estado': '✅ Actualizado' if not actualizado else '⚠️ Desactualizado'
                })
            else:
                comparaciones.append({
                    'archivo': nombre_archivo,
                    'fecha_archivo': fecha_archivo.strftime('%Y-%m-%d %H:%M:%S'),
                    'fecha_db': 'No registrado',
                    'estado': '❌ No registrado'
                })

    return render_template('tabla.html', comparaciones=comparaciones)

if __name__ == '__main__':
    app.run(debug=True)
