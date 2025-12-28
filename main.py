"""
FastAPI application for PDF generation
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from config import (
    API_TITLE, 
    API_VERSION, 
    CORS_ORIGINS, 
    TEMPLATE_PDF_PATH,
    API_HOST,
    API_PORT
)
from models import PDFRequest, HealthResponse, HomeResponse
from pdf_generator import PDFGenerator
from utils import validate_template_exists

# --------------------- New DB Imports ---------------------
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
from pymongo import MongoClient
from typing import List

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise Exception("MONGO_URL missing in .env")

client = MongoClient(MONGO_URL)
db = client["auth_db"]
n8n_collection = db["n8n_data"]


class ChallanSchema(BaseModel):
    challan_no: str = Field(..., example="CH-101")
    student_name: str = Field(..., example="Adeel Ahmed")
    roll_number: str = Field(..., example="232201010")
    class_name: str = Field(..., example="BSCS-5-A")
    email: EmailStr = Field(..., example="adeelahmed@example.com")
    expiry_date: str = Field(..., example="2025-05-20")  # YYYY-MM-DD
    status: str = Field(default="pending", example="pending")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        schema_extra = {
            "example": {
                "challan_no": "CH-101",
                "student_name": "Adeel Ahmed",
                "roll_number": "232201010",
                "class_name": "BSCS-5-A",
                "email": "adeelahmed@example.com",
                "expiry_date": "2025-05-20",
                "status": "pending",
                "created_at": "2025-12-28T15:30:00"
            }
        }


# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="API for generating student challan PDFs"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PDF Generator
pdf_generator = PDFGenerator()


@app.get("/", response_model=HomeResponse)
async def home():
    """
    Home endpoint - API information
    """
    return {
        "message": f"Welcome to {API_TITLE}",
        "version": API_VERSION,
        "endpoints": {
            "/": "API information (this page)",
            "/health": "Health check endpoint",
            "/generate-pdf": "Generate student challan PDF (POST)",
            "/generate-pdf-sample": "Generate sample PDF (GET)",
            "/create-challan": "Create challan record in DB (POST)",
            "/list-challans": "List all challan records (GET)",
            "/delete-challan": "Delete challan record by email (DELETE)"
        },
        "documentation": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    template_exists = validate_template_exists(TEMPLATE_PDF_PATH)
    return {
        "status": "healthy" if template_exists else "degraded",
        "template_available": template_exists,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/generate-pdf")
async def generate_pdf_endpoint(request: PDFRequest):
    """
    Generate a student challan PDF
    """
    
    # Check if template exists
    if not validate_template_exists(TEMPLATE_PDF_PATH):
        raise HTTPException(
            status_code=500, 
            detail=f"Template PDF '{TEMPLATE_PDF_PATH}' not found"
        )
    
    try:
        # Generate PDF (returns bytes)
        pdf_bytes = pdf_generator.generate(
            challan_no=request.challan_no,
            student_name=request.student_name,
            roll_number=request.roll_number,
            class_name=request.class_name,
            expiry_date_str=request.expiry_date
        )
        
        # Return PDF directly from memory
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=output.pdf"
            }
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@app.get("/generate-pdf-sample")
async def generate_sample_pdf():
    """
    Generate a sample PDF with predefined data for testing
    """
    
    if not validate_template_exists(TEMPLATE_PDF_PATH):
        raise HTTPException(
            status_code=500, 
            detail=f"Template PDF '{TEMPLATE_PDF_PATH}' not found"
        )
    
    try:
        # Generate PDF (returns bytes)
        pdf_bytes = pdf_generator.generate(
            challan_no="22",
            student_name="Adeel Ahmed",
            roll_number="232201010",
            class_name="BSCS-5-A",
            expiry_date_str="2025-05-20"
        )
        
        # Return PDF directly from memory
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=output.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sample PDF: {str(e)}")


# --------------------- New DB Routes ---------------------

@app.post("/create-challan", response_model=ChallanSchema)
def create_challan(challan: ChallanSchema):
    """
    Create a challan record in the n8n_data collection
    """
    challan_data = challan.dict()
    challan_data["created_at"] = datetime.utcnow().isoformat()

    result = n8n_collection.insert_one(challan_data)
    challan_data["_id"] = str(result.inserted_id)

    return challan_data


@app.get("/list-challans", response_model=List[ChallanSchema])
def list_challans():
    """
    List all challan records from n8n_data collection
    """
    records = []
    for doc in n8n_collection.find():
        doc["created_at"] = doc.get("created_at", datetime.utcnow().isoformat())
        doc["status"] = doc.get("status", "pending")
        records.append(ChallanSchema(
            challan_no=doc.get("challan_no"),
            student_name=doc.get("student_name"),
            roll_number=doc.get("roll_number"),
            class_name=doc.get("class_name"),
            email=doc.get("email"),
            expiry_date=doc.get("expiry_date"),
            status=doc.get("status"),
            created_at=doc.get("created_at")
        ))
    return records


@app.delete("/delete-challan/{email}")
def delete_challan(email: str):
    """
    Delete a challan record by email
    """
    result = n8n_collection.delete_many({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"No challan found for email: {email}")
    return {"message": f"Deleted {result.deleted_count} record(s) for email: {email}"}


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    print(f"🚀 {API_TITLE} v{API_VERSION} starting...")
    print(f"📄 Template PDF: {TEMPLATE_PDF_PATH}")
    print(f"✓ Template exists: {validate_template_exists(TEMPLATE_PDF_PATH)}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    print(f"👋 {API_TITLE} shutting down...")




import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render dynamically assigns PORT
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Must be 0.0.0.0 for Render
        port=port,
        log_level="info",
        reload=False  # Turn off reload in production
    )
