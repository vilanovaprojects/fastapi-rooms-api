from app.models.sala import Sala


class BaseRepository:
    def __init__(self, db):
        self.db = db


class SalaRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db)

    def obtener_todos(self, skip: int = 0, limit: int = 10):
        return self.db.query(Sala).offset(skip).limit(limit).all()

    def obtener_por_id(self, sala_id: int):
        return self.db.query(Sala).filter(Sala.id == sala_id).first()

    def obtener_por_nombre(self, nombre: str):
        return self.db.query(Sala).filter(Sala.nombre == nombre).first()

    def filtrar(self, skip: int = 0, limit: int = 10, tipo_sala: str | None = None, estado: str | None = None):
        query = self.db.query(Sala)
        if tipo_sala:
            query = query.filter(Sala.tipo_sala == tipo_sala)
        if estado:
            query = query.filter(Sala.estado == estado)
        return query.offset(skip).limit(limit).all()

    def contar_total(self) -> int:
        return self.db.query(Sala).count()

    def crear(self, sala_data):
        db_sala = Sala(**sala_data.model_dump())
        self.db.add(db_sala)
        self.db.commit()
        self.db.refresh(db_sala)
        return db_sala

    def actualizar(self, sala_id: int, sala_data):
        db_sala = self.obtener_por_id(sala_id)
        if not db_sala:
            return None

        update_data = sala_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_sala, field, value)

        self.db.commit()
        self.db.refresh(db_sala)
        return db_sala

    def eliminar(self, sala_id: int) -> bool:
        db_sala = self.obtener_por_id(sala_id)
        if not db_sala:
            return False

        self.db.delete(db_sala)
        self.db.commit()
        return True
