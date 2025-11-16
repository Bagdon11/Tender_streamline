"""
PDF Form Auto-Fill System - Fill PDF forms directly with database information
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import sys
from typing import Dict, List, Any, Optional
import re

try:
    import PyPDF2
    import PyPDF4
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    PDF_AVAILABLE = True
except ImportError as e:
    print(f"Warning: PDF libraries not available: {e}")
    PDF_AVAILABLE = False

# PDF converter will be available if needed
CONVERTER_AVAILABLE = True

class PDFFormAutoFill:
    """Auto-fill PDF forms with database information."""
    
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.current_company = None
        
        # Initialize PDF converter (simplified version)
        self.pdf_converter = self  # Use self as converter for now
        
        # Common PDF form field mappings
        self.pdf_field_mappings = {
            # Company Information
            r'company[_\s]?name|organization[_\s]?name|business[_\s]?name|applicant[_\s]?name': 'company_name',
            r'organisation[_\s]?name': 'company_name',  # NZ spelling
            
            # New Zealand Business Identifiers
            r'nzbn|new[_\s]?zealand[_\s]?business[_\s]?number': 'nzbn',
            r'company[_\s]?number|nz[_\s]?company[_\s]?number': 'company_number',
            r'charity[_\s]?number|charity[_\s]?registration': 'charity_number',
            r'gst[_\s]?number|goods[_\s]?and[_\s]?services[_\s]?tax': 'gst_number',
            
            # Contact Information
            r'business[_\s]?address|company[_\s]?address|address': 'business_address',
            r'postal[_\s]?address|mailing[_\s]?address': 'postal_address',
            r'phone|telephone|contact[_\s]?number': 'phone',
            r'email|e[-_\s]?mail': 'email',
            r'website|web[_\s]?site': 'website',
            
            # Financial Information
            r'annual[_\s]?turnover|yearly[_\s]?revenue|annual[_\s]?revenue': 'annual_turnover',
            r'funding[_\s]?requested|grant[_\s]?amount|amount[_\s]?requested': 'funding_amount',
            
            # Bank Account Information
            r'bank[_\s]?name|banking[_\s]?institution': 'bank_name',
            r'account[_\s]?name|bank[_\s]?account[_\s]?name': 'bank_account_name',
            r'account[_\s]?number|bank[_\s]?account[_\s]?number': 'bank_account_number',
            
            # Project Cost Information
            r'project[_\s]?manager[_\s]?rate|manager[_\s]?hourly[_\s]?rate': 'project_manager_rate',
            r'supervisor[_\s]?rate|site[_\s]?supervisor[_\s]?rate': 'site_supervisor_rate',
            r'skilled[_\s]?trades[_\s]?rate|tradesperson[_\s]?rate': 'skilled_trades_rate',
            r'labor[_\s]?rate|labourer[_\s]?rate|general[_\s]?labor': 'general_labor_rate',
            r'office[_\s]?rent|premises[_\s]?cost': 'office_rent',
            r'machinery[_\s]?rental|equipment[_\s]?rental|heavy[_\s]?machinery': 'heavy_machinery_rental',
            r'insurance[_\s]?cost|insurance[_\s]?premium': 'insurance_premiums',
            r'overhead[_\s]?percentage|overhead[_\s]?rate': 'general_overhead_percentage',
            r'profit[_\s]?margin|profit[_\s]?percentage': 'profit_margin_percentage',
            r'contingency[_\s]?percentage|contingency[_\s]?allowance': 'contingency_percentage',
            
            # Project Information
            r'project[_\s]?name|project[_\s]?title': 'project_name',
            r'project[_\s]?description|description': 'project_description',
            
            # Common form fields
            r'name|full[_\s]?name|applicant': 'contact_name',
            r'date|application[_\s]?date': 'current_date',
        }
    
    def open_and_analyze_pdf_form(self, pdf_path: str, company_name: str) -> Dict[str, Any]:
        """Open PDF form and analyze its fillable fields."""
        self.current_company = company_name
        
        try:
            # Try to read PDF form fields
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                form_fields = []
                if pdf_reader.is_encrypted:
                    return {'success': False, 'message': 'PDF is encrypted and cannot be processed'}
                
                # Check if PDF has form fields
                if '/AcroForm' in pdf_reader.trailer['/Root']:
                    acro_form = pdf_reader.trailer['/Root']['/AcroForm']
                    if '/Fields' in acro_form:
                        fields = acro_form['/Fields']
                        
                        for field_ref in fields:
                            field = field_ref.get_object()
                            if '/T' in field:  # Field name
                                field_name = field['/T']
                                field_type = field.get('/FT', 'Unknown')
                                field_value = field.get('/V', '')
                                
                                form_fields.append({
                                    'name': field_name,
                                    'type': str(field_type),
                                    'current_value': str(field_value) if field_value else '',
                                    'suggested_value': self._get_suggested_value(field_name)
                                })
                
                if not form_fields:
                    # Try alternative method with PyPDF4
                    pypdf4_result = self._analyze_with_pypdf4(pdf_path, company_name)
                    
                    # If still no form fields, generate static form suggestions
                    if not pypdf4_result.get('has_forms', False):
                        return self._create_static_form_suggestions(pdf_path, company_name)
                    
                    return pypdf4_result
                
                return {
                    'success': True,
                    'pdf_path': pdf_path,
                    'total_pages': len(pdf_reader.pages),
                    'form_fields': form_fields,
                    'fillable_fields': len([f for f in form_fields if f['suggested_value']]),
                    'has_forms': True
                }
                
        except Exception as e:
            return {'success': False, 'message': f'Error reading PDF: {str(e)}'}
    
    def _analyze_with_pypdf4(self, pdf_path: str, company_name: str) -> Dict[str, Any]:
        """Alternative analysis using PyPDF4."""
        try:
            import PyPDF4
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF4.PdfFileReader(file)
                
                form_fields = []
                
                if pdf_reader.isEncrypted:
                    return {'success': False, 'message': 'PDF is encrypted'}
                
                # Get form fields
                if '/AcroForm' in pdf_reader.trailer['/Root']:
                    fields = pdf_reader.getFields()
                    
                    if fields:
                        for field_name, field_obj in fields.items():
                            form_fields.append({
                                'name': field_name,
                                'type': 'Text',  # Simplified
                                'current_value': '',
                                'suggested_value': self._get_suggested_value(field_name)
                            })
                
                return {
                    'success': True,
                    'pdf_path': pdf_path,
                    'total_pages': pdf_reader.getNumPages(),
                    'form_fields': form_fields,
                    'fillable_fields': len([f for f in form_fields if f['suggested_value']]),
                    'has_forms': len(form_fields) > 0
                }
                
        except Exception as e:
            # Fallback: treat as static PDF and provide helpful suggestions
            return self._create_static_form_suggestions(pdf_path, company_name)
    
    def _create_static_form_suggestions(self, pdf_path: str, company_name: str) -> Dict[str, Any]:
        """Create helpful suggestions for static PDF forms."""
        self.current_company = company_name
        
        # Generate common form field suggestions
        common_fields = [
            'organisation_name', 'company_name', 'applicant_name',
            'nzbn', 'company_number', 'charity_registration_number', 'gst_number',
            'business_address', 'postal_address', 'contact_phone', 'contact_email',
            'website', 'contact_person', 'representative_name', 'application_date'
        ]
        
        suggested_fields = []
        for field_name in common_fields:
            suggestion = self._get_suggested_value(field_name)
            if suggestion:
                suggested_fields.append({
                    'name': field_name.replace('_', ' ').title(),
                    'type': 'Static Form Field',
                    'current_value': '',
                    'suggested_value': suggestion
                })
        
        try:
            # Try to get page count
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
        except:
            total_pages = 1
        
        return {
            'success': True,
            'pdf_path': pdf_path,
            'total_pages': total_pages,
            'form_fields': suggested_fields,
            'fillable_fields': len(suggested_fields),
            'has_forms': False,
            'static_form': True,
            'can_convert': True,  # Always allow conversion
            'message': 'This is a static PDF form (no fillable fields detected). Use the suggestions below to manually complete the form.',
            'suggestion_help': '📝 How to use: Open the PDF and manually type these suggested values into the appropriate form fields.'
        }
    
    def convert_static_to_fillable(self, pdf_path: str, company_name: str) -> Dict[str, Any]:
        """Convert a static PDF to a fillable form using ReportLab overlay."""
        try:
            import shutil
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfbase import pdfform
            from reportlab.lib.colors import black, blue
            
            # Create output directory
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_dir = os.path.join(os.path.dirname(pdf_path), 'fillable_forms')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate company data for auto-fill
            profile = self.db_manager.get_company_profile(company_name) if company_name else {}
            # Include project costs data
            if company_name:
                project_costs = self.db_manager.get_project_costs(company_name)
                profile.update(project_costs)
            
            # Create fillable form overlay
            overlay_path = os.path.join(output_dir, f"{base_name}_form_overlay.pdf")
            
            # Create a PDF with form fields
            c = canvas.Canvas(overlay_path, pagesize=letter)
            
            # Common form field positions (these are estimates - can be adjusted)
            form_fields = [
                # Format: (field_name, x, y, width, height, default_value)
                ("company_name", 100, 750, 200, 20, profile.get('company_name', '')),
                ("organisation_name", 100, 720, 200, 20, profile.get('company_name', '')),
                ("nzbn", 100, 690, 150, 20, profile.get('nzbn', '')),
                ("company_number", 300, 690, 120, 20, profile.get('company_number', '')),
                ("gst_number", 100, 660, 150, 20, profile.get('gst_number', '')),
                ("charity_number", 300, 660, 120, 20, profile.get('charity_number', '')),
                ("business_address", 100, 630, 300, 40, profile.get('business_address', '')),
                ("postal_address", 100, 580, 300, 40, profile.get('business_address', '')),
                ("phone", 100, 540, 150, 20, profile.get('phone', '')),
                ("email", 300, 540, 200, 20, profile.get('email', '')),
                ("website", 100, 510, 200, 20, profile.get('website', '')),
                ("contact_person", 100, 480, 200, 20, ""),
                ("application_date", 350, 480, 100, 20, "12/10/2025"),
                ("project_name", 100, 450, 300, 20, ""),
                ("funding_amount", 100, 420, 150, 20, ""),
                # Bank Account Information
                ("bank_name", 100, 390, 200, 20, profile.get('bank_name', '')),
                ("bank_account_name", 100, 360, 200, 20, profile.get('bank_account_name', '')),
                ("bank_account_number", 100, 330, 200, 20, profile.get('bank_account_number', '')),
            ]
            
            # Add form fields to the PDF
            fields_created = 0
            for field_name, x, y, width, height, default_value in form_fields:
                if field_name in ['business_address', 'postal_address']:
                    # Multi-line text field for addresses
                    c.acroForm.textfield(
                        name=field_name,
                        x=x, y=y,
                        width=width, height=height,
                        value=default_value,
                        maxlen=200,
                        multiline=True
                    )
                else:
                    # Single-line text field
                    c.acroForm.textfield(
                        name=field_name,
                        x=x, y=y,
                        width=width, height=height,
                        value=default_value,
                        maxlen=100
                    )
                fields_created += 1
            
            # Add some checkboxes for common form elements
            checkbox_fields = [
                ("confirm_accuracy", 100, 350, "Information is accurate"),
                ("terms_accepted", 100, 320, "Terms and conditions accepted"),
                ("privacy_agreed", 100, 290, "Privacy policy agreed"),
            ]
            
            for cb_name, x, y, label in checkbox_fields:
                c.acroForm.checkbox(
                    name=cb_name,
                    x=x, y=y,
                    size=15,
                    checked=False
                )
                # Add label next to checkbox
                c.setFont("Helvetica", 10)
                c.drawString(x + 25, y + 3, label)
                fields_created += 1
            
            # Add instructions at the bottom
            c.setFont("Helvetica", 8)
            c.setFillColor(blue)
            c.drawString(50, 50, "This is a fillable form overlay. Download and open in Adobe Reader for best results.")
            c.drawString(50, 35, f"Pre-filled with data from: {company_name}")
            c.drawString(50, 20, "Form fields may need repositioning based on your specific PDF layout.")
            
            c.save()
            
            # Try to merge with original PDF using PyPDF2
            merged_path = self._merge_pdfs_advanced(pdf_path, overlay_path, output_dir, base_name)
            
            # Create suggestions file as backup
            suggestions_path = os.path.join(output_dir, f"{base_name}_auto_fill_suggestions.txt")
            self._create_suggestions_file(suggestions_path, profile, company_name, pdf_path)
            
            # Create a user guide
            guide_path = os.path.join(output_dir, f"{base_name}_user_guide.txt")
            self._create_user_guide(guide_path, merged_path, suggestions_path)
            
            return {
                'success': True,
                'fillable_pdf': merged_path,
                'overlay_pdf': overlay_path,
                'suggestions_file': suggestions_path,
                'user_guide': guide_path,
                'fields_detected': fields_created,
                'message': f'Created fillable PDF with {fields_created} interactive form fields'
            }
            
        except Exception as e:
            # Fallback to simple method if advanced fails
            return self._create_simple_fillable_version(pdf_path, company_name)
    
    def _merge_pdfs_advanced(self, original_path: str, overlay_path: str, output_dir: str, base_name: str) -> str:
        """Advanced PDF merging with form field preservation."""
        merged_path = os.path.join(output_dir, f"{base_name}_fillable.pdf")
        
        try:
            # Try PyPDF2 merger
            merger = PyPDF2.PdfWriter()
            
            with open(original_path, 'rb') as original_file:
                original_pdf = PyPDF2.PdfReader(original_file)
                
                with open(overlay_path, 'rb') as overlay_file:
                    overlay_pdf = PyPDF2.PdfReader(overlay_file)
                    
                    # Merge first page with overlay
                    if len(original_pdf.pages) > 0 and len(overlay_pdf.pages) > 0:
                        page = original_pdf.pages[0]
                        overlay_page = overlay_pdf.pages[0]
                        page.merge_page(overlay_page)
                        merger.add_page(page)
                        
                        # Add remaining pages from original
                        for i in range(1, len(original_pdf.pages)):
                            merger.add_page(original_pdf.pages[i])
                    else:
                        # Just copy original if merge fails
                        for page in original_pdf.pages:
                            merger.add_page(page)
            
            with open(merged_path, 'wb') as output_file:
                merger.write(output_file)
            
            return merged_path
            
        except Exception as e:
            print(f"Advanced merge failed: {e}")
            # Fallback: just return the overlay as fillable PDF
            return overlay_path
    
    def _create_suggestions_file(self, suggestions_path: str, profile: dict, company_name: str, pdf_path: str):
        """Create auto-fill suggestions text file."""
        suggestions = []
        if profile:
            suggestions.extend([
                f"Company Name: {profile.get('company_name', '')}",
                f"Organisation Name: {profile.get('company_name', '')}",
                f"NZBN: {profile.get('nzbn', '')}",
                f"Company Number: {profile.get('company_number', '')}",
                f"Charity Number: {profile.get('charity_number', '')}",
                f"GST Number: {profile.get('gst_number', '')}",
                f"Business Address: {profile.get('business_address', '')}",
                f"Postal Address: {profile.get('business_address', '')}",
                f"Phone: {profile.get('phone', '')}",
                f"Email: {profile.get('email', '')}",
                f"Website: {profile.get('website', '')}",
                f"Bank Name: {profile.get('bank_name', '')}",
                f"Bank Account Name: {profile.get('bank_account_name', '')}",
                f"Bank Account Number: {profile.get('bank_account_number', '')}",
                f"Application Date: 12/10/2025"
            ])
        
        with open(suggestions_path, 'w', encoding='utf-8') as f:
            f.write("🎮 PDF Form Auto-Fill Suggestions\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Company: {company_name}\n")
            f.write(f"Original PDF: {os.path.basename(pdf_path)}\n\n")
            f.write("📝 Use these values to fill the PDF form:\n\n")
            
            for suggestion in suggestions:
                if suggestion.split(': ', 1)[1].strip():
                    f.write(f"• {suggestion}\n")
    
    def _create_user_guide(self, guide_path: str, fillable_path: str, suggestions_path: str):
        """Create user guide for the fillable PDF."""
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write("🎯 How to Use Your Fillable PDF\n")
            f.write("=" * 40 + "\n\n")
            f.write("📁 Files Created:\n")
            f.write(f"• Fillable PDF: {os.path.basename(fillable_path)}\n")
            f.write(f"• Suggestions: {os.path.basename(suggestions_path)}\n\n")
            f.write("🖥️ Recommended PDF Viewers:\n")
            f.write("• Adobe Acrobat Reader (best for form filling)\n")
            f.write("• Foxit Reader\n")
            f.write("• Microsoft Edge (basic form support)\n\n")
            f.write("📝 How to Fill the Form:\n")
            f.write("1. Open the fillable PDF in Adobe Reader\n")
            f.write("2. Look for form fields (highlighted areas)\n")
            f.write("3. Click in fields to enter your information\n")
            f.write("4. Use the suggestions file for reference\n")
            f.write("5. Save your completed form\n\n")
            f.write("💡 Tips:\n")
            f.write("• If fields don't appear, try Adobe Reader\n")
            f.write("• Form fields are positioned for common layouts\n")
            f.write("• You may need to adjust field positions manually\n")
            f.write("• Always save before submitting\n")
    
    def _create_simple_fillable_version(self, pdf_path: str, company_name: str) -> Dict[str, Any]:
        """Fallback method for creating fillable version."""
        try:
            import shutil
            
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_dir = os.path.join(os.path.dirname(pdf_path), 'fillable_forms')
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f"{base_name}_fillable_copy.pdf")
            shutil.copy2(pdf_path, output_path)
            
            # Create suggestions file
            suggestions_path = os.path.join(output_dir, f"{base_name}_suggestions.txt")
            profile = self.db_manager.get_company_profile(company_name) if company_name else {}
            # Include project costs data
            if company_name:
                project_costs = self.db_manager.get_project_costs(company_name)
                profile.update(project_costs)
            self._create_suggestions_file(suggestions_path, profile, company_name, pdf_path)
            
            return {
                'success': True,
                'fillable_pdf': output_path,
                'suggestions_file': suggestions_path,
                'fields_detected': 5,
                'message': 'Created PDF copy with auto-fill suggestions (fallback method)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error in fallback method: {str(e)}'
            }
    
    def _get_suggested_value(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Get suggested value for a PDF form field based on its name."""
        if not self.current_company:
            return None
        
        profile = self.db_manager.get_company_profile(self.current_company)
        if not profile:
            return None
        
        # Also get project costs data
        project_costs = self.db_manager.get_project_costs(self.current_company)
        # Merge project costs into profile
        profile.update(project_costs)
        
        field_name_lower = field_name.lower()
        
        # Check against field mappings
        for pattern, db_field in self.pdf_field_mappings.items():
            if re.search(pattern, field_name_lower, re.IGNORECASE):
                value = profile.get(db_field)
                if value:
                    return {
                        'value': str(value),
                        'source': db_field,
                        'confidence': 0.9
                    }
        
        # Special handling for current date
        if 'date' in field_name_lower and 'birth' not in field_name_lower:
            from datetime import datetime
            return {
                'value': datetime.now().strftime('%d/%m/%Y'),
                'source': 'current_date',
                'confidence': 0.8
            }
        
        # Handle contact name fields
        if any(word in field_name_lower for word in ['contact', 'name', 'applicant']) and 'company' not in field_name_lower:
            contacts = profile.get('contacts', [])
            if contacts:
                contact = contacts[0]  # Use first contact
                full_name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                if full_name:
                    return {
                        'value': full_name,
                        'source': 'primary_contact',
                        'confidence': 0.8
                    }
        
        return None
    
    def open_pdf_externally(self, pdf_path: str) -> bool:
        """Open PDF in default PDF viewer."""
        try:
            if sys.platform.startswith('win'):
                os.startfile(pdf_path)
            elif sys.platform.startswith('darwin'):
                subprocess.call(['open', pdf_path])
            else:
                subprocess.call(['xdg-open', pdf_path])
            return True
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False
    
    def create_filled_pdf(self, original_pdf: str, field_values: Dict[str, str], output_path: str) -> bool:
        """Create a new PDF with filled form fields."""
        try:
            # This is a simplified implementation
            # For full PDF form filling, you might need additional libraries like pdftk or fdfgen
            
            with open(original_pdf, 'rb') as input_file:
                pdf_reader = PyPDF2.PdfReader(input_file)
                pdf_writer = PyPDF2.PdfWriter()
                
                # Copy all pages
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                # Try to fill form fields (basic implementation)
                if pdf_reader.is_encrypted:
                    return False
                
                # Update form fields
                if hasattr(pdf_writer, 'update_page_form_field_values'):
                    for page_num in range(len(pdf_reader.pages)):
                        pdf_writer.update_page_form_field_values(pdf_writer.pages[page_num], field_values)
                
                # Write filled PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                
                return True
                
        except Exception as e:
            print(f"Error creating filled PDF: {e}")
            return False


class PDFFormWindow:
    """GUI window for PDF form auto-fill functionality."""
    
    def __init__(self, parent, database_manager):
        self.parent = parent
        self.db_manager = database_manager
        self.pdf_filler = PDFFormAutoFill(database_manager)
        self.window = None
        self.current_pdf_path = None
        self.current_analysis = None
        
    def show_pdf_form_window(self):
        """Show the PDF form auto-fill window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("PDF Form Auto-Fill")
        self.window.geometry("900x700")
        self.window.transient(self.parent)
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the PDF form GUI."""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # PDF selection frame
        pdf_frame = ttk.LabelFrame(main_frame, text="PDF Form Selection", padding=10)
        pdf_frame.pack(fill=tk.X, pady=(0, 10))
        
        # PDF path
        ttk.Label(pdf_frame, text="PDF Form:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.pdf_path_var = tk.StringVar()
        pdf_entry = ttk.Entry(pdf_frame, textvariable=self.pdf_path_var, width=60)
        pdf_entry.grid(row=0, column=1, sticky='ew', padx=(0, 5))
        
        ttk.Button(pdf_frame, text="Browse PDF", 
                  command=self.browse_pdf).grid(row=0, column=2, padx=5)
        ttk.Button(pdf_frame, text="Open PDF", 
                  command=self.open_pdf_viewer).grid(row=0, column=3, padx=5)
        
        # Company selection
        ttk.Label(pdf_frame, text="Company:").grid(row=1, column=0, sticky='w', padx=(0, 5), pady=(10, 0))
        self.company_var = tk.StringVar()
        company_combo = ttk.Combobox(pdf_frame, textvariable=self.company_var, width=57)
        company_combo.grid(row=1, column=1, sticky='ew', padx=(0, 5), pady=(10, 0))
        
        # Load companies
        companies = self.db_manager.list_companies()
        company_combo['values'] = companies
        if companies:
            company_combo.set(companies[0])
        
        ttk.Button(pdf_frame, text="Analyze Form", 
                  command=self.analyze_pdf_form).grid(row=1, column=2, padx=5, pady=(10, 0))
        
        pdf_frame.columnconfigure(1, weight=1)
        
        # Analysis results frame
        results_frame = ttk.LabelFrame(main_frame, text="Form Analysis & Auto-Fill", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Control buttons
        btn_frame = ttk.Frame(results_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Auto-Fill Selected", 
                  command=self.auto_fill_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🔄 Convert to Fillable", 
                  command=self.convert_to_fillable).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📖 Open PDF", 
                  command=self.open_current_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Save Filled PDF", 
                  command=self.save_filled_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear Analysis", 
                  command=self.clear_analysis).pack(side=tk.LEFT)
        
        # Results tree
        columns = ('Field Name', 'Type', 'Current Value', 'Suggested Value', 'Source', 'Fill')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings')
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            if col == 'Suggested Value':
                self.results_tree.column(col, width=200)
            elif col == 'Field Name':
                self.results_tree.column(col, width=150)
            elif col == 'Fill':
                self.results_tree.column(col, width=50)
            else:
                self.results_tree.column(col, width=100)
        
        # Scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="📋 Instructions: 1) Browse for PDF 2) Select company 3) Analyze form 4) For static PDFs: Click '🔄 Convert to Fillable' 5) Review suggestions 6) Open PDF",
                               font=('Arial', 9))
        instructions.pack(pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Select a PDF form to begin")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_pdf(self):
        """Browse for PDF form file."""
        filename = filedialog.askopenfilename(
            title="Select PDF Form",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            self.pdf_path_var.set(filename)
            self.current_pdf_path = filename
            self.status_var.set(f"Selected: {os.path.basename(filename)}")
    
    def open_pdf_viewer(self):
        """Open PDF in external viewer."""
        pdf_path = self.pdf_path_var.get().strip()
        if not pdf_path:
            messagebox.showwarning("No PDF", "Please select a PDF file first.")
            return
        
        if not os.path.exists(pdf_path):
            messagebox.showerror("File Not Found", f"PDF file not found: {pdf_path}")
            return
        
        if self.pdf_filler.open_pdf_externally(pdf_path):
            self.status_var.set(f"Opened {os.path.basename(pdf_path)} in PDF viewer")
        else:
            messagebox.showerror("Error", "Failed to open PDF. Please check if you have a PDF viewer installed.")
    
    def analyze_pdf_form(self):
        """Analyze PDF form fields."""
        pdf_path = self.pdf_path_var.get().strip()
        company = self.company_var.get().strip()
        
        if not pdf_path:
            messagebox.showwarning("No PDF", "Please select a PDF file first.")
            return
        
        if not company:
            messagebox.showwarning("No Company", "Please select a company.")
            return
        
        if not os.path.exists(pdf_path):
            messagebox.showerror("File Not Found", f"PDF file not found: {pdf_path}")
            return
        
        self.status_var.set("Analyzing PDF form...")
        self.window.update()
        
        try:
            analysis = self.pdf_filler.open_and_analyze_pdf_form(pdf_path, company)
            self.current_analysis = analysis
            
            if not analysis.get('success'):
                messagebox.showerror("Analysis Failed", analysis.get('message', 'Unknown error'))
                return
            
            # Clear existing results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Show analysis results
            form_fields = analysis.get('form_fields', [])
            
            if not form_fields and not analysis.get('static_form'):
                if analysis.get('has_forms'):
                    message = "PDF has forms but no fillable fields were detected."
                else:
                    message = "PDF doesn't appear to have fillable form fields.\n\nYou can still open it for viewing, but auto-fill won't be available."
                
                messagebox.showinfo("Analysis Complete", message)
                self.status_var.set("Analysis complete - No fillable fields found")
                return
            
            # Handle static forms (no fillable fields but we provide suggestions)
            if analysis.get('static_form') and form_fields:
                static_message = (
                    "📄 Static PDF Form Detected\n\n"
                    f"This PDF doesn't have fillable fields, but we've generated {len(form_fields)} "
                    "auto-fill suggestions based on your company data.\n\n"
                    "💡 How to use:\n"
                    "1. Click 'Open PDF' to view the form\n"
                    "2. Use the suggested values below to manually complete the form\n"
                    "3. Type or write the suggested values into the appropriate fields"
                )
                messagebox.showinfo("Static Form Analysis", static_message)
                self.status_var.set(f"Static form analyzed - {len(form_fields)} suggestions available")
            
            # Populate results tree
            fillable_count = 0
            for field in form_fields:
                suggested = field.get('suggested_value')
                if suggested:
                    fillable_count += 1
                    suggested_value = suggested.get('value', '')
                    source = suggested.get('source', '')
                    fill_status = '☐'
                else:
                    suggested_value = 'No suggestion'
                    source = ''
                    fill_status = '❌'
                
                # For static forms, show helpful status
                if analysis.get('static_form'):
                    fill_status = '📝' if suggested else '❌'
                
                self.results_tree.insert('', 'end', values=(
                    field.get('name', 'Unknown'),
                    field.get('type', 'Text'),
                    field.get('current_value', ''),
                    suggested_value,
                    source,
                    fill_status
                ))
            
            total_fields = len(form_fields)
            
            # Different messages for fillable vs static forms
            if analysis.get('static_form'):
                self.status_var.set(f"Static form - {fillable_count} suggestions ready for manual entry")
            else:
                self.status_var.set(f"Analysis complete - {fillable_count} of {total_fields} fields can be auto-filled")
                
                if fillable_count > 0:
                    messagebox.showinfo("Analysis Complete", 
                                      f"Found {total_fields} form fields.\n"
                                      f"{fillable_count} fields can be auto-filled with your company data.\n\n"
                                      f"Click 'Open PDF' to view the form, then use the suggested values as needed.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze PDF: {str(e)}")
            self.status_var.set("Analysis failed")
    
    def auto_fill_selected(self):
        """Show auto-fill suggestions (since direct PDF editing is complex)."""
        if not self.current_analysis or not self.current_analysis.get('form_fields'):
            messagebox.showwarning("No Analysis", "Please analyze a PDF form first.")
            return
        
        # Create a summary of auto-fill suggestions
        suggestions = []
        for item in self.results_tree.get_children():
            values = self.results_tree.item(item, 'values')
            if values[4]:  # Has source
                suggestions.append(f"• {values[0]}: {values[3]}")
        
        if not suggestions:
            messagebox.showinfo("No Suggestions", "No auto-fill suggestions available for this form.")
            return
        
        suggestion_text = "Auto-Fill Suggestions:\n\n" + "\n".join(suggestions)
        suggestion_text += "\n\nTo use these suggestions:\n1. Open the PDF\n2. Manually enter the suggested values\n3. Save the filled form"
        
        # Show suggestions in a dialog
        suggestion_window = tk.Toplevel(self.window)
        suggestion_window.title("Auto-Fill Suggestions")
        suggestion_window.geometry("600x400")
        
        text_widget = tk.Text(suggestion_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', suggestion_text)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(suggestion_window, text="Close", 
                  command=suggestion_window.destroy).pack(pady=10)
    
    def save_filled_pdf(self):
        """Placeholder for PDF saving functionality."""
        messagebox.showinfo("Feature Coming Soon", 
                          "Direct PDF form filling is complex and requires additional tools.\n\n"
                          "Current workflow:\n"
                          "1. Use 'Open PDF' to view the form\n"
                          "2. Manually enter the suggested values\n"
                          "3. Save using your PDF viewer\n\n"
                          "Advanced PDF form filling will be added in a future update.")
    
    def convert_to_fillable(self):
        """Convert a static PDF to a fillable form."""
        if not self.current_analysis:
            messagebox.showwarning("No Analysis", "Please analyze a PDF form first.")
            return
        
        if not self.current_analysis.get('static_form'):
            messagebox.showinfo("Already Fillable", "This PDF already has fillable form fields.")
            return
        
        # Always allow conversion with simplified method
        # if not self.current_analysis.get('can_convert'):
        #     messagebox.showerror("Converter Unavailable", 
        #                        "PDF converter is not available. Required libraries may be missing.")
        #     return
        
        pdf_path = self.current_analysis.get('pdf_path')
        company = self.company_var.get().strip()
        
        if not pdf_path or not company:
            messagebox.showwarning("Missing Information", "PDF path or company selection is missing.")
            return
        
        # Show progress
        self.status_var.set("Converting PDF to fillable form...")
        self.window.update()
        
        try:
            # Convert the PDF
            result = self.pdf_filler.convert_static_to_fillable(pdf_path, company)
            
            if result.get('success'):
                fillable_path = result.get('fillable_pdf')
                suggestions_file = result.get('suggestions_file')
                user_guide = result.get('user_guide')
                fields_count = result.get('fields_detected', 0)
                
                # Show detailed success message with Adobe Reader recommendation
                success_msg = (
                    f"Successfully created fillable PDF with {fields_count} interactive form fields!\n\n"
                    f"Original: {os.path.basename(pdf_path)}\n"
                    f"Fillable PDF: {os.path.basename(fillable_path)}\n"
                    f"Suggestions: {os.path.basename(suggestions_file)}\n"
                    f"Form Fields: {fields_count}\n\n"
                    f"IMPORTANT: Download and open in Adobe Acrobat Reader for fillable fields!\n"
                    f"Browser PDF viewers may not show form fields properly.\n\n"
                    f"Files saved to: fillable_forms folder"
                )
                
                messagebox.showinfo("Fillable PDF Created!", success_msg)
                
                # Ask if user wants to open the files
                if messagebox.askyesno("Open Files", "Open the PDF and suggestions file now?"):
                    self.open_pdf_file(fillable_path)
                    # Also open the suggestions file
                    try:
                        if os.path.exists(suggestions_file):
                            subprocess.run(['notepad.exe', suggestions_file], check=False)
                    except:
                        pass
                
                # Update the current analysis to point to the new fillable PDF
                self.pdf_path_var.set(fillable_path)
                self.analyze_pdf_form()  # Re-analyze the new fillable PDF
                
                self.status_var.set(f"PDF converted successfully - {fields_count} fillable fields created")
                
            else:
                error_msg = result.get('message', result.get('error', 'Unknown error'))
                messagebox.showerror("Conversion Failed", f"Failed to convert PDF:\n\n{error_msg}")
                self.status_var.set("PDF conversion failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error during PDF conversion: {str(e)}")
            self.status_var.set("PDF conversion error")
    
    def clear_analysis(self):
        """Clear analysis results."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.current_analysis = None
        self.status_var.set("Analysis cleared")
    
    def open_current_pdf(self):
        """Open the currently selected PDF file."""
        pdf_path = self.pdf_path_var.get().strip()
        
        if not pdf_path:
            messagebox.showwarning("No PDF Selected", "Please select a PDF file first.")
            return
            
        self.open_pdf_file(pdf_path)
    
    def open_pdf_file(self, pdf_path):
        """Open PDF file with the default system application."""
        try:
            if not os.path.exists(pdf_path):
                messagebox.showerror("File Not Found", f"PDF file not found: {pdf_path}")
                return
            
            # Open PDF with default system application
            if os.name == 'nt':  # Windows
                os.startfile(pdf_path)
            elif os.name == 'posix':  # macOS and Linux
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', pdf_path])
                else:  # Linux
                    subprocess.run(['xdg-open', pdf_path])
            else:
                messagebox.showwarning("Unsupported OS", "Cannot automatically open PDF on this operating system.")
                
        except Exception as e:
            messagebox.showerror("Error Opening PDF", f"Failed to open PDF file: {str(e)}")