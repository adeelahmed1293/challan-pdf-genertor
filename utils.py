"""
Utility functions for PDF generation
"""
from datetime import datetime, timedelta
import os
from config import DATE_FORMAT, OUTPUT_DIRECTORY


def format_date(date: datetime) -> str:
    """
    Format datetime object to DD-MM-YYYY string
    
    Args:
        date: datetime object
        
    Returns:
        Formatted date string
    """
    return date.strftime(DATE_FORMAT)


def calculate_late_fee_dates(first_expiry: datetime, first_days: int, second_days: int) -> tuple:
    """
    Calculate late fee dates based on first expiry date
    
    Args:
        first_expiry: First expiry date
        first_days: Days to add for first late fee
        second_days: Days to add for second late fee
        
    Returns:
        Tuple of (first_late_fee_date, second_late_fee_date, third_late_fee_date)
    """
    second_expiry = first_expiry + timedelta(days=first_days)
    third_expiry = second_expiry + timedelta(days=second_days)
    
    return (
        format_date(first_expiry),
        format_date(second_expiry),
        format_date(third_expiry)
    )


def generate_unique_filename(challan_no: str) -> str:
    """
    Generate fixed filename for PDF (always output.pdf)
    
    Args:
        challan_no: Challan number (not used, kept for compatibility)
        
    Returns:
        Fixed filename with path
    """
    filename = "output.pdf"
    return os.path.join(OUTPUT_DIRECTORY, filename)


def validate_template_exists(template_path: str) -> bool:
    """
    Check if template PDF exists
    
    Args:
        template_path: Path to template PDF
        
    Returns:
        True if exists, False otherwise
    """
    return os.path.exists(template_path)