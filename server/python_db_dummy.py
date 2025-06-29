from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Device, Base  # Assuming your FastAPI app is in `main.py` and has `Device` and `Base` defined

# SQLite database URL (same as in your FastAPI app)
SQLALCHEMY_DATABASE_URL = "sqlite:///./mainDatabase.db"

# Set up SQLAlchemy engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the database (if not already created)
Base.metadata.create_all(bind=engine)

# Create a new session
db = SessionLocal()

# Dummy data to insert
dummy_devices = [
    {
        "deviceName": "Device 1",
        "status": "Online",
        "location": "Living Room",
        "relay1": "On",
        "relay2": "Off",
        "relay3": "On",
        "relay4": "Off",
        "lastSeen": "2025-06-22 10:00:00"
    },
    {
        "deviceName": "Device 2",
        "status": "Offline",
        "location": "Kitchen",
        "relay1": "Off",
        "relay2": "On",
        "relay3": "Off",
        "relay4": "On",
        "lastSeen": "2025-06-22 12:00:00"
    },
    {
        "deviceName": "Device 3",
        "status": "Online",
        "location": "Bedroom",
        "relay1": "On",
        "relay2": "On",
        "relay3": "Off",
        "relay4": "Off",
        "lastSeen": "2025-06-22 14:30:00"
    },
    {
        "deviceName": "Device 4",
        "status": "Offline",
        "location": "Bathroom",
        "relay1": "Off",
        "relay2": "Off",
        "relay3": "On",
        "relay4": "On",
        "lastSeen": "2025-06-22 16:00:00"
    }
]

# Insert dummy data into the database
for device in dummy_devices:
    # db_device = Device(**device)
    db.add(device)

# Commit the session to the database
db.commit()

# Close the session
db.close()

print("Dummy data added to the database successfully!")
