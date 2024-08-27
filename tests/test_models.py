from src.orm import *
from src.models import *
from src.helper_functions import create_db_sensor_entry_from_measurement, parse_measurement
from datetime import datetime, timezone
import pytz
import pytest
from pydantic import ValidationError


@pytest.fixture
def room():
    bedroom_dict = {"name": "bedroom"}
    return Room(**bedroom_dict)
    
@pytest.fixture
def plant(room):
    dict = {
        "name": "Pothos",
        "room": room
    }
    return Plant(**dict)

@pytest.fixture
def humidity_measurement():
    measurement_data = {
        "sensor_id": 1234,
        "entry_timestamp": datetime.now(timezone.utc),
        "temperature": 20.5,
        "humidity": 0.67
    }
    return Measurement(**measurement_data)

@pytest.fixture
def wetness_measurement():
    measurement_data = {
        "sensor_id": 1234,
        "entry_timestamp": datetime.now(timezone.utc),
        "temperature": 20.5,
        "humidity": 0.67,
        "wetness":0.54
    }
    return Measurement(**measurement_data)


def test_create_room():
    bedroom_dict = {"name": "bedroom"}
    bedroom = Room(**bedroom_dict)
    assert bedroom.name == 'bedroom'

def test_create_sensor(room):
    sensor_dict = {
        "serial_number" : 12345,
        "room": room
    }
    sensor = Sensor(**sensor_dict)
    assert sensor.serial_number == 12345
    assert sensor.room.name == "bedroom"

def test_create_plant_sensor(plant):
    sensor_dict = {
        "serial_number" : 12345,
        "plant": plant
    }
    sensor = PlantSensor(**sensor_dict)
    assert sensor.serial_number == 12345
    assert sensor.plant.name == "Pothos"


def test_create_humidity_temperature_measurement():
    bedroom_dict = {"name": "bedroom"}
    bedroom = Room(**bedroom_dict)

    sensor = Sensor(
        room = bedroom,
        serial_number = 100
    )

    measurement_time = datetime.now(timezone.utc)

    measurement_data = {
        "sensor": sensor,
        "entry_timestamp": measurement_time,
        "temperature": 20.5,
        "humidity": 0.56
    }
    
    data_entry = HumidityTemperatureEntry(**measurement_data)

    assert data_entry.entry_timestamp == measurement_time and data_entry.temperature == 20.5 and data_entry.humidity == 0.56 \
    and data_entry.sensor.serial_number == 100 and data_entry.sensor.room.name == "bedroom"

def test_create_humitidy_temperature_measurement_only_sensor_id():
       
    measurement_data = {
        "sensor_id": 100,
        "entry_timestamp": datetime.now(timezone.utc),
        "temperature": 20.5,
        "humidity": 0.56
    }
    
    data_entry = HumidityTemperatureEntry(**measurement_data)

    assert data_entry.entry_timestamp == measurement_data["entry_timestamp"] and data_entry.temperature == 20.5 and data_entry.humidity == 0.56 \
    and data_entry.sensor_id == 100
       

#use pydantic model for validation
@pytest.mark.parametrize("humidity_level", [None, -1, 1.5])
def test_humidity_validation(humidity_level):

    measurement_data = {
        "sensor_id": 1234,
        "entry_timestamp": datetime.utcnow(),
        "temperature": 20.5,
        "humidity": humidity_level
    }
    with pytest.raises(ValidationError):
        data_entry = Measurement(**measurement_data)

@pytest.mark.parametrize("temperature", [None, -56, 110])
def test_temperature_validation(temperature):

    bedroom_dict = {"name": "bedroom"}
    bedroom = Room(**bedroom_dict)

    measurement_data = {
        "sensor_id": 1234,
        "entry_timestamp": datetime.utcnow(),
        "temperature": temperature,
        "humidity": 0.5
    }
    with pytest.raises(ValidationError):
        data_entry = Measurement(**measurement_data)

def test_create_create_db_entry(humidity_measurement):
    db_entry = create_db_sensor_entry_from_measurement(humidity_measurement)
    assert isinstance(db_entry, HumidityTemperatureEntry) and db_entry.temperature == 20.5 and db_entry.humidity == 0.67 \
    and db_entry.sensor_id == 1234
    humidity_measurement.wetness = 0.54
    db_entry = create_db_sensor_entry_from_measurement(humidity_measurement)
    assert isinstance(db_entry, PlantSensorEntry) and db_entry.temperature == 20.5 and db_entry.humidity == 0.67 \
    and db_entry.sensor_id == 1234 and db_entry.wetness == 0.54


@pytest.mark.parametrize("data, expected", [
    (pytest.lazy_fixture('humidity_measurement'), HumidityTemperatureEntry),
    (pytest.lazy_fixture('wetness_measurement'), PlantSensorEntry)
])
def test_parse_measurement_data_create_right_instance(data, expected):
    measurement_obj = parse_measurement(data)
    assert isinstance(measurement_obj, expected)


def test_parse_measurement_withous_ts():
    measurement_data = {
        "sensor_id": 1234,
        "temperature": 15.6,
        "humidity": 0.5
    }

    measurement_object = Measurement(**measurement_data)
    measurement_obj = parse_measurement(measurement_object)
    #this is not ideal for the test but the timestamp is created within parse function so this avoids returning 
    #the timestamp just for the test itself
    assert (measurement_obj.entry_timestamp - datetime.now(timezone.utc)).total_seconds() < 0.01

def test_parse_measurement_naive_timestamp():
    measurement_data = {
        "entry_timestamp": datetime.now(),
        "sensor_id": 1234,
        "temperature": 15.6,
        "humidity": 0.5
    }
    assert measurement_data["entry_timestamp"].tzinfo == None
    measurement_obj = parse_measurement(Measurement(**measurement_data))
    assert measurement_obj.entry_timestamp.tzinfo == pytz.utc
