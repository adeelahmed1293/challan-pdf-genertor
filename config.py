"""
Configuration settings for the PDF Generator API
"""
import os

# API Configuration
API_TITLE = "PDF Generator API"
API_VERSION = "1.0.0"
API_HOST = "0.0.0.0"
API_PORT = 8000

# File Paths
TEMPLATE_PDF_PATH = "new_pdf.pdf"
OUTPUT_DIRECTORY = "generated_pdfs"

# PDF Coordinates - Adjust these based on your template
COORDINATES = {
    "challan_no": {
        "y": 571,
        "x_positions": [75, 350, 625]
    },
    "name": {
        "y": 460,
        "x_positions": [75, 350, 625]
    },
    "roll": {
        "y": 445,
        "x_positions": [75, 350, 625]
    },
    "class": {
        "y": 445,
        "x_positions": [205, 475, 750]
    },
    "expiry_date": {
        "y": 212,
        "x_positions": [142, 420, 696]
    },
    "late_fee_dates": {
        "row1_y": 188,
        "row2_y": 173,
        "row3_y": 151.5,
        "x_positions": [220, 495, 770],
        "size": 9
    }
}

# Date Configuration
DATE_FORMAT = "%d-%m-%Y"
INPUT_DATE_FORMAT = "%Y-%m-%d"
FIRST_LATE_FEE_DAYS = 7  # Days after first expiry
SECOND_LATE_FEE_DAYS = 14  # Days after second expiry

# Font Configuration
FONT_NAME = "Helvetica-Bold"
DEFAULT_FONT_SIZE = 10

# CORS Configuration
CORS_ORIGINS = ["*"]  # Change to specific origins in production

# Ensure output directory exists
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)