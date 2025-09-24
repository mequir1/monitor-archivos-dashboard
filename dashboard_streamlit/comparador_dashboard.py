import streamlit as st
from sqlalchemy import create_engine, Table, Column, String, DateTime, Integer, MetaData, select
from datetime import datetime

# Configuración de conexión
connection_string = (
    'mssql+pyodbc://mequir1:gArAnt14@monitorfiles.database.windows.net:1433/monitorFiles'
    '?driver=ODBC+Driver+17+for+SQL+Server'
)
engine = create_engine(connection_string)
metadata = MetaData()

# Definir tablas
tabla_pos = Table('actualizaciones_archivos', metadata,
    Column('nombre', String(255), primary_key=True),
    Column('fecha_actualizacion', DateTime),
    Column('tamaño_bytes', Integer)
)

tabla_dp = Table('archivos_db', metadata,
    Column('nombre', String(255), primary_key=True),
    Column('fecha_actualizacion', DateTime)
)

# Título
st.title("📊 Comparador de archivos entre POS y DP")

# Cargar datos
with engine.connect() as conn:
    pos_data = conn.execute(select(tabla_pos)).fetchall()
    dp_data = conn.execute(select(tabla_dp)).fetchall()

# Convertir a diccionarios
pos_dict = {row.nombre: row.fecha_actualizacion for row in pos_data}
dp_dict = {row.nombre: row.fecha_actualizacion for row in dp_data}

# Comparar
resultados = []
for nombre in set(pos_dict.keys()).union(dp_dict.keys()):
    fecha_pos = pos_dict.get(nombre)
    fecha_dp = dp_dict.get(nombre)

    if fecha_pos and fecha_dp:
        if fecha_pos > fecha_dp:
            estado = "🟢 actualizado"
        elif fecha_pos < fecha_dp:
            estado = "🔴 No actualizado"
        else:
            estado = "🟡 Sincronizado"
    elif fecha_pos:
        estado = "🔵 Solo en pos"
    else:
        estado = "⚪ Solo en dp"

    resultados.append({
        "File": nombre,
        "Date_pos": fecha_pos,
        "Date_dp": fecha_dp,
        "Status": estado
    })

# Mostrar tabla
st.dataframe(resultados)

# Filtro opcional
archivo_filtrado = st.text_input("🔍 Buscar archivo por nombre")
if archivo_filtrado:
    filtrados = [r for r in resultados if archivo_filtrado.lower() in r["Archivo"].lower()]
    st.write(f"Resultados para: `{archivo_filtrado}`")
    st.dataframe(filtrados)
