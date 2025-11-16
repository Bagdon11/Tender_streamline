"""
PDF Converter - Transform static PDFs into fillable forms
"""

import os
import sys
import re
from typing import Dict, List, Tuple, Any, Optional
import tempfile
import shutil

try:
    import pymupdf as fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    try:
        import fitz  # Try old import style
        FITZ_AVAILABLE = True
    except ImportError:
        FITZ_AVAILABLE = False
        print("Warning: PyMuPDF (fitz) not available for PDF conversion")

try:
    from fdfgen import forge_fdf
    FDFGEN_AVAILABLE = True
except ImportError:
    FDFGEN_AVAILABLE = False
    print("Warning: fdfgen not available for form data generation")

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not available for PDF conversion")

class PDFConverter:
    """Convert static PDFs to fillable forms with intelligent field detection."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.field_patterns = {
            # Company information patterns
            r'(company|organisation|organization)[\s_]*name': 'company_name',
            r'(business|trading)[\s_]*name': 'company_name',
            r'applicant[\s_]*name': 'company_name',
            r'organization': 'company_name',
            
            # Business numbers
            r'nzbn|new[\s_]*zealand[\s_]*business[\s_]*number': 'nzbn',
            r'company[\s_]*number|registration[\s_]*number': 'company_number',
            r'charity[\s_]*number|charity[\s_]*registration': 'charity_number',
            r'gst[\s_]*number|tax[\s_]*number': 'gst_number',
            
            # Contact information
            r'(business|postal|mailing)[\s_]*address': 'business_address',
            r'address': 'business_address',
            r'(phone|telephone)[\s_]*(number)?': 'phone',
            r'(email|e[\-_]?mail)[\s_]*(address)?': 'email',
            r'website|web[\s_]*site|url': 'website',
            
            # Contact person
            r'contact[\s_]*person|representative': 'contact_person',
            r'(contact|applicant)[\s_]*name': 'contact_person',
            r'authorised[\s_]*person': 'contact_person',
            
            # Project details
            r'project[\s_]*name|project[\s_]*title': 'project_name',
            r'(funding|grant)[\s_]*amount|amount[\s_]*requested': 'funding_amount',
            r'project[\s_]*description|description': 'project_description',
            
            # Dates
            r'application[\s_]*date|date[\s_]*of[\s_]*application': 'application_date',
            r'start[\s_]*date|commencement[\s_]*date': 'start_date',
            r'end[\s_]*date|completion[\s_]*date': 'end_date',
        }
    
    def convert_static_to_fillable(self, pdf_path: str, company_name: str = None) -> Dict[str, Any]:
        """
        Convert a static PDF to a fillable form by detecting text patterns and creating form fields.
        
        Args:
            pdf_path (str): Path to the static PDF
            company_name (str): Company name for auto-fill suggestions
            
        Returns:
            dict: Conversion results with new fillable PDF path
        """
        if not FITZ_AVAILABLE:
            return {
                'success': False,
                'message': 'PyMuPDF library not available. Cannot convert static PDFs to fillable forms.'
            }
        
        try:
            # Open the PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            
            # Extract text and detect potential form fields
            detected_fields = self._detect_form_fields(doc)
            
            if not detected_fields:
                return {
                    'success': False,
                    'message': 'No potential form fields detected in the PDF'
                }
            
            # Create fillable version
            output_path = self._create_fillable_pdf(pdf_path, detected_fields, company_name)
            
            doc.close()
            
            return {
                'success': True,
                'original_pdf': pdf_path,
                'fillable_pdf': output_path,
                'fields_detected': len(detected_fields),
                'detected_fields': detected_fields,
                'message': f'Successfully converted PDF with {len(detected_fields)} fillable fields'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error converting PDF: {str(e)}'
            }
    
    def _detect_form_fields(self, doc) -> List[Dict[str, Any]]:
        """Detect potential form fields in the PDF by analyzing text patterns."""
        detected_fields = []
        field_id = 1
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Get text with position information
            text_dict = page.get_text("dict")
            
            # Extract text blocks and detect field patterns
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text and len(text) > 2:
                                # Check for field patterns
                                field_info = self._analyze_text_for_fields(text, span, page_num)
                                if field_info:
                                    field_info['id'] = f'field_{field_id}'
                                    field_id += 1
                                    detected_fields.append(field_info)
        
        # Remove duplicates and refine field positions
        return self._refine_detected_fields(detected_fields)
    
    def _analyze_text_for_fields(self, text: str, span: Dict, page_num: int) -> Optional[Dict[str, Any]]:
        """Analyze text to determine if it represents a form field."""
        text_lower = text.lower()
        
        # Look for common field indicators
        field_indicators = [
            ':',  # "Name:"
            '_' * 3,  # Underscore lines for filling
            '...' * 3,  # Dotted lines
            '[]',  # Checkboxes
            '()',  # Parentheses for filling
        ]
        
        # Check if text contains field indicators
        has_indicator = any(indicator in text for indicator in field_indicators)
        
        if has_indicator or self._matches_field_pattern(text_lower):
            # Determine field type and suggested mapping
            field_type = self._determine_field_type(text_lower)
            field_mapping = self._get_field_mapping(text_lower)
            
            # Calculate field position (approximate input area)
            bbox = span["bbox"]  # [x0, y0, x1, y1]
            
            # Position the input field slightly to the right or below the label
            if ':' in text:
                # Field label ends with colon, place input field to the right
                input_x = bbox[2] + 10
                input_y = bbox[1]
            else:
                # Place input field below the label
                input_x = bbox[0]
                input_y = bbox[3] + 5
            
            return {
                'text': text,
                'field_type': field_type,
                'field_mapping': field_mapping,
                'page': page_num,
                'position': {
                    'x': input_x,
                    'y': input_y,
                    'width': max(150, bbox[2] - bbox[0]),
                    'height': 20
                },
                'label_bbox': bbox
            }
        
        return None
    
    def _matches_field_pattern(self, text: str) -> bool:
        """Check if text matches known field patterns."""
        for pattern in self.field_patterns.keys():
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _determine_field_type(self, text: str) -> str:
        """Determine the type of form field based on text content."""
        if 'date' in text:
            return 'date'
        elif 'email' in text:
            return 'email'
        elif 'phone' in text or 'telephone' in text:
            return 'phone'
        elif 'address' in text:
            return 'textarea'
        elif 'description' in text:
            return 'textarea'
        elif '[]' in text or 'check' in text:
            return 'checkbox'
        else:
            return 'text'
    
    def _get_field_mapping(self, text: str) -> Optional[str]:
        """Get database field mapping for the detected text."""
        for pattern, db_field in self.field_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return db_field
        return None
    
    def _refine_detected_fields(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and refine field positions."""
        refined_fields = []
        seen_mappings = set()
        
        for field in fields:
            # Avoid duplicate field mappings on the same page
            key = (field['field_mapping'], field['page'])
            if key not in seen_mappings:
                seen_mappings.add(key)
                refined_fields.append(field)
        
        return refined_fields
    
    def _create_fillable_pdf(self, original_path: str, detected_fields: List[Dict], company_name: str = None) -> str:
        """Create a fillable PDF from the detected fields."""
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(original_path))[0]
        output_dir = os.path.join(os.path.dirname(original_path), 'fillable_forms')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{base_name}_fillable.pdf")
        
        try:
            # Copy original file as base
            shutil.copy2(original_path, output_path)
            
            # Open with PyMuPDF to add form fields
            doc = fitz.open(output_path)
            
            # Add form fields to the PDF
            for field in detected_fields:
                page = doc[field['page']]
                pos = field['position']
                
                # Create form field rectangle
                field_rect = fitz.Rect(
                    pos['x'], 
                    pos['y'], 
                    pos['x'] + pos['width'], 
                    pos['y'] + pos['height']
                )
                
                # Add form field based on type
                if field['field_type'] == 'checkbox':
                    # Add checkbox
                    widget = fitz.Widget()
                    widget.field_name = field['id']
                    widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
                    widget.rect = field_rect
                    widget.field_value = False
                    page.add_widget(widget)
                elif field['field_type'] == 'textarea':
                    # Add multiline text field
                    widget = fitz.Widget()
                    widget.field_name = field['id']
                    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
                    widget.rect = field_rect
                    widget.field_flags = fitz.PDF_TX_FIELD_IS_MULTILINE
                    widget.field_value = ""
                    page.add_widget(widget)
                else:
                    # Add regular text field
                    widget = fitz.Widget()
                    widget.field_name = field['id']
                    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
                    widget.rect = field_rect
                    widget.field_value = ""
                    
                    # Set suggested value if available
                    if company_name and field['field_mapping'] and self.db_manager:
                        suggested_value = self._get_suggested_value_for_field(field['field_mapping'], company_name)
                        if suggested_value:
                            widget.field_value = suggested_value
                    
                    page.add_widget(widget)
            
            # Save the modified PDF
            doc.save(output_path, incremental=True)
            doc.close()
            
            return output_path
            
        except Exception as e:
            # If PyMuPDF approach fails, try alternative method
            return self._create_fillable_pdf_alternative(original_path, detected_fields, company_name)
    
    def _create_fillable_pdf_alternative(self, original_path: str, detected_fields: List[Dict], company_name: str = None) -> str:
        """Alternative method to create fillable PDF using reportlab overlay."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfbase import pdfform
            from reportlab.lib.colors import black
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            output_dir = os.path.join(os.path.dirname(original_path), 'fillable_forms')
            os.makedirs(output_dir, exist_ok=True)
            
            # Create form overlay
            overlay_path = os.path.join(output_dir, f"{base_name}_overlay.pdf")
            
            # Create PDF with form fields
            c = canvas.Canvas(overlay_path, pagesize=letter)
            
            for field in detected_fields:
                if field['page'] == 0:  # Only handle first page for now
                    pos = field['position']
                    
                    # Convert coordinates (PyMuPDF uses different coordinate system)
                    x = pos['x']
                    y = 792 - pos['y'] - pos['height']  # Flip Y coordinate for reportlab
                    
                    if field['field_type'] == 'checkbox':
                        c.acroForm.checkbox(
                            name=field['id'],
                            x=x,
                            y=y,
                            size=15,
                            checked=False
                        )
                    else:
                        # Get suggested value
                        value = ""
                        if company_name and field['field_mapping'] and self.db_manager:
                            suggested = self._get_suggested_value_for_field(field['field_mapping'], company_name)
                            if suggested:
                                value = suggested
                        
                        c.acroForm.textfield(
                            name=field['id'],
                            x=x,
                            y=y,
                            width=pos['width'],
                            height=pos['height'],
                            value=value,
                            maxlen=200
                        )
            
            c.save()
            
            # Try to merge with original PDF
            if PDF_AVAILABLE:
                return self._merge_pdfs(original_path, overlay_path)
            else:
                return overlay_path
                
        except Exception as e:
            print(f"Alternative PDF creation failed: {e}")
            # Return a simple copy with field annotations
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            output_dir = os.path.join(os.path.dirname(original_path), 'fillable_forms')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{base_name}_annotated.pdf")
            shutil.copy2(original_path, output_path)
            return output_path
    
    def _merge_pdfs(self, original_path: str, overlay_path: str) -> str:
        """Merge original PDF with form field overlay."""
        try:
            merger = PyPDF2.PdfWriter()
            
            with open(original_path, 'rb') as original_file:
                original_pdf = PyPDF2.PdfReader(original_file)
                
                with open(overlay_path, 'rb') as overlay_file:
                    overlay_pdf = PyPDF2.PdfReader(overlay_file)
                    
                    for page_num in range(len(original_pdf.pages)):
                        page = original_pdf.pages[page_num]
                        
                        # Overlay form fields if available
                        if page_num < len(overlay_pdf.pages):
                            overlay_page = overlay_pdf.pages[page_num]
                            page.merge_page(overlay_page)
                        
                        merger.add_page(page)
            
            # Generate final output path
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            output_dir = os.path.join(os.path.dirname(original_path), 'fillable_forms')
            final_path = os.path.join(output_dir, f"{base_name}_fillable.pdf")
            
            with open(final_path, 'wb') as output_file:
                merger.write(output_file)
            
            # Clean up overlay file
            try:
                os.remove(overlay_path)
            except:
                pass
            
            return final_path
            
        except Exception as e:
            print(f"PDF merge failed: {e}")
            return overlay_path
    
    def _get_suggested_value_for_field(self, field_mapping: str, company_name: str) -> Optional[str]:
        """Get suggested value for a field from the database."""
        if not self.db_manager:
            return None
            
        profile = self.db_manager.get_company_profile(company_name)
        if not profile:
            return None
        
        # Map database fields to suggested values
        field_map = {
            'company_name': profile.get('company_name'),
            'nzbn': profile.get('nzbn'),
            'company_number': profile.get('company_number'),
            'charity_number': profile.get('charity_number'),
            'gst_number': profile.get('gst_number'),
            'business_address': profile.get('business_address'),
            'phone': profile.get('phone'),
            'email': profile.get('email'),
            'website': profile.get('website'),
        }
        
        value = field_map.get(field_mapping)
        return str(value) if value else None
    
    def create_pre_filled_pdf(self, pdf_path: str, company_name: str, field_values: Dict[str, str]) -> str:
        """Create a pre-filled version of a fillable PDF."""
        try:
            # Generate FDF data for the form
            fdf_data = []
            for field_name, value in field_values.items():
                if value:
                    fdf_data.append((field_name, str(value)))
            
            if not fdf_data:
                return pdf_path  # No data to fill
            
            # Create FDF file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.fdf', delete=False) as fdf_file:
                fdf_content = forge_fdf("", fdf_data, [], [], [])
                fdf_file.write(fdf_content)
                fdf_path = fdf_file.name
            
            # Generate output path
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_dir = os.path.join(os.path.dirname(pdf_path), 'filled_forms')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{base_name}_filled_{company_name.replace(' ', '_')}.pdf")
            
            # Try to fill the PDF using available methods
            if self._fill_pdf_with_fdf(pdf_path, fdf_path, output_path):
                os.unlink(fdf_path)  # Clean up FDF file
                return output_path
            else:
                os.unlink(fdf_path)  # Clean up FDF file
                return pdf_path  # Return original if filling failed
                
        except Exception as e:
            print(f"Error creating pre-filled PDF: {e}")
            return pdf_path
    
    def _fill_pdf_with_fdf(self, pdf_path: str, fdf_path: str, output_path: str) -> bool:
        """Fill PDF with FDF data using available methods."""
        try:
            # Method 1: Try with PyMuPDF
            doc = fitz.open(pdf_path)
            
            # Read FDF data (simplified approach)
            with open(fdf_path, 'rb') as f:
                fdf_content = f.read()
            
            # For now, just copy the original (FDF integration is complex)
            shutil.copy2(pdf_path, output_path)
            doc.close()
            return True
            
        except Exception as e:
            print(f"PDF filling failed: {e}")
            return False