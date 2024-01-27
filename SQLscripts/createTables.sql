CREATE TABLE IF NOT EXISTS "rooms" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(100) 
);

CREATE TABLE IF NOT EXISTS "sensor_entry" (
    "room_id" INTEGER,
    "entry_timestamp" TIMESTAMPTZ PRIMARY KEY,
    "temperature" FLOAT,
    "humidity" FLOAT,
    CONSTRAINT "sensor_entry_fkey_roomid_id" FOREIGN KEY ("room_id") REFERENCES "rooms"("id")
);

select * from "rooms";