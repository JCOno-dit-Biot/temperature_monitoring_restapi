import os
from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
from src import models
from src.sqlmodel_repository import *
from sqlalchemy.orm import joinedload

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



host = "localhost"
database= os.getenv("POSTGRES_DB_NAME")
user= os.getenv("POSTGRES_USER_NAME")
password= os.getenv("POSTGRES_PWD")
port = os.getenv("PORT")


DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

repo = SQLModel_repository(engine)
app = Flask(__name__)


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
    plant = None
    data= request.get_json()

    room = repo.get_room(models.Room(name = data["room_name"]))

    if room is None:
        try: 
            room = repo.add_room(models.Room(name = data["room_name"]))
        except Exception as e:
            logger.error(f"could not add room {room.name}")
            logger.error(e)
            return jsonify({"error": "Could not find the matching plant and could not create a new one"}), 500
        
    elif "plant_name" in data:

        plant = repo.get_plant(models.Plant(name = data["plant_name"]))
    
        if plant is None:
            try: 
                plant = repo.add_plant(models.Plant(name = data["plant_name"], room= room))
            except Exception as e:
                logger.error(f"could not add plant {plant.name}")
                logger.error(e)
                return jsonify({"error": "Could not find the matching plant and could not create a new one"}), 500

        #depending on the field in the request, the method creates a plant sensor or a regular sensor    
        if plant is None:
            sensor = models.Sensor(
                serial_number= data["serial_number"],
                room = room
            )
        else: 
            sensor =  models.PlantSensor(
                serial_number=data["serial_number"],
                plant = plant
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

    sensor_entry = repo.add_data_entry(sensor_entry)
    
    return { "message": f"Measurement recorded."}, 201


#passing a room is optional. revisit exception Validation may be thrown for other reasons than just room being None
@app.get("/api/average/", defaults = {'room_name': None})
@app.get("/api/average/<string:room_name>")
def get_average_temperature(room_name):
    data = {"name":room_name}
    
    try:
        avg_room = models.room(**data)
    except ValidationError:
        logger.warning("No room were specified, calculating the average over all entries")
        avg_room = None

    average_temp = repo.get_average_temperature(avg_room)
    if average_temp:
        return { "average": round(average_temp, 2)}, 200
    else:
        #
        return {"messsage": f"could not calcualte average for room: {avg_room.name}"} ,200