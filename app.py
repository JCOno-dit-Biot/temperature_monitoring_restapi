import os
from flask import Flask, request
import psycopg2
from dotenv import load_dotenv
from src import models
from src.postgres_repository import *
from pydantic import create_model

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


connection = psycopg2.connect(
    host = "localhost",
    database= os.getenv("POSTGRES_DB_NAME"),
    user= os.getenv("POSTGRES_USER_NAME"),
    password= os.getenv("POSTGRES_PWD"),
    port = os.getenv("PORT")
)
repo = PostgreSQLRepository(connection)
app = Flask(__name__)

@app.post("/api/room")
def create_room():
    data= request.get_json()
    room = models.room(data["name"])
    room_id = repo.add_room(room)

    return {"id": room_id, "message": f"Room {room.name} created."}, 201

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


#try to make the room optional. if no room passed, calculate average for all rooms
#with the current implementaiton room_name must be specified
@app.get("/api/average/<string:room_name>")
def get_average_temperature(room_name):
    data = {"name":room_name}
    
    try:
        avg_room = models.room(**data)
    except KeyError:
        logger.warning("No room were specified, calculating the average over all entries")
        avg_room = None

    average_temp = repo.get_average_temperature(avg_room)
    if average_temp:
        return { "average": round(average_temp, 2)}, 201
    else:
        #
        return {"messsage": f"could not calcualte average for room: {avg_room.name}"} ,201