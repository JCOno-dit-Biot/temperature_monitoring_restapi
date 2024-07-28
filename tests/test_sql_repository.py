import pytest
from sqlmodel import SQLModel, create_engine, Session, text
from src.models import *
from src.sqlmodel_repository import SQLModel_repository
import psycopg2
from sqlalchemy.exc import IntegrityError

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

def test_add_room_with_wrong_type_raises(sql_repo):
    bedroom = Room(name = 1234)
    with pytest.raises(TypeError):
        sql_repo.add_room(bedroom)

def test_add_plant(engine, sql_repo):
    plant1= Plant(name = "Pothos")
    sql_repo.add_plant(plant1)
    with Session(engine) as session:
        stmt = text('SELECT * FROM plant WHERE name = :val')
        plant1_query =session.exec(stmt, params = {'val': plant1.name}).first()
    assert plant1_query.name == plant1.name

@pytest.mark.parametrize("plant_name", ['Plant1', 'plant1'])
def test_add_existing_room_raises_error(sql_repo, plant_name):
    plant1 = Plant(name = "plant1")
    sql_repo.add_plant(plant1)
    with pytest.raises(IntegrityError):
        sql_repo.add_plant(Plant(name= plant_name))

        