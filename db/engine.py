from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, object_mapper
from typing import Union
from .models import PostTable, MultiMediaTable, Base

DIALECT = "sqlite"
LOCATION = "/db/database.db"
URL = f"{DIALECT}://{LOCATION}"

class InvalidData(Exception): pass
class InvalidParams(Exception): pass
    
class DB:
    def __init__(self):
        engine = create_engine(URL, echo=True)
        self._engine = engine
        Base.metadata.create_all(engine)
        self._Session = sessionmaker(bind=engine)
        

    @property
    def engine(self):
        return self._engine
    
    def create_session(self):
        return self._Session()
    
    def _validate_input(self, data:dict, table:Union[PostTable,MultiMediaTable], skippable:list=["created_at"]) -> None:
        expected_keys = sorted([
            column.name for column in table.__table__.columns if column.name not in skippable
        ])

        missing_keys = sorted(set(expected_keys) - set(data.keys()))
        if missing_keys:
            raise InvalidData(f"Missing keys in provided data: {missing_keys}")

        if not (sorted(data.keys()) == expected_keys):
            raise InvalidData(f"Provided data does not match expected keys: {expected_keys}")
    
    def _add_data(self, data:dict, table:Union[PostTable,MultiMediaTable], skippable:list=["created_at"]) -> None:
        self._validate_input(data, table, skippable)
        with self.create_session() as session:
            new_data = table(**data)
            session.add(new_data)
            session.commit()
    
    def update_post_data(self, data:dict, skippable:list=["created_at"]) -> None:
        self._validate_input(data, PostTable, skippable)
        with self.create_session() as session:
            session.query(PostTable).filter_by(id=data.get("id")).update(data)
            session.commit()
    
    def update_multimedia_data(self, data:dict, skippable:list=["id", "created_at"]) -> None:
        self._validate_input(data, MultiMediaTable, skippable)
        with self.create_session() as session:
            session.query(MultiMediaTable).filter_by(post_id=data.get("post_id")).update(data)
            session.commit()
    
        
    def add_post_data(self, data:dict) -> None:
        id = data.get("id")
        existing_post = self.get_post_record(id=id)
        if existing_post:
            self.update_post_data(data)
            return
        self._add_data(data, PostTable)

    def add_multimedia_data(self, data:dict) -> None:
        id = data.get("id")
        existing_multimedia = self.get_multimedia_by_post_id(post_id=id)
        if existing_multimedia:
            self.update_multimedia_data(data, skippable=["id", "created_at"])
            return
        self._add_data(data, MultiMediaTable, skippable=["id", "created_at"])

    def _get_record(self, table:Union[PostTable,MultiMediaTable], id:str="", by:str="") -> dict:
        with self.create_session() as session:
            if id:
                result = session.query(table).filter_by(id=id).first()
            elif by:
                result = session.query(table).order_by(getattr(table, by).desc()).first()
            else:
                raise InvalidParams("You must provide either an id, or a field to sort by")
            if not result:
                return {}
            return {column.key: getattr(result, column.key) for column in object_mapper(result).mapped_table.columns}
    
    def get_post_record(self, id:str="") -> dict:
        return self._get_record(PostTable, id=id, by="timestamp")
    
    def get_multimedia_record(self, id:str="", by:str="") -> dict:
        return self._get_record(MultiMediaTable, id=id, by=by)

    def get_multimedia_by_post_id(self, post_id:str):
        with self.create_session() as session:
            result = (session
                .query(MultiMediaTable)
                .filter_by(post_id=post_id)
                .order_by(MultiMediaTable.created_at.desc()).first())
            if not result:
                return {}
            return {column.key: getattr(result, column.key) for column in object_mapper(result).mapped_table.columns}