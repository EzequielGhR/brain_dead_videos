from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, object_mapper
from .models import PostTable, MultiMediaTable, Base

class InvalidData(Exception): pass
class InvalidParams(Exception): pass

DIALECT = "sqlite"
LOCATION = "/db/database.db"
URL = f"{DIALECT}://{LOCATION}"
    
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
    
    def _add_data(self, data:dict, table:Base, skippable:list=["created_at"]):
        expected_keys = sorted([
            column.name for column in table.__table__.columns if column.name not in skippable
        ])

        missing_keys = sorted(set(expected_keys) - set(data.keys()))
        if missing_keys:
            raise InvalidData(f"Missing keys in provided data: {missing_keys}")

        if not (sorted(data.keys()) == expected_keys):
            raise InvalidData(f"Provided data does not match expected keys: {expected_keys}")
        
        with self.create_session() as session:
            new_data = table(**data)
            session.add(new_data)
            session.commit()
        
    def add_post_data(self, data:dict):
        self._add_data(data, PostTable)

    def add_multimedia_data(self, data:dict):
        self._add_data(data, MultiMediaTable, skippable=["id", "video_uri", "created_at"])

    def _get_record(self, table:Base, id:str="", by:str="") -> dict:
        with self.create_session() as session:
            if id:
                result = session.query(table).filter_by(id=id).first()
            elif by:
                result = session.query(table).order_by(getattr(table, by).desc()).first()
            else:
                raise InvalidParams("You must provide either an id, or a field to sort by")
            return {column.key: getattr(result, column.key) for column in object_mapper(result).mapped_table.columns}
    
    def get_post_record(self, id:str="") -> dict:
        return self._get_record(PostTable, id=id, by="timestamp")
    
    def get_multimedia_record(self, id:str="", by:str="") -> dict:
        return self._get_record(MultiMediaTable, id=id, by=by)
