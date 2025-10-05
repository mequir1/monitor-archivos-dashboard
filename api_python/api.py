import os
import socket
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Table, Column, String, DateTime, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert, select, update
from database import Base, MetaData, SessionLocal
from models import PosPrice
from schemas import PosPriceSchema, PriceFilter
from pydantic import ValidationError


app = Flask(__name__)

metadata = MetaData()

table_dpfile_pos = Table('dpfile_pos', metadata,
    Column('ip_nbr', String(255), primary_key=True),
    Column('store_nbr', Integer),
    Column('pos_nbr', String(20)),       
    Column('modification_date', DateTime),
    Column('size_bytes', Integer)
)

table_pmt_dpc = Table('pmt_dpc', metadata,
    Column('name_pmt', String(255), primary_key=True),
    Column('store_nbr', Integer),
    Column('modification_date', DateTime),
    Column('size_bytes', Integer)
)

# metadata.create_all(engine)

session = SessionLocal()

@app.route('/reportar-pmt-dpc', methods=['POST'])
def reportar_pmt_dpc():
    data = request.get_json()
    print("📥 Recibido:", data)
    if not isinstance(data, list):
        return jsonify({"error": "Se esperaba una lista de objetos JSON"}), 400

    for item in data:
        name_pmt = item['name_pmt']
        store_nbr=item['store_nbr']
        modification_date = datetime.strptime(item['modification_date'], "%Y-%m-%d %H:%M:%S.%f")
        size_bytes = item['size_bytes']
                
        if not all([name_pmt, store_nbr, modification_date, size_bytes]):
            print(f"⚠️ Datos incompletos: {item}")
            continue

    try:
        # Verificar si ya existe
        query = select(table_pmt_dpc).where(table_pmt_dpc.c.name_pmt == name_pmt)
        resultado = session.execute(query).fetchone()

        if resultado:
            # Ya existe → actualizar
            stmt = (
                update(table_pmt_dpc)
                .where(table_pmt_dpc.c.name_pmt == name_pmt)
                .values(
                    store_nbr=store_nbr,                               
                    modification_date=modification_date,
                    size_bytes=size_bytes
                )    
            )
            session.execute(stmt)
            print(f"🔄 Actualizado: {name_pmt}")
        else:
            # No existe → insertar
            stmt = insert(table_pmt_dpc).values(
                name_pmt=name_pmt,
                store_nbr=store_nbr,
                modification_date=modification_date,
                size_bytes=size_bytes
            )
            session.execute(stmt)
            print(f"🆕 Insertado: {name_pmt}")
        session.commit()
        return {'status': 'ok'}, 200
    except Exception as ex:
        print(f"❌ Error al insertar/actualizar: {ex}")
        return {'status': 'Error'}, 500
    finally:
        session.close()

    

@app.route('/reportar-dpfile-pos', methods=['POST'])
def reportar_dpfile_pos():
    data = request.get_json()
    print("📥 Recibido:", data)
    if not isinstance(data, list):
        return jsonify({"error": "Se esperaba una lista de objetos JSON"}), 400

    for item in data:
        ip_nbr = item['ip_nbr']
        store_nbr=item['store_nbr']
        pos_nbr=item['pos_nbr']
        modification_date = datetime.strptime(item['modification_date'], "%Y-%m-%d %H:%M:%S.%f")
        size_bytes = item['size_bytes']
                
        if not all([ip_nbr, store_nbr, pos_nbr, modification_date, size_bytes]):
            print(f"⚠️ Datos incompletos: {item}")
            continue

    try:
        # Verificar si ya existe
        query = select(table_dpfile_pos).where(table_dpfile_pos.c.ip_nbr == ip_nbr)
        resultado = session.execute(query).fetchone()

        if resultado:
            # Ya existe → actualizar
            stmt = (
                update(table_dpfile_pos)
                .where(table_dpfile_pos.c.ip_nbr == ip_nbr)
                .values(
                    store_nbr=store_nbr, 
                    pos_nbr=pos_nbr,                              
                    modification_date=modification_date,
                    size_bytes=size_bytes
                )    
            )
            session.execute(stmt)
            print(f"🔄 Actualizado: {ip_nbr}")
        else:
            # No existe → insertar
            stmt = insert(table_dpfile_pos).values(
                ip_nbr=ip_nbr,
                store_nbr=store_nbr,
                pos_nbr=pos_nbr,
                modification_date=modification_date,
                size_bytes=size_bytes
            )
            session.execute(stmt)
            print(f"🆕 Insertado: {ip_nbr}")
        session.commit()
    except Exception as ex:
        print(f"❌ Error al insertar/actualizar: {ex}")
    finally:
        session.close()
        
    return {'status': 'ok'}, 200

@app.route("/insert-price/", methods=["POST"])
def insert_price():
    try:
        data = PosPriceSchema(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    db = SessionLocal()
    new_record = PosPrice(**data.model_dump(exclude_unset=True))
    db.add(new_record)
    db.commit()
    db.close()
    return jsonify({"message": "Registro insertado correctamente"})

@app.route("/prices/", methods=["POST"])
def get_prices():
    try:
        filters = PriceFilter(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    db = SessionLocal()
    query = db.query(PosPrice)

    if filters.store_nbr is not None:
        query = query.filter(PosPrice.store_nbr == filters.store_nbr)
    if filters.item_nbr is not None:
        query = query.filter(PosPrice.item_nbr == filters.item_nbr)
    if filters.upc_code is not None:
        query = query.filter(PosPrice.upc_code == filters.upc_code)

    results = query.all()
    db.close()

    return jsonify([{
        "store_nbr": r.store_nbr,
        "item_nbr": r.item_nbr,
        "upc_code": r.upc_code,
        "upc_description": r.upc_description,
        "previous_base_price": float(r.previous_base_price),
        "new_base_price": float(r.new_base_price),
        "previous_customer_price": float(r.previous_customer_price),
        "new_customer_price": float(r.new_customer_price),
        "modification_date": r.modification_date.isoformat()
    } for r in results])

# Carpeta específica que quieres escanear
CARPETA_OBJETIVO = 'C:/Users/mequir1/Documents/tmp/testingPython/Files/'

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
            size = os.path.getsize(ruta_completa)
            last_modification = os.path.getmtime(ruta_completa)
            date = datetime.fromtimestamp(last_modification).strftime('%Y-%m-%d %H:%M:%S')

            archivos.append({
                'name_file': nombre_archivo,
                'size_bytes': size,
                'last_modification': date
            })

    return jsonify({'archivos': archivos})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
