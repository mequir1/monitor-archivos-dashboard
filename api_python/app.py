import os
#import socket
from datetime import datetime
from flask import Flask, request, jsonify
from database import SessionLocal
from sqlalchemy import select, and_
from models import PosPrice, DpFilePos, PmtDpc
from models import table_dpfile_pos, table_pmt_dpc, table_promos_update_pos, table_promos_update_store
from schemas import PosPriceSchema, PriceFilter, DpfilePosSchema, PmtDpcSchema, PromoFilter
from pydantic import ValidationError

app = Flask(__name__)

@app.route('/reportar-pmt-dpc', methods=['POST'])
def reportar_pmt_dpc():
    data_list = request.get_json()
    print("📥 Recibido:", data_list)
    
    if not isinstance(data_list, list):
        return jsonify({"error": "Se esperaba una lista de objetos JSON"}), 400
    
    db = SessionLocal()
    
    for item in data_list:
        try:
            data = PmtDpcSchema(**item)
        except ValidationError as e:
            print(f"❌ Error de validación: {e}")  
        
        try:
            # Verificar si el registro ya existe
            existing = db.query(PmtDpc).filter_by(
                name_pmt=data.name_pmt
            ).first()
            if existing:
            # Actualizar campos
                existing.name_pmt = data.name_pmt
                existing.store_nbr = data.store_nbr
                existing.modification_date = data.modification_date
                existing.size_bytes = data.size_bytes
                db.commit()
                message = "Registro actualizado correctamente"
            else:
                # Insertar nuevo registro
                new_record = PmtDpc(**data.model_dump())
                db.add(new_record)
                db.commit()
                message = "Registro insertado correctamente"
            return jsonify({"message": message}), 200
    
        except Exception as ex:
            db.rollback()
            return jsonify({"❌ Error al insertar/actualizar": str(ex)}), 500
        finally:
            db.close()
    

@app.route('/reportar-dpfile-pos', methods=['POST'])
def reportar_dpfile_pos():    
    data_list = request.get_json()
    print("📥 Recibido:", data_list)

    if not isinstance(data_list, list):
        return jsonify({"error": "Se esperaba una lista de objetos JSON"}), 400

    db = SessionLocal()

    for item in data_list:
        try:
            data = DpfilePosSchema(**item)
        except ValidationError as e:
            print(f"❌ Error de validación: {e}")  
        try:
            # Verificar si el registro ya existe
            existing = db.query(DpFilePos).filter_by(
                store_nbr=data.store_nbr,
                pos_nbr=data.pos_nbr
        ).first()
            if existing:
             # Actualizar campos
                existing.store_nbr = data.store_nbr
                existing.pos_nbr= data.pos_nbr
                existing.ip_nbr = data.ip_nbr
                existing.modification_date = data.modification_date
                existing.size_bytes = data.size_bytes
                db.commit()
                message = "Registro actualizado correctamente"
            else:
                # Insertar nuevo registro
                new_record = DpFilePos(**data.model_dump())
                db.add(new_record)
                db.commit()
                message = "Registro insertado correctamente"
            return jsonify({"message": message}), 200
    
        except Exception as ex:
            db.rollback()
            return jsonify({"❌ Error al insertar/actualizar": str(ex)}), 500
        finally:
            db.close()
    
    
    
@app.route("/insert-price/", methods=["POST"])
def insert_price():
    try:
        data = PosPriceSchema(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    db = SessionLocal()

    try:
        # Verificar si el registro ya existe
        existing = db.query(PosPrice).filter_by(
            store_nbr=data.store_nbr,
            item_nbr=data.item_nbr,
            upc_code=data.upc_code
        ).first()

        if existing:
            # Actualizar campos
            existing.upc_description = data.upc_description
            existing.previous_base_price = data.previous_base_price
            existing.new_base_price = data.new_base_price
            existing.previous_customer_price = data.previous_customer_price
            existing.new_customer_price = data.new_customer_price
            existing.modification_date = data.modification_date
            db.commit()
            message = "Registro actualizado correctamente"
        else:
            # Insertar nuevo registro
            new_record = PosPrice(**data.model_dump())
            db.add(new_record)
            db.commit()
            message = "Registro insertado correctamente"

        return jsonify({"message": message}), 200
        
    except Exception as ex:
        db.rollback()
        return jsonify({"error": str(ex)}), 500
    finally:
        db.close()
       

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
    

@app.route('/comparar-fechas', methods=['POST'])
def comparar_fechas():
    filtros = request.get_json()
    store_nbr = filtros.get("store_nbr")
    session = SessionLocal()
    
    try:
        condiciones = []
        if store_nbr is not None:
            condiciones.append(table_pmt_dpc.c.store_nbr == store_nbr)

        stmt = (
            select(
                table_pmt_dpc.c.store_nbr,
                table_pmt_dpc.c.modification_date.label("pmt_modification_date"),
                table_pmt_dpc.c.modification_date.label("dpfile_modification_date")
            )
            .select_from(
                table_pmt_dpc.outerjoin(table_dpfile_pos, table_pmt_dpc.c.store_nbr == table_dpfile_pos.c.store_nbr)
            )
        )

        if condiciones:
            stmt = stmt.where(and_(*condiciones))

        resultados = session.execute(stmt).fetchall()

        datos = [{
            "store_nbr": r.store_nbr,
            "pmt_modification_date": r.pmt_modification_date.isoformat() if r.pmt_modification_date else None,
            "dpfile_modification_date": r.dpfile_modification_date.isoformat() if r.dpfile_modification_date else None
        } for r in resultados]

        return jsonify(datos)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

########
@app.route('/info-promotions', methods=['POST'])
def info_promotions():
    try:
        filters = PromoFilter(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    db = SessionLocal()
    results = []

    try:
        # Consulta por store_nbr en table_promos_update_store
        if filters.store_nbr is not None and filters.pos_nbr is None:
            query_store = db.query(table_promos_update_store).filter(
                table_promos_update_store.c.store_nbr == filters.store_nbr
            )
            results += query_store.all()

        # Consulta por store_nbr y pos_nbr en table_promos_update_pos
        if filters.pos_nbr is not None:
            query_pos = db.query(table_promos_update_pos).filter(
                table_promos_update_pos.c.store_nbr == filters.store_nbr,
                table_promos_update_pos.c.pos_nbr == filters.pos_nbr
            )
            results += query_pos.all()

        # Formatear respuesta
        return jsonify([{
            "store_nbr": r.store_nbr,
            "pos_nbr": getattr(r, "pos_nbr", None),
            "central_modification_date": r.central_modification_date.isoformat(),
            "store_modification_date": r.store_modification_date.isoformat(),
            "update": r.status
        } for r in results])

    finally:
        db.close()

                                    
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
