from src.models import *
from datetime import datetime
import pytest
from pydantic import ValidationError

def test_create_room():
    bedroom_dict = {"name": "bedroom"}
    bedroom = room(**bedroom_dict)
    assert bedroom.name == 'bedroom'

def test_validation_pydantic():
    bedroom_dict = {"name": 1}
    with pytest.raises(ValidationError):
        bedroom = room(**bedroom_dict)

def test_create_measurement():
    bedroom_dict = {"name": "bedroom"}
    bedroom = room(**bedroom_dict)

    measurement_time = datetime.utcnow()

    measurement_data = {
        "room": bedroom,
        "entry_timestamp": measurement_time,
        "temperature": 20.5,
        "humidity": 0.56
    }
    
    data_entry = measurement(**measurement_data)

    assert data_entry.entry_timestamp == measurement_time and data_entry.temperature == 20.5 and data_entry.humidity == 0.56

