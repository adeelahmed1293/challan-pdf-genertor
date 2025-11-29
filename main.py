"""
FastAPI application for PDF generation
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

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
            "/generate-pdf-sample": "Generate sample PDF (GET)"
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
    
    Parameters:
    - challan_no: Challan number (string)
    - student_name: Student's full name
    - roll_number: Student's roll number
    - class_name: Class/Section name
    - expiry_date: First expiry date in YYYY-MM-DD format
    
    Returns:
    - PDF file download
    """
    
    # Check if template exists
    if not validate_template_exists(TEMPLATE_PDF_PATH):
        raise HTTPException(
            status_code=500, 
            detail=f"Template PDF '{TEMPLATE_PDF_PATH}' not found"
        )
    
    try:
        # Generate PDF
        pdf_path = pdf_generator.generate(
            challan_no=request.challan_no,
            student_name=request.student_name,
            roll_number=request.roll_number,
            class_name=request.class_name,
            expiry_date_str=request.expiry_date
        )
        
        # Return PDF file
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"challan_{request.challan_no}.pdf",
            headers={
                "Content-Disposition": f"attachment; filename=challan_{request.challan_no}.pdf"
            }
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@app.post("/generate-pdf")
async def generate_pdf_endpoint(request: PDFRequest):
    """
    Generate a student challan PDF
    
    Parameters:
    - challan_no: Challan number (string)
    - student_name: Student's full name
    - roll_number: Student's roll number
    - class_name: Class/Section name
    - expiry_date: First expiry date in YYYY-MM-DD format
    
    Returns:
    - PDF file download (always named output.pdf)
    """
    
    # Check if template exists
    if not validate_template_exists(TEMPLATE_PDF_PATH):
        raise HTTPException(
            status_code=500, 
            detail=f"Template PDF '{TEMPLATE_PDF_PATH}' not found"
        )
    
    try:
        # Generate PDF
        pdf_path = pdf_generator.generate(
            challan_no=request.challan_no,
            student_name=request.student_name,
            roll_number=request.roll_number,
            class_name=request.class_name,
            expiry_date_str=request.expiry_date
        )
        
        # Return PDF file with fixed name
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename="output.pdf",  # Fixed filename
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
        pdf_path = pdf_generator.generate(
            challan_no="22",
            student_name="Adeel Ahmed",
            roll_number="232201010",
            class_name="BSCS-5-A",
            expiry_date_str="2025-05-20"
        )
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename="output.pdf"  # Fixed filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sample PDF: {str(e)}")

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=API_HOST, 
        port=API_PORT,
        log_level="info"
    )