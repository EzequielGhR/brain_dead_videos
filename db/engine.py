from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import PostTable, MultiMediaTable, Base

class InvalidData(Exception): pass

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
    
    def _add_data(self, data:dict, table:Base):
        expected_keys = sorted([column.name for column in table.__table__.columns])

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
        self._add_data(data, MultiMediaTable)
