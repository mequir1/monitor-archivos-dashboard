from sqlalchemy import create_engine,  MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib

# Conexión a Azure SQL
#connection_string = (
#    'mssql+pyodbc://mequir1:gArAnt14@monitorfiles.database.windows.net:1433/monitorFiles'
#    '?driver=ODBC+Driver+17+for+SQL+Server'
#)

# Conexion a SQL Server
connection_string = (
    'mssql+pyodbc:///?odbc_connect=' +
    urllib.parse.quote_plus(
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=dmxnt55112mx.mx.Wal-Mart.com,4433;'
        'Database=DPCMonitor;'
        'Trusted_Connection=yes;'
        'Encrypt=yes;'
        'TrustServerCertificate=yes;'
    )
)

engine = create_engine(connection_string)
metadata = MetaData()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()