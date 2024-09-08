import os
from contextlib import asynccontextmanager
import ipaddress
from fastapi import FastAPI, Request, HTTPException, status, Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from src import models, orm
from src.repository.sqlmodel_repository import *
from src.helper_functions import parse_measurement
#error handling packages
from sqlalchemy.exc import IntegrityError, OperationalError, DataError, ProgrammingError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

#define postgres database connection parameters
host = os.getenv("HOSTNAME")
database= os.getenv("POSTGRES_DB")
user= os.getenv("POSTGRES_USER")
password= os.getenv("POSTGRES_PASSWORD")
port = int(os.getenv("PORT"))

ALLOWED_NETWORKS = [
    ipaddress.ip_network(os.getenv("LOCAL_IP_MASK")),
    ipaddress.ip_network("127.0.0.1/32")  # /32 specifies a single IP address
]

#database connection string for  sqlAlchemy
DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

#start the sqlmodel engine
engine = create_engine(DATABASE_URL)


#define repository, here we are using SQLModel
repo = SQLModel_repository(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    

app = FastAPI(lifespan= lifespan)

# This middleware is not strictly necessary if ran as a container in a private network
# with firewall enabled but this is just an extra layer of safety
@app.middleware("http")
async def ip_filter_middleware(request: Request, call_next):
    #in case the app runs behind a reverse proxy, get the original IP
    client_ip = request.headers.get("x-forwarded-for")

    if client_ip:
        # The header can contain multiple IP addresses delimited by commas
        # due to successive proxies. The first one is the original IP.
        client_ip = client_ip.split(",")[0].strip()
    else:
        # Fall back to the direct connection's IP address if no forwarding info
        client_ip = request.client.host
    client_ip_address = ipaddress.ip_address(client_ip)
    if not any(client_ip_address in network for network in ALLOWED_NETWORKS):
        data = {
            'message': f'IP {request.client.host} is not allowed to access this resource.'
        }
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=data)
    response = await call_next(request)
    return response


@app.get('/')
def index():
    return {"message":'Welcome to your home monitoring server'}

@app.post("/api/room", status_code=status.HTTP_201_CREATED)
async def create_room(room: Room) -> dict:
    '''
    End point to create a room in the database, room only need a name
    The room name must be unique (case insensitive)
    '''

    try:
        room= repo.add_room(room)
    except ValueError as valerr:
        # Handle the exception and return a JSON error response
        raise HTTPException(status_code=409, detail=f"Integrity error occurred, "+ str(valerr))
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
async def create_sensor(sensor: models.SensorIn) -> dict:
    '''
    End point to create a sensor in the database, sensors must
    have a serial number and a room attached, plant is optional.
    If a plant is specified, the sensor will be added to the plant
    sensor table.
    '''
    
    room = repo.get_room(orm.Room(name = sensor.room))    

    #if the room does not exist in the database, create it
    if room is None:
        try: 
            room = repo.add_room(orm.Room(name = sensor.room))
        except ValueError as valerr:
            logger.error(valerr)
            return HTTPException(status_code=409, detail = valerr)
        except Exception as e:
            logger.error(f"could not add room {room.room}")
            logger.error(e)
            return HTTPException(status_code= 500, detail = "Could not find the matching plant and could not create a new one")
        
    #check for field value in data, only plant sensor would report a plant name
    if hasattr(sensor, 'plant') and sensor.plant is not None:
        plant = repo.get_plant(orm.Plant(name = sensor.plant))
    
        #if the plant does not exist in the database, it is created
        if plant is None:
            try: 
                plant = repo.add_plant(orm.Plant(name = sensor.plant, room = room))
            except Exception as e:
                logger.error(f"could not add plant {sensor.plant}")
                logger.error(e)
                raise HTTPException(status_code= 500, detail = "Could not find the matching plant and could not create a new one")
      
        #at this stage plant should be defined (either from the database or was just added)
        sensor =  orm.PlantSensor(
                    serial_number=sensor.serial_number,
                    plant = plant
        )

    else:
        sensor = orm.Sensor(
            serial_number= sensor.serial_number,
            room = room
        )

    try:
        #sensor can be a Plant or Regular sensor based on the processing done above
        sensor = repo.add_sensor(sensor)
    except IntegrityError as e:
        logger.error(e)
        raise HTTPException(status_code= 409, detail = "Sensor already exists in database")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code= 500, detail = "An unexpected error occurred")
    else:
        return {"id": sensor.serial_number, "message": f"Sensor {sensor.serial_number} was created."}

@app.post("/api/measurement", status_code=status.HTTP_201_CREATED)
async def add_measurement(measurement: models.Measurement):
    
    '''
    Endpoint to add measurements from sensor to the database.
    Required fields:
        - sensor_id
        - temperature
        - humidity
    Optional fields:
        - entry_timestamp, if not specified or cannot be parsed as a UTC timestamp the 
        data will be timestamped when it is received by the server
        - wetness, only comes from plant sensors. If this field is present the data 
        is processed as a plant measurement automatically
    '''
    
    #parse data entry into a database object, plant or regular sensor entry
    measurement_object = parse_measurement(measurement)

    try:
        sensor_entry = repo.add_data_entry(measurement_object)
    except Exception as e
        raise HTTPException(status_code=500, detail = f"Entry cannot be added: {e}")

    return {"message": f"Measurement recorded for sensor sensor_entry {sensor_entry.sensor_id}"}


#passing a room is optional. revisit exception Validation may be thrown for other reasons than just room being None
@app.get("/api/average/")
@app.get("/api/average/<string:room_name>")
async def get_average_temperature(room_name: Optional[str] = None):
    data = {"name":room_name}
    
    try:
        avg_room = repo.get_room(orm.Room(name = data["name"]))
    except KeyError:
        logger.warning("No room were specified, calculating the average over all entries")
        avg_room = None

    average_temp = repo.get_average_temperature(avg_room)
    if average_temp:
        return { "average": round(average_temp, 2)}, 200
    else:
        return {"error": f"could not calcualte average temperature"} , 500