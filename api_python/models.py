from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Table, MetaData
from database import Base

class PosPrice(Base):
    __tablename__ = "pos_prices"

    store_nbr = Column(Integer, primary_key=True)
    item_nbr = Column(String(10), primary_key=True)
    upc_code = Column(String(14), primary_key=True)
    upc_description = Column(String(255))
    previous_base_price = Column(DECIMAL(18, 2))
    new_base_price = Column(DECIMAL(18, 2))
    previous_customer_price = Column(DECIMAL(18, 2))
    new_customer_price = Column(DECIMAL(18, 2))
    modification_date = Column(DateTime)
    
class DpFilePos(Base):
    __tablename__ = "dpfile_pos"
    
    store_nbr = Column(Integer, primary_key=True)
    pos_nbr = Column(String(20), primary_key=True)
    ip_nbr= Column(String(255))
    modification_date= Column(DateTime)
    size_bytes= Column(Integer)
    
class PmtDpc(Base):
    __tablename__ = "pmt_dpc"
     
    name_pmt = Column(String(255), primary_key=True)
    store_nbr = Column(Integer)
    modification_date= Column(DateTime)
    size_bytes = Column(Integer)
    
    
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

table_promos_update_store = Table('vw_store_promos_update', metadata,
    Column('store_nbr', Integer, primary_key=True),      
    Column('central_modification_date', DateTime),
    Column('store_modification_date', DateTime),
    Column('status', String(5))
)

table_promos_update_pos = Table('vw_pos_promos_update', metadata,
    Column('store_nbr', Integer, primary_key=True),
    Column('pos_nbr', String(20), primary_key=True),       
    Column('central_modification_date', DateTime),
    Column('store_modification_date', DateTime),
    Column('status', String(5))
)