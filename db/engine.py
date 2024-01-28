from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, object_mapper
from typing import Union
from .models import PostTable, MultiMediaTable, Base

#This should be easily modifible for other engines
DIALECT = "sqlite"
LOCATION = "/db/database.db"
URL = f"{DIALECT}://{LOCATION}"

#Basic but usefull exception classes
class InvalidData(Exception): pass
class InvalidParams(Exception): pass
    
class DB:
    def __init__(self):
        engine = create_engine(URL, echo=True)
        self._engine = engine
        #Create table from models
        Base.metadata.create_all(engine)
        self._Session = sessionmaker(bind=engine)
        

    @property
    def engine(self):
        return self._engine
    
    def create_session(self):
        """
        Creates a session for db interactions
        """
        return self._Session()
    
    def _validate_input(self, data:dict, table:Union[PostTable,MultiMediaTable], skippable:list=["created_at"]) -> None:
        """
        Validates data provided in contrast with expected columns on each table
        Params:
            - data: A dictionary with each key being the column name for which to provide data for
            - table: The class for the table from models
            - skippable: List of expected fields to skip, defaults to only "created_at" since it's an automatic datetime
        Returns:
            None
        Errors:
            Will raise InvalidData exception if there's an error with provided data.
            The message will include the missing keys if there are any or say the data doesn't match expected keys
        """
        #Get expected keys directly from the table skipping those provided on "skippable"
        expected_keys = sorted([
            column.name for column in table.__table__.columns if column.name not in skippable
        ])
        #Check for missing keys
        missing_keys = sorted(set(expected_keys) - set(data.keys()))
        if missing_keys:
            raise InvalidData(f"Missing keys in provided data: {missing_keys}")
        #Compare if the data provided has the exact same keys as the expected ones
        if not (sorted(data.keys()) == expected_keys):
            raise InvalidData(f"Provided data does not match expected keys: {expected_keys}")
    
    def _add_data(self, data:dict, table:Union[PostTable,MultiMediaTable], skippable:list=["created_at"]) -> None:
        """
        Adds new data to one of the tables.
        Params:
            - data: A dictionary with each key being the column name for which to provide data for
            - table: The class for the table from models
            - skippable: List of expected fields to skip, defaults to only "created_at" since it's an automatic datetime
        Returns:
            None
        Errors:
            On _validate_input: InvalidData
        """
        #Validate the provided inputs
        self._validate_input(data, table, skippable)
        #Add new data using a session
        with self.create_session() as session:
            new_data = table(**data)
            session.add(new_data)
            session.commit()
    
    def update_post_data(self, data:dict, skippable:list=["created_at"]) -> None:
        """
        Updates PostTable fields by id.
        Params:
            - data: A dictionary with each key being the column name for which to provide data for
            - skippable: List of expected fields to skip, defaults to only "created_at" since it's an automatic datetime
        Returns:
            None
        Errors:
            On _validate_input: InvalidData
        """
        #Validate provided inputs
        self._validate_input(data, PostTable, skippable)
        #create a session that will be closed after finishing.
        with self.create_session() as session:
            #Query the table by id and update with new data
            session.query(PostTable).filter_by(id=data.get("id")).update(data)
            session.commit()
    
    def update_multimedia_data(self, data:dict, skippable:list=["id", "created_at"]) -> None:
        """
        Updates MultiMediaTable fields by post_id.
        Params:
            - data: A dictionary with each key being the column name for which to provide data for
            - skippable: List of expected fields to skip, defaults to only "created_at" and "id" since they are auto fields
        Returns:
            None
        Errors:
            On _validate_input: InvalidData
        """
        self._validate_input(data, MultiMediaTable, skippable)
        #Validate provided inputs
        with self.create_session() as session:
            #Query the table by post_id and update with new data
            session.query(MultiMediaTable).filter_by(post_id=data.get("post_id")).update(data)
            session.commit()
    
        
    def add_post_data(self, data:dict) -> None:
        """
        Adds or updates data on PostTable
        Params:
            - data: A dictionary with each key being the column name for which to provide data for
        Returns:
            None
        Errors:
            On _validate_input: InvalidData
            On get_post_record: InvalidParams
        """
        id_ = data.get("id")
        #check for existing post by id
        existing_post = self.get_post_record(id=id_)
        #if post already exists, update and return None, else add data
        if existing_post:
            self.update_post_data(data)
        else:
            self._add_data(data, PostTable)

    def add_multimedia_data(self, data:dict) -> None:
        """
        Adds or updates data on MultiMediaTable by post_id
        Params:
            - data: A dictionary with each key being the column name for which to provide data for
        Returns:
            None
        Errors:
            On _validate_input: InvalidData
            On get_multimedia_by_post_id: InvalidParams
        """
        post_id = data["post_id"]
        #check for existing multimedia by post_id
        existing_multimedia = self.get_multimedia_by_post_id(post_id=post_id)
        #if multimedia already exists, update and return None, else add data
        if existing_multimedia:
            self.update_multimedia_data(data, skippable=["id", "created_at"])
        else:
            self._add_data(data, MultiMediaTable, skippable=["id", "created_at"])

    def _get_record(self, table:Union[PostTable,MultiMediaTable], id:str="", by:str="") -> dict:
        """
        Fetches a record by id or the first one after sorting by column.
        Params:
            - id: primary key of the table to fetch the record.
            - by: field to be ordered by and fetching the first. If "id" is provided, this param is ignored
        Returns:
            Dictionary with the columns as keys and record data as values, or empty dict.
        Errors:
            Will raise InvalidParams if "id" nor "by" are provided.
        """
        with self.create_session() as session:
            #Check for id if provided
            if id:
                result = session.query(table).filter_by(id=id).first()
            #if id not provided order by "by" param in desc order, then fetch first record
            elif by:
                result = session.query(table).order_by(getattr(table, by).desc()).first()
            #raise an error if no params are provided
            else:
                raise InvalidParams("You must provide either an id, or a field to sort by")
            #return an empty dict if a result can't be found
            if not result:
                return {}
            return {column.key: getattr(result, column.key) for column in object_mapper(result).mapped_table.columns}
    
    def get_post_record(self, id:str="") -> dict:
        """
        Get a record from PostTable by id, or latest post
        Params:
            - id: id of the record to fetch. If not provided will fetch latest post made
        Returns:
            Dictionary with the columns as keys and record data as values, or empty dict
        Errors:
            Shouldn't raise any.
        """
        return self._get_record(PostTable, id=id, by="timestamp")
    
    def get_multimedia_record(self, id:str="", by:str="") -> dict:
        """
        Get a record from MultiMediaTable by id, or first one by provided field
        Params:
            - id: id of the record to fetch.
            - by: Field to order by and get first one. If "id" is provided, this param is ignored.
        Returns:
            Dictionary with the columns as keys and record data as values, or empty dict
        Errors:
            on _get_record: InvalidParams
        """
        return self._get_record(MultiMediaTable, id=id, by=by)

    def get_multimedia_by_post_id(self, post_id:str):
        """
        Gets a record by post_id (which should be unique).
        Params:
            - post_id: ForeignKey for PostTable.
        Returns:
            Dictionary with the columns as keys and record data as values, or empty dict.
        Errors:
            Shouldn't raise any
        """
        with self.create_session() as session:
            #Query MultiMediaTable by post_id, and in case there are many (which shouldn't happen) get last created one.
            result = (session
                .query(MultiMediaTable)
                .filter_by(post_id=post_id)
                .order_by(MultiMediaTable.created_at.desc()).first())
            #Return an empty dict if no result is found
            if not result:
                return {}
            return {column.key: getattr(result, column.key) for column in object_mapper(result).mapped_table.columns}