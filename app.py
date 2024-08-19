import os
from fastapi import FastAPI, Request, HTTPException, status
from dotenv import load_dotenv
from src import models, orm
from src.repository.sqlmodel_repository import *
from src.helper_functions import create_db_sensor_entry_from_measurement, parse_measurement_dict
from datetime import datetime, timezone
#error handling packages
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError, DataError, ProgrammingError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

#define postgres database connection parameters
host = "localhost"
database= os.getenv("POSTGRES_DB_NAME")
user= os.getenv("POSTGRES_USER_NAME")
password= os.getenv("POSTGRES_PWD")
port = os.getenv("PORT")

#database connection string for  sqlAlchemy
DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

#define repository, here we are using SQLModel
repo = SQLModel_repository(engine)
#define flask app
app = FastAPI()

# @app.before_request
# def limit_remote_addr():
#     if not request.remote_addr.startswith('192.168.2.'):
#         abort(403)  # Forbidden

@app.get('/')
def index():
    return {"message":'Welcome to your home monitoring server'}

@app.post("/api/room", status_code=status.HTTP_201_CREATED)
async def create_room(request: Request):
    '''
    End point to create a room in the database, room only need a name
    The room name must be unique (case insensitive)
    '''

    data= await request.json()
    room = orm.Room(name = data["name"])

    try:
        room= repo.add_room(room)
    except IntegrityError:
        # Handle the exception and return a JSON error response
        raise HTTPException(status_code=400, detail="Integrity error occurred")
    except DataError:
        raise HTTPException(status_code=400, detail="Invalid data format")
    except OperationalError:
        raise HTTPException(status_code=500, detail="Operational error with the database")
    except ProgrammingError:
        raise HTTPException(status_code=500, detail="Database programming error")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail="An unexpected error occurred")
    else:
        return {"id": room.id, "message": f"Room {room.name} created."}

@app.post("/api/sensor", status_code=status.HTTP_201_CREATED)
async def create_sensor(request: Request):

    #initialize plant as None
    plant = None

    #collect data from request
    data= await request.json()

    room = repo.get_room(orm.Room(name = data["room_name"]))

    #if the room does not exist in the database, create it
    if room is None:
        try: 
            room = repo.add_room(orm.Room(name = data["room_name"]))
        except Exception as e:
            logger.error(f"could not add room {room.name}")
            logger.error(e)
            return HTTPException(status_code= 500, detail = "Could not find the matching plant and could not create a new one")
        
    #check for field value in data, only plant sensor would report a plant name
    if "plant_name" in data:
    
        plant = repo.get_plant(orm.Plant(name = data["plant_name"]))
    
        #if the plant does not exist in the database, it is created
        if plant is None:
            try: 
                plant = repo.add_plant(orm.Plant(name = data["plan_name"], room= room))
            except Exception as e:
                logger.error(f"could not add plant {data['plant_name']}")
                logger.error(e)
                return HTTPException(status_code= 500, detail = "Could not find the matching plant and could not create a new one")
      
        #at this stage plant should be defined (either from the database or was just added)
        sensor =  orm.PlantSensor(
                    serial_number=data["serial_number"],
                    plant = plant
        )

    else:
        sensor = orm.Sensor(
            serial_number= data["serial_number"],
            room = room
        )

    try:
        #sensor can be a Plant or Regular sensor based on the processing done above
        sensor = repo.add_sensor(sensor)
    except Exception as e:
        logger.error(e)
        return HTTPException(status_code= 500, detail = "An unexpected error occurred")
    else:
        return {"id": sensor.serial_number, "message": f"Sensor {sensor.serial_number} was created."}

@app.post("/api/measurement", status_code=status.HTTP_201_CREATED)
async def add_measurement(request: Request):
    data = await request.json()
    
    #returns a PlantSensorEntry or HumidityTemperatureEntry depending on the fields in data
    #If the timestamp cannot be parsed as a UTC timestamp, data is timestamped with the processing timestamp (UTC)
    #timestamp validation is taken care of by the pydantic class (in parse measurement_dict)
    measurement_object = parse_measurement_dict(data)


    #TODO add try block, make sure add_data_entry would raise an exception if needed
    sensor_entry = repo.add_data_entry(measurement_object)

    return {"message": "Measurement recorded."}


#passing a room is optional. revisit exception Validation may be thrown for other reasons than just room being None
@app.get("/api/average/")
@app.get("/api/average/<string:room_name>")
async def get_average_temperature(room_name: Optional[str] = None):
    data = {"name":room_name}
    
    try:
        avg_room = repo.get_room(orm.Room(name = data["name"]))
        print(avg_room)
    except KeyError:
        logger.warning("No room were specified, calculating the average over all entries")
        avg_room = None

    average_temp = repo.get_average_temperature(avg_room)
    if average_temp:
        return { "average": round(average_temp, 2)}, 200
    else:
        return {"error": f"could not calcualte average temperature"} , 500