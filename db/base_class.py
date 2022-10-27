from typing import Any
from sqlalchemy.exc import OperationalError, ProgrammingError

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm.session import Session
from sqlalchemy import inspect

@as_declarative()
class Base:
    id: Any
    __name__: str
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def addtrans(self, db: Session):
        trans2 = db.begin_nested()
        db.add(self)
        trans2.commit()

    def deletetrans(self, db: Session):
        trans2 = db.begin_nested()
        db.delete(self)
        trans2.commit()

    def create(self, db: Session):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def update(self, db: Session):
        db.add(self)  # al parecer de esta forma se actualizan los datos
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session):
        #obj = db.query(self.model).get(id)
        borrado = False
        try:
            db.delete(self)
            db.commit()
            borrado = True
        except (OperationalError, ProgrammingError) as err :
            print(err)
        return borrado

    async def getStructureTable (self, database):
        tablaAconsultar = self.__tablename__
        dataPlantilla = {}
        mdColReq = [("" if col["nullable"] else "*") for col in inspect(database.engine).get_columns(tablaAconsultar) ]
        mdColumn = [ col["name"] for col in inspect(database.engine).get_columns(tablaAconsultar) ]
        mdColTip = []
        for col in inspect(database.engine).get_columns(tablaAconsultar):
            objTipo = str(col["type"])
            if objTipo.startswith("INTEGER"): mdColTip.append("Num. Entero")
            if objTipo.startswith("VARCHAR"): mdColTip.append("Texto")
            if objTipo.startswith("BOOLEAN"): mdColTip.append("Booleano")
            if objTipo.startswith("DATE"): mdColTip.append("Fecha")
            if objTipo.startswith("DATETIME"): mdColTip.append("Fecha y Hora")
        dataPlantilla = {"fields": mdColumn, "required": mdColReq, "type": mdColTip}
        return dataPlantilla

    async def getTableName (self):
        return self.__tablename__
