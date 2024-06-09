-- When using SQLmodel classes, tables are automatically created in the database
-- Alembic can be used to apply migrations if classes are modified
-- The script below only creates the original tables that were used with the postgres repo

CREATE TABLE IF NOT EXISTS "room" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL UNIQUE  
);

CREATE TABLE IF NOT EXISTS "sensor"(
    "serial_number" INTEGER PRIMARY KEY,
    "type" VARCHAR(100),
    "room_id" INTEGER,
    CONSTRAINT "sensor_entry_fkey_room_id_id" FOREIGN KEY ("room_id") REFERENCES "room"("id")
);

CREATE TABLE IF NOT EXISTS "humidity_temperature_entry" (
    "sensor_serial" INTEGER,
    "entry_timestamp" TIMESTAMPTZ,
    "temperature" FLOAT,
    "humidity" FLOAT,
    CONSTRAINT "humidity_temperature_pkey_serial_timestamp" PRIMARY KEY ("sensor_serial", "entry_timestamp"),
    CONSTRAINT "humidity_temperature_entry_fkey_sensor_sensor_serial" FOREIGN KEY ("sensor_serial") REFERENCES "sensor"("serial_number")
);

CREATE TABLE IF NOT EXISTS "wetness_entry" (
    "sensor_serial" INTEGER,
    "entry_timestamp" TIMESTAMPTZ,
    "wetnesse" FLOAT,
    CONSTRAINT "wetness_pkey_serial_timestamp" PRIMARY KEY ("sensor_serial", "entry_timestamp"),
    CONSTRAINT "wetness_entry_fkey_sensor_sensor_serial" FOREIGN KEY ("sensor_serial") REFERENCES "sensor"("serial_number")
);

INSERT INTO room (name)
    VALUES ('default room')