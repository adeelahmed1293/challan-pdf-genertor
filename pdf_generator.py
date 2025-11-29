"""
PDF generation logic using PyPDF2 and ReportLab
"""
from PyPDF2 import PdfReader, PdfWriter, PageObject
from reportlab.pdfgen import canvas
from datetime import datetime
import io
from typing import Dict

from config import (
    TEMPLATE_PDF_PATH, 
    COORDINATES, 
    FONT_NAME, 
    DEFAULT_FONT_SIZE,
    INPUT_DATE_FORMAT,
    FIRST_LATE_FEE_DAYS,
    SECOND_LATE_FEE_DAYS
)
from utils import calculate_late_fee_dates, format_date


class PDFGenerator:
    """
    Class to handle PDF generation with student details
    """
    
    def __init__(self, template_path: str = TEMPLATE_PDF_PATH):
        """
        Initialize PDF Generator
        
        Args:
            template_path: Path to template PDF file
        """
        self.template_path = template_path
        self.coords = COORDINATES
        
    def _draw_text(self, canvas_obj, text: str, x: float, y: float, size: int = DEFAULT_FONT_SIZE):
        """
        Draw text on canvas at specified position
        
        Args:
            canvas_obj: ReportLab canvas object
            text: Text to draw
            x: X coordinate
            y: Y coordinate
            size: Font size
        """
        canvas_obj.setFont(FONT_NAME, size)
        canvas_obj.drawString(x, y, text)
    
    def _draw_challan_no(self, canvas_obj, number: str):
        """Draw challan number at three positions"""
        y = self.coords["challan_no"]["y"]
        for x in self.coords["challan_no"]["x_positions"]:
            self._draw_text(canvas_obj, number, x, y)
    
    def _draw_name(self, canvas_obj, name: str):
        """Draw student name at three positions"""
        y = self.coords["name"]["y"]
        for x in self.coords["name"]["x_positions"]:
            self._draw_text(canvas_obj, name, x, y)
    
    def _draw_roll(self, canvas_obj, roll: str):
        """Draw roll number at three positions"""
        y = self.coords["roll"]["y"]
        for x in self.coords["roll"]["x_positions"]:
            self._draw_text(canvas_obj, roll, x, y)
    
    def _draw_class(self, canvas_obj, class_name: str):
        """Draw class name at three positions"""
        y = self.coords["class"]["y"]
        for x in self.coords["class"]["x_positions"]:
            self._draw_text(canvas_obj, class_name, x, y)
    
    def _draw_expiry_dates(self, canvas_obj, date: str):
        """Draw expiry date at three positions"""
        y = self.coords["expiry_date"]["y"]
        for x in self.coords["expiry_date"]["x_positions"]:
            self._draw_text(canvas_obj, date, x, y)
    
    def _draw_late_fee_dates(self, canvas_obj, date1: str, date2: str, date3: str):
        """Draw late fee dates in three rows"""
        coords = self.coords["late_fee_dates"]
        size = coords["size"]
        
        # First row
        for x in coords["x_positions"]:
            self._draw_text(canvas_obj, date1, x, coords["row1_y"], size)
        
        # Second row
        for x in coords["x_positions"]:
            self._draw_text(canvas_obj, date2, x, coords["row2_y"], size)
        
        # Third row
        for x in coords["x_positions"]:
            self._draw_text(canvas_obj, date3, x, coords["row3_y"], size)
    
    def generate(self, challan_no: str, student_name: str, roll_number: str, 
                 class_name: str, expiry_date_str: str) -> bytes:
        """
        Generate PDF with student details and return as bytes
        
        Args:
            challan_no: Challan number
            student_name: Student's full name
            roll_number: Roll number
            class_name: Class/Section name
            expiry_date_str: First expiry date (YYYY-MM-DD)
            
        Returns:
            PDF file as bytes (in-memory)
            
        Raises:
            FileNotFoundError: If template PDF doesn't exist
            ValueError: If date format is invalid
        """
        
        # Load original PDF
        reader = PdfReader(self.template_path)
        original_page = reader.pages[0]
        
        # Get page dimensions
        page_width = float(original_page.mediabox.width)
        page_height = float(original_page.mediabox.height)
        
        # Create overlay
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        
        # Parse and calculate dates
        try:
            first_expiry = datetime.strptime(expiry_date_str, INPUT_DATE_FORMAT)
        except ValueError:
            raise ValueError(f"Invalid date format. Use {INPUT_DATE_FORMAT}")
        
        f1, f2, f3 = calculate_late_fee_dates(
            first_expiry, 
            FIRST_LATE_FEE_DAYS, 
            SECOND_LATE_FEE_DAYS
        )
        
        # Draw all content
        self._draw_challan_no(c, challan_no)
        self._draw_name(c, student_name)
        self._draw_roll(c, roll_number)
        self._draw_class(c, class_name)
        self._draw_expiry_dates(c, f1)
        self._draw_late_fee_dates(c, f2, f3, f3)
        
        # Finalize overlay
        c.save()
        packet.seek(0)
        
        # Merge with original
        overlay_pdf = PdfReader(packet)
        overlay_page = overlay_pdf.pages[0]
        
        writer = PdfWriter()
        merged_page = PageObject.create_blank_page(
            width=original_page.mediabox.width,
            height=original_page.mediabox.height
        )
        
        merged_page.merge_page(original_page)
        merged_page.merge_page(overlay_page)
        writer.add_page(merged_page)
        
        # Return PDF as bytes (in-memory)
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        return output.read()
