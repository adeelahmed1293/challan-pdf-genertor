"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class PDFRequest(BaseModel):
    """
    Request model for generating student challan PDF
    """
    challan_no: str = Field(..., description="Challan number", min_length=1, max_length=50)
    student_name: str = Field(..., description="Student's full name", min_length=1, max_length=100)
    roll_number: str = Field(..., description="Student's roll number", min_length=1, max_length=50)
    class_name: str = Field(..., description="Class/Section name", min_length=1, max_length=50)
    expiry_date: str = Field(..., description="First expiry date in YYYY-MM-DD format")

    @validator('expiry_date')
    def validate_date_format(cls, v):
        """Validate date format"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    class Config:
        schema_extra = {
            "example": {
                "challan_no": "22",
                "student_name": "Adeel Ahmed",
                "roll_number": "232201010",
                "class_name": "BSCS-5-A",
                "expiry_date": "2025-05-20"
            }
        }


class HealthResponse(BaseModel):
    """
    Response model for health check
    """
    status: str
    template_available: bool
    timestamp: str


class HomeResponse(BaseModel):
    """
    Response model for home endpoint
    """
    message: str
    version: str
    endpoints: dict
    documentation: str