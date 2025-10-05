from flask import Flask, request
from sqlalchemy import create_engine, Table, Column, String, DateTime, Integer, MetaData
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import insert, select, update

app = Flask(__name__)

# Conexión a Azure SQL
connection_string = (
    'mssql+pyodbc://mequir1:gArAnt14@monitorfiles.database.windows.net:1433/monitorFiles'
    '?driver=ODBC+Driver+17+for+SQL+Server'
)
engine = create_engine(connection_string)
metadata = MetaData()
tabla_actualizaciones = Table('actualizaciones_archivos', metadata,
    Column('nombre', String(255), primary_key=True),
    Column('fecha_actualizacion', DateTime),
    Column('tamaño_bytes', Integer)
)

tabla_archivos = Table('archivos_db', metadata,
    Column('nombre', String(255), primary_key=True),
    Column('fecha_actualizacion', DateTime)
)

# metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

@app.route('/reportar', methods=['POST'])
def reportar():
    data = request.get_json()
    print("📥 Recibido:", data)
    nombre = data['nombre']
    fecha = datetime.strptime(data['fecha'], "%Y-%m-%d %H:%M:%S.%f")
    tamaño = data['tamaño']
    
    try:
        # Verificar si ya existe
        query = select(tabla_actualizaciones).where(tabla_actualizaciones.c.nombre == nombre)
        resultado = session.execute(query).fetchone()

        if resultado:
            # Ya existe → actualizar
            stmt = update(tabla_actualizaciones).where(tabla_actualizaciones.c.nombre == nombre).values(
                fecha_actualizacion=fecha,
                tamaño_bytes=tamaño
            )
            session.execute(stmt)
            print(f"🔄 Actualizado: {nombre}")
        else:
            # No existe → insertar
            stmt = insert(tabla_actualizaciones).values(
                nombre=nombre,
                fecha_actualizacion=fecha,
                tamaño_bytes=tamaño
            )
            session.execute(stmt)
            print(f"🆕 Insertado: {nombre}")

        session.commit()
    except Exception as ex:
        print(f"❌ Error al insertar/actualizar: {ex}")
    finally:
        session.close()

    return {'status': 'ok'}, 200


@app.route('/comparar', methods=['GET'])
def comparar():
    session = SessionLocal()
    try:
        # Obtener todos los registros de ambas tablas
        monitor_data = session.execute(select(tabla_actualizaciones)).fetchall()
        base_data = session.execute(select(tabla_archivos)).fetchall()

        # Convertir a diccionarios por nombre
        monitor_dict = {row.nombre: row.fecha_actualizacion for row in monitor_data}
        base_dict = {row.nombre: row.fecha_actualizacion for row in base_data}

        resultados = []

        # Archivos en monitor
        for nombre, fecha_monitor in monitor_dict.items():
            if nombre in base_dict:
                fecha_base = base_dict[nombre]
                if fecha_monitor > fecha_base:
                    estado = "actualizado"
                elif fecha_monitor < fecha_base:
                    estado = "No actualizado"
                else:
                    estado = "sincronizado"
            else:
                estado = "solo en pos"
            resultados.append({
                "archivo": nombre,
                "date_pos": str(fecha_monitor),
                "date_dp": str(base_dict.get(nombre)),
                "estado": estado
            })

        # Archivos solo en base
        for nombre, fecha_base in base_dict.items():
            if nombre not in monitor_dict:
                resultados.append({
                    "archivo": nombre,
                    "date_pos": None,
                    "date_dp": str(fecha_base),
                    "estado": "solo en dp"
                })

        return {"comparacion": resultados}, 200
    except Exception as ex:
        print(f"❌ Error en comparacion: {ex}")
        return {"error": str(ex)}, 500
    finally:
        session.close()


if __name__ == '__main__':
    app.run(debug=True)

