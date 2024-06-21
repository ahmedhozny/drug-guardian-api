from fastapi import HTTPException, Depends, APIRouter
from pydantic import BaseModel

from storage import db_instance

# Create a FastAPI instance
router = APIRouter()


# Pydantic model for data sent by clients
class ClientData(BaseModel):
    id: int
    name: str
    # Add more fields as needed


# Endpoint to receive data from clients
@router.post("/sync-data/")
async def sync_data(data: ClientData):
    db = db_instance.get_session()
    try:
        # Store the received data in the server database
        # Example: Insert data into a server table
        # Replace "ServerTable" with the actual table name in your server database
        db.execute(
            "INSERT INTO ServerTable (id, name) VALUES (:id, :name)",
            {"id": data.id, "name": data.name}
        )
        db.commit()
    except Exception as e:
        # Rollback the transaction if an error occurs
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        # Close the database connection
        db.close()
    return {"message": "Data synchronized successfully"}


@router.post("/optimize_dosage")
async def optimize_dosage():
    db = db_instance.get_session()
