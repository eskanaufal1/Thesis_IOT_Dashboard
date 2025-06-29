from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base  # Updated import
from starlette.middleware.cors import CORSMiddleware

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./mainDatabase.db"

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests from the React app running on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your React app's domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)

# SQLAlchemy setup
Base = declarative_base()  # No change needed here as it's already imported from sqlalchemy.orm

# Device model definition
class DeviceModel(Base):
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True, index=True)
    deviceName = Column(String, index=True)
    status = Column(String)
    location = Column(String)
    relay1 = Column(String)
    relay2 = Column(String)
    relay3 = Column(String)
    relay4 = Column(String)
    lastSeen = Column(String)

# Database session setup
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Pydantic models to handle request/response bodies
class DeviceBase(BaseModel):
    deviceName: str
    status: str
    location: str
    relay1: str
    relay2: str
    relay3: str
    relay4: str
    lastSeen: str

class DeviceCreate(DeviceBase):
    pass

class Device(DeviceBase):
    id: int
    
    class Config:
        from_attributes = True  # Updated for Pydantic V2

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to handle different Pydantic versions for dict() or model_dump()
def get_device_data(device):
    if hasattr(device, "model_dump"):  # For Pydantic v2.x
        return device.model_dump()
    else:  # For Pydantic v1.x
        return device.dict()

# Routes for device management

@app.get("/devices", response_model=List[Device])
def get_devices(db: Session = Depends(get_db)):
    """Get a list of all devices"""
    devices = db.query(DeviceModel).all()
    return devices

@app.get("/devices/{device_id}", response_model=Device)
def get_device(device_id: int, db: Session = Depends(get_db)):
    """Get a single device by ID"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.post("/devices", response_model=Device)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """Create a new device"""
    db_device = DeviceModel(**get_device_data(device))
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.put("/devices/{device_id}", response_model=Device)
def update_device(device_id: int, device: DeviceCreate, db: Session = Depends(get_db)):
    """Update an existing device by ID"""
    db_device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Update device fields
    for key, value in get_device_data(device).items():
        setattr(db_device, key, value)
    
    db.commit()
    db.refresh(db_device)
    return db_device

@app.delete("/devices/{device_id}", response_model=Device)
def delete_device(device_id: int, db: Session = Depends(get_db)):
    """Delete a device by ID"""
    db_device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(db_device)
    db.commit()
    return db_device
