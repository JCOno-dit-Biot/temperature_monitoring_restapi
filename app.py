import os
from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
from src import models
from src.sqlmodel_repository import *
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
        return jsonify({"error": "An unexpected error occurred"}), 500
    else:
        return jsonify({"id": room.id, "message": f"Room {room.name} created."}), 201


@app.post("/api/measurement")
def add_measurement():
    data = request.get_json()
    sensor_measurement = parse_measurement_dict(data)

    room_id = repo.get_room_id(sensor_measurement.room)
    print(room_id)
    if room_id is not None:
        repo.add_measurement(sensor_measurement, room_id)
    else:
        room_id = repo.add_room(sensor_measurement.room)
        repo.add_measurement(sensor_measurement, room_id)

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