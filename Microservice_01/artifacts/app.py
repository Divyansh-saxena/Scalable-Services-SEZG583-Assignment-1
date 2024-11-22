from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from dateutil import parser

# Database URL
DATABASE_URL = "postgresql+asyncpg://root:divyansh@postgres:5432/postgres"

# Create SQLAlchemy base
Base = declarative_base()

# Define Weather and AQI models
class WeatherData(Base):
    __tablename__ = 'weather_data'
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    temperature = Column(Float)
    humidity = Column(Float)
    recorded_at = Column(TIMESTAMP)

class AQIData(Base):
    __tablename__ = 'aqi_data'
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    aqi = Column(Integer)
    recorded_at = Column(TIMESTAMP)

# Create database engine and session
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# FastAPI application
app = FastAPI()

# Pydantic models for request body validation
class WeatherCreate(BaseModel):
    city: str
    temperature: float
    humidity: float
    recorded_at: str  # Accepts date as string, we'll parse it

# class AQICreate(BaseModel):
#     city: str
#     aqi: int
#     recorded_at: str  # Accepts date as string, we'll parse it

# Helper function to parse dates in any format
def parse_date(date_str: str) -> datetime:
    try:
        # Parse the date string to a datetime object
        return parser.parse(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Microservice 1: Weather Data Operations

@app.post("/weather/")
async def create_weather_data(weather: WeatherCreate, db: AsyncSession = Depends(get_db)):
    # Convert string date to datetime object
    weather.recorded_at = parse_date(weather.recorded_at)
    weather_data = WeatherData(**weather.dict())
    db.add(weather_data)
    await db.commit()
    return {"message": "Weather data created successfully"}

@app.get("/weather/")
async def read_weather(date: str = None, db: AsyncSession = Depends(get_db)):
    query = select(WeatherData).order_by(WeatherData.recorded_at.desc())
    if date:
        parsed_date = parse_date(date)
        query = query.filter(WeatherData.recorded_at >= parsed_date)
    result = await db.execute(query)
    data = result.scalars().first()
    if not data:
        raise HTTPException(status_code=404, detail="Weather data not found")
    return data

@app.delete("/weather/{date}")
async def delete_weather(date: str, db: AsyncSession = Depends(get_db)):
    parsed_date = parse_date(date)
    query = select(WeatherData).filter(WeatherData.recorded_at >= parsed_date)
    result = await db.execute(query)
    data = result.scalars().first()
    if not data:
        raise HTTPException(status_code=404, detail="Weather data not found")
    await db.delete(data)
    await db.commit()
    return {"message": "Weather data deleted successfully"}

@app.get("/weather/avg_temp")
async def average_temperature(db: AsyncSession = Depends(get_db)):
    query = select(WeatherData.temperature)
    result = await db.execute(query)
    temperatures = result.scalars().all()
    if not temperatures:
        raise HTTPException(status_code=404, detail="No temperature data found")
    avg_temp = sum(temperatures) / len(temperatures)
    return {"average_temperature": avg_temp}

@app.get("/weather/avg_humidity")
async def average_humidity(db: AsyncSession = Depends(get_db)):
    query = select(WeatherData.humidity)
    result = await db.execute(query)
    humidity = result.scalars().all()
    if not humidity:
        raise HTTPException(status_code=404, detail="No humidity data found")
    avg_humidity = sum(humidity) / len(humidity)
    return {"average_humidity": avg_humidity}

# # Microservice 2: AQI Data Operations

# @app.post("/aqi/")
# async def create_aqi_data(aqi: AQICreate, db: AsyncSession = Depends(get_db)):
#     # Convert string date to datetime object
#     aqi.recorded_at = parse_date(aqi.recorded_at)
#     aqi_data = AQIData(**aqi.dict())
#     db.add(aqi_data)
#     await db.commit()
#     return {"message": "AQI data created successfully"}

# @app.get("/aqi/")
# async def read_aqi(date: str = None, db: AsyncSession = Depends(get_db)):
#     query = select(AQIData).order_by(AQIData.recorded_at.desc())
#     if date:
#         parsed_date = parse_date(date)
#         query = query.filter(AQIData.recorded_at >= parsed_date)
#     result = await db.execute(query)
#     data = result.scalars().first()
#     if not data:
#         raise HTTPException(status_code=404, detail="AQI data not found")
#     return data

# @app.delete("/aqi/{date}")
# async def delete_aqi(date: str, db: AsyncSession = Depends(get_db)):
#     parsed_date = parse_date(date)
#     query = select(AQIData).filter(AQIData.recorded_at >= parsed_date)
#     result = await db.execute(query)
#     data = result.scalars().first()
#     if not data:
#         raise HTTPException(status_code=404, detail="AQI data not found")
#     await db.delete(data)
#     await db.commit()
#     return {"message": "AQI data deleted successfully"}

# @app.get("/aqi/avg_aqi")
# async def average_aqi(db: AsyncSession = Depends(get_db)):
#     date_7_days_ago = datetime.now() - timedelta(days=7)
#     query = select(AQIData.aqi).filter(AQIData.recorded_at >= date_7_days_ago)
#     result = await db.execute(query)
#     aqis = result.scalars().all()
#     if not aqis:
#         raise HTTPException(status_code=404, detail="No AQI data found in the last 7 days")
#     avg_aqi = sum(aqis) / len(aqis)
#     return {"average_aqi": avg_aqi}