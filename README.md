📁 Monitor de Archivos + API + Dashboard
Este proyecto permite monitorear cambios en archivos locales usando Java, registrar actualizaciones en una base de datos Azure SQL mediante una API en Flask, y visualizar comparaciones entre versiones desde un dashboard interactivo en Streamlit.
🧱 Estructura del proyecto
plaintext
monitor-archivos-dashboard/
├── monitor_java/            # Monitor de archivos en Java
├── api_python/              # API Flask para registrar actualizaciones
├── dashboard_streamlit/     # Dashboard visual en Streamlit
├── sql/                     # Scripts de base de datos
├── docs/                    # Documentación técnica
├── .env                     # Variables compartidas
├── .gitignore
└── README.md
🚀 Componentes
1. Monitor Java (monitor_java/)
Monitorea una carpeta local y reporta cambios a la API.
Requisitos
Java 8 o superior
Maven
Uso
bash
cd monitor_java
mvn clean package
./lanzar_monitor.sh
Configura .env con:
bash
CARPETA=/ruta/a/archivos/
PYTHON_ENDPOINT=http://localhost:5000/reportar
LOG_PATH=monitor_archivos.log
MAIN_CLASS=com.oscar.ArchivoWatcher
JAR_PATH=target/monitor_archivos_java-1.0.0-jar-with-dependencies.jar
2. API Flask (api_python/)
Recibe los reportes del monitor y los guarda en Azure SQL.
Requisitos
Python 3.8+
requirements.txt incluye: Flask, SQLAlchemy, pyodbc
Uso
bash
cd api_python
python monitorfiles.py
La API expone:
POST /reportar: recibe nombre, fecha, tamaño
GET /comparar: compara registros entre tablas actualizaciones_archivos y archivos_db
3. Dashboard Streamlit (dashboard_streamlit/)
Visualiza comparaciones entre archivos del monitor y la base oficial.
Requisitos
Python 3.8+
Streamlit
Uso
bash
cd dashboard_streamlit
streamlit run comparador_dashboard.py
Incluye búsqueda por nombre y estado visual (🟢, 🔴, 🟡, etc.).
🗃️ Base de datos Azure SQL
El proyecto usa dos tablas:
sql
CREATE TABLE actualizaciones_archivos (
  nombre VARCHAR(255) PRIMARY KEY,
  fecha_actualizacion DATETIME,
  tamaño_bytes INT
);

CREATE TABLE archivos_db (
  nombre VARCHAR(255) PRIMARY KEY,
  fecha_actualizacion DATETIME,
  tamaño_bytes INT
);
🧠 Ideas futuras
Endpoint /sincronizar para actualizar registros automáticamente
Exportación a CSV desde el dashboard
Autenticación básica para proteger la API
Contenerización con Docker
🤝 Contribuciones
¡Bienvenidas! Puedes abrir issues, enviar pull requests o proponer mejoras en el dashboard, monitor o API.
📄 Licencia
Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y compartirlo libremente.