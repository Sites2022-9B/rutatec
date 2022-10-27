from datetime import datetime
from sqlalchemy.schema import DDL
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 
import os
from db.base_class import Base

# Import all the models, so that Base has them before being
# imported by Alembic
#from modulos.seguridad.models import User, Rol, RolUser  # noqa

SQLALCHEMY_DATABASE_URL = 'postgresql://rutatec:rutatec@localhost:5432/rutatec'
Base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, echo = False)
SessionLocal = sessionmaker( bind=engine, autocommit=False, autoflush=False)

                
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def createLastChangesInDB():
    totFilesExecTot = 0 # contador de archivos sql a ejecutar
    totFilesExecOK = 0 # contador de archivos ejecutados correctamente
    # Recorrer la estructura de directorios para obtener los archivos sql 
    # [que inician con "sisutsdb_" y terminan con .sql]
    wd = os.getcwd()
    #print("working directory is ", wd)
    wd = f"{wd}{os.sep}db"
    with os.scandir(wd) as ficheros:
        archsConCambiosALaBD = [fichero.name for fichero in ficheros if fichero.is_file() and \
            fichero.name.startswith('rutatecdb_') and fichero.name.endswith('.sql')  ]
    #print (archsConCambiosALaBD)
    if len(archsConCambiosALaBD) == 0:
        print ( __name__ + 'Error no se encontró ningun archivo de creación de la BD')
    else:
        for fileScriptSql in archsConCambiosALaBD:
            # print("fileScriptSql",fileScriptSql)
            # Obtener el número de la ultima actualización
            # fileScriptSql = archsConCambiosALaBD[-1] # 
            # Buscar el archivo sql en la tabla de control, para ejecutarla en caso de que no encuentre registrada 
            totFilesExecTot += 1
            scriptsqlyaEjecutado = f"Select * from controlversionbd where archivo_tecnico = '{fileScriptSql}'"
            regs = execSql(scriptsqlyaEjecutado,{}, False)    
            if regs == None or len(regs) == 0:
                numErrs = 0
                try :
                    conn = engine.connect()
                    trans = conn.begin()
                    sql_command = ""
                    with open(f"{wd}{os.sep}{fileScriptSql}",'r', encoding='utf-8' ) as sql_file:
                        # # Eliminar comentarios
                        for line in sql_file:
                            if not line.startswith('--') and line.strip('\n'):
                                # Append line to the command string
                                # sql_command += " " + line.strip('\n')   
                                sql_command += " "+ line
                    # print("sql_command",sql_command)         
                    ddl_stmt = DDL(sql_command)
                    conn.execute(ddl_stmt)
                    try:
                        sql_command = f"insert into controlversionbd (archivo_tecnico, fechaejecucion) values ('{fileScriptSql}','{datetime.today()}');"
                        conn.execute(sql_command)
                        trans.commit()
                        totFilesExecOK += 1
                    except  (BaseException) as err :
                        print("Err BD: ")
                        print(err)
                        trans.rollback()
                        break

                except  (BaseException) as err :
                    numErrs += 1
                    print("Err BD: ")
                    print(err)
            else:
                totFilesExecOK += 1
    return ( totFilesExecTot == totFilesExecOK )

def execCreateTableOrView(sqlObject:str, sqlText: str):
    with engine.connect() as con:
        try:
            rs = con.execute(sqlText.strip())
            if rs.returns_rows == True:
                for row in rs:
                    return row
        except  (OperationalError, ProgrammingError) as err :
            print(err)

def execSql(sqlText: str, sqlParams={}, getCamposYValores: Boolean = False, getMeta:Boolean = False, getTotal:Boolean = False, offset:str = None, limit:str = None):
    metadatos = ""
    sqlText = sqlText.strip().replace("\n", " ")
    try:
        with engine.connect() as con:
            try:
                statement = text (sqlText)
                if (len(sqlParams) > 0 ):
                    rs = con.execute(statement, (sqlParams) )
                else:
                    rs = con.execute(statement)
                if rs.returns_rows == True:
                    acum = []
                    metadatos = rs._metadata.keys._keys
                    if getCamposYValores == True:
                        acum = [row._mapping for row in rs]
                    else:
                        acum = [row._data for row in rs]
                    totalregs = len(acum)
                    #totalregs = rs.cursor.arraysize # solo es útil para operaciones de Ins, Upd, Del
                    if totalregs > 0 :
                        if limit != None and limit != "0":
                            intOffset = int(offset)
                            intLimit = int(limit)
                            # retornar solamente la lista paginada
                            acum = acum[intOffset: (intOffset + intLimit)] 

                    resp = acum
                    if getMeta == True:
                        resp = metadatos, acum
                    if getTotal == True:
                        resp = metadatos, acum, totalregs
                    return resp
            except (BaseException) as err :
                print(err)
    except (BaseException) as err2:
        print("Error de conexión con el servidor de BD:")
        print(err2)

# Función para generar datos de prueba al iniciar la aplicación
def execFirst(sqlText: str, table: str):
    sqlText = sqlText.strip().replace("\n", " ")
    with engine.connect() as con:
        try:
            if(table == 'procexeccont'):
                validateQuery = 'SELECT COUNT(*) FROM ' + table
                validateResp = con.execute(validateQuery).fetchone()
                if(int(validateResp[0]) == 0):
                    statement = text (sqlText)
                    con.execute(statement)
                    con.execute("INSERT INTO procexeccont(id, proc_id, numexec) VALUES(NULL, 1, 0)")
            else:
                validateQuery = 'SELECT * FROM ' + table + ' LIMIT 5'
                validateResp = con.execute(validateQuery).fetchall()
                # print(len(validateResp) < 10)
                if (len(validateResp) < 5):
                    statement = text (sqlText)
                    con.execute(statement)
            return table 
        except  (OperationalError, ProgrammingError) as err :
            print(err)