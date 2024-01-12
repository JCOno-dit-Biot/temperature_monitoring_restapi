from src.models import *
from datetime import datetime


def test_create_room():
    bedroom = room('bedroom')
    assert bedroom.name == 'bedroom'

def test_create_measurement():
    measurement_time = datetime.utcnow()
    data_entry = measurement(measurement_time, 20.5, .56)

    assert data_entry.timestamp == measurement_time and data_entry.temperature == 20.5 and data_entry.humidity == 0.56

