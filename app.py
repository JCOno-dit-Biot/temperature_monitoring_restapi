import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from src import models
from src.sqlmodel_repository import *

#error handling packages
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError, DataError, ProgrammingError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


load_dotenv()



def parse_measurement_dict(data_dict):
        
        try:
            entry_timestamp =  datetime.utcfromtimestamp(int(data_dict["timestamp"]))
        except KeyError as e:
            entry_timestamp = datetime.utcnow()
            logger.warning(e)
            logger.warning("could not parse timestamp to utc time, using now as the measurement time")
        

        if 'wetness' in data_dict:
            measurement_obj = models.PlantSensorEntry(
                entry_timestamp=entry_timestamp,
                temperature = data_dict['temperature'],
                humidity = data_dict['humidity'],
                wetness = data_dict["wetness"]
            )


            measurement_obj = measurement(
                room= room(data_dict["name"]),
                temperature = data_dict["temperature"],
                humidity = data_dict['humidity'],
                entry_timestamp = entry_timestamp
            )

        return measurement_obj


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
app = Flask(__name__)

# @app.before_request
# def limit_remote_addr():
#     if not request.remote_addr.startswith('192.168.2.'):
#         abort(403)  # Forbidden

@app.route('/')
def index():
    return('Welcome to your home monitoring server')

@app.post("/api/room")
def create_room():
    '''
    End point to create a room in the database, room only need a name
    The room name must be unique (case insensitive)
    '''

    data= request.get_json()
    room = models.Room(name = data["name"])

    try:
        room= repo.add_room(room)
    except IntegrityError:
        return jsonify({"error": "Integrity error occurred"}), 400
    except DataError:
        return jsonify({"error": "Invalid data format"}), 400
    except OperationalError:
        return jsonify({"error": "Operational error with the database"}), 500
    except ProgrammingError:
        return jsonify({"error": "Database programming error"}), 500
    except Exception as e:
        logger.error(e)
        return jsonify({"error": "An unexpected error occurred"}), 500
    else:
        return jsonify({"id": room.id, "message": f"Room {room.name} created."}), 201

@app.post("/api/sensor")
def create_sensor():

    #initialize plant as None
    plant = None

    #collect data from request
    data= request.get_json()

    room = repo.get_room(models.Room(name = data["room_name"]))

    #if the room does not exist in the database, create it
    if room is None:
        try: 
            room = repo.add_room(models.Room(name = data["room_name"]))
        except Exception as e:
            logger.error(f"could not add room {room.name}")
            logger.error(e)
            return jsonify({"error": "Could not find the matching plant and could not create a new one"}), 500
        
    #check for field value in data, only plant sensor would report a plant name
    if "plant_name" in data:
    
        plant = repo.get_plant(models.Plant(name = data["plant_name"]))
    
        #if the plant does not exist in the database, it is created
        if plant is None:
            try: 
                plant = repo.add_plant(models.Plant(name = data["plan_name"], room= room))
            except Exception as e:
                logger.error(f"could not add plant {data["plant_name"]}")
                logger.error(e)
                return jsonify({"error": "Could not find the matching plant and could not create a new one"}), 500
      
        #at this stage plant should be defined (either from the database or was just added)
        sensor =  models.PlantSensor(
                    serial_number=data["serial_number"],
                    plant = plant
        )

    else:
        sensor = models.Sensor(
            serial_number= data["serial_number"],
            room = room
        )

    try:
        #sensor can be a Plant or Regular sensor based on the processing done above
        sensor = repo.add_sensor(sensor)
    except Exception as e:
        logger.error(e)
        return jsonify({"error": "An unexpected error occurred"}), 500
    else:
        return jsonify({"id": sensor.serial_number, "message": f"Sensor {sensor.serial_number} was created."}), 201

@app.post("/api/measurement")
def add_measurement():
    data = request.get_json()
    
    #tries to parse the timestamp as a UTC datetime, if it cannot find the timestamp
    #the data is timestamped with the time at which it is processed
    #TODO add some timestamp validation (for example cannot be 0)
    try:
        data["entry_timestamp"] = datetime.utcfromtimestamp(int(data["timestamp"]))
    except KeyError as e:
        data["entry_timestamp"] = datetime.utcnow()
        logger.warning(e)
        logger.warning("could not parse timestamp to utc time, using now as the measurement time")

    if 'wetness' in data:
        plant_sensor = repo.get_sensor(models.PlantSensor(serial_number = data["serial_number"]))

        #only save data if the plant is known in the database
        if plant_sensor is None:
            return jsonify ({"error": "Sensor is not in the database, entry is ignored"}), 500
        else:
            sensor_entry = models.PlantSensorEntry(
                sensor = plant_sensor,
                entry_timestamp = data["entry_timestamp"],
                temperature = data['temperature'],
                humidity = data['humidity'],
                wetness = data["wetness"]
            )
    
    else:
        #if the request does not contain wetness, it is a regular sensor (temperature and humidity only)
        sensor = repo.get_sensor(models.Sensor(serial_number = data["serial_number"]))

        if sensor is None:
            return jsonify ({"error": "Sensor is not in the database, entry is ignored"}), 500
        else:
            sensor_entry = models.HumityTemperatureEntry(
                sensor = sensor,
                entry_timestamp = data["entry_timestamp"],
                temperature = data['temperature'],
                humidity = data['humidity']
            )

    #TODO add try block, make sure add_data_entry would raise an exception if needed
    sensor_entry = repo.add_data_entry(sensor_entry)
    
    return { "message": f"Measurement recorded."}, 201


#passing a room is optional. revisit exception Validation may be thrown for other reasons than just room being None
@app.get("/api/average/", defaults = {'room_name': None})
@app.get("/api/average/<string:room_name>")
def get_average_temperature(room_name):
    data = {"name":room_name}
    
    try:
        avg_room = repo.get_room(models.Room(name = data["name"]))
        print(avg_room)
    except KeyError:
        logger.warning("No room were specified, calculating the average over all entries")
        avg_room = None

    average_temp = repo.get_average_temperature(avg_room)
    if average_temp:
        return { "average": round(average_temp, 2)}, 200
    else:
        return {"error": f"could not calcualte average temperature"} , 500