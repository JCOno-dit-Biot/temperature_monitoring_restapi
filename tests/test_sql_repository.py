import pytest
from sqlmodel import SQLModel, create_engine, Session, text
from src.models import *
from src.sqlmodel_repository import SQLModel_repository
import psycopg2

@pytest.fixture(name="engine")
def fixture_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="sql_repo")
def fixture_repo(engine):
    return SQLModel_repository(engine)

def test_get_room_doesnot_exist(sql_repo):
    room_null = Room(name = "not_in_database")
    room_null = sql_repo.get_room(room_null)
    assert room_null == None

def test_get_room_in_database(sql_repo, engine):
    bedroom = Room(name="bedroom")
    SQL_statement =  text('INSERT INTO room VALUES (0,"bedroom");')
    
    with Session(engine) as session:    
        session.exec(SQL_statement)
        session.commit()
    
    bedroom_query = sql_repo.get_room(bedroom)
    
    assert bedroom.name == bedroom_query.name
    
def test_add_room(engine, sql_repo):
    bedroom = Room(name = "bedroom")
    sql_repo.add_room(bedroom)
    with Session(engine) as session:
        bedroom_query =session.exec(text('SELECT * FROM room WHERE name = "bedroom"')).first()
    assert bedroom_query.name == bedroom.name

def test_add_existing_room_raises_error(sql_repo):
    bedroom = Room(name = "bedroom")
    sql_repo.add_room(bedroom)
    with pytest.raises(ValueError):
        sql_repo.add_room(bedroom)
        #make sure the method is not case sensitive
        sql_repo.add_room(Room("BedRoom"))


        