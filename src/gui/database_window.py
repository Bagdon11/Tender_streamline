"""
Database GUI - Interface for managing company information database
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Dict, List, Any, Optional
import json
import os
from PIL import Image, ImageTk
import fitz  # PyMuPDF for PDF preview

class ImagePreviewTooltip:
    """Tooltip class for showing image previews on hover."""
    
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        
    def showtip(self, text, file_path=None):
        """Display text or image in tooltip."""
        if self.tipwindow or not text:
            return
        
        # Get mouse position for tooltip placement
        x = self.widget.winfo_pointerx() + 10
        y = self.widget.winfo_pointery() + 10
        
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Create frame for content
        frame = tk.Frame(tw, background="lightyellow", relief="solid", borderwidth=1)
        frame.pack()
        
        # Add text
        label = tk.Label(frame, text=text, justify="left", background="lightyellow",
                        relief="solid", borderwidth=1, font=("Arial", 9))
        label.pack()
        
        # Add image preview if file exists
        if file_path and os.path.exists(file_path):
            try:
                preview_image = self._create_preview_image(file_path)
                if preview_image:
                    img_label = tk.Label(frame, image=preview_image, background="lightyellow")
                    img_label.image = preview_image  # Keep a reference
                    img_label.pack(pady=5)
            except Exception as e:
                # If image preview fails, show error text
                error_label = tk.Label(frame, text=f"Preview unavailable: {str(e)[:50]}...",
                                     background="lightyellow", font=("Arial", 8), fg="red")
                error_label.pack()
    
    def _create_preview_image(self, file_path, max_size=(200, 150)):
        """Create a preview image from file."""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            # Handle regular images
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize while maintaining aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
                
        elif file_ext == '.pdf':
            # Handle PDF files - create preview from first page
            try:
                doc = fitz.open(file_path)
                if len(doc) > 0:
                    page = doc[0]
                    # Create image from PDF page
                    mat = fitz.Matrix(0.5, 0.5)  # Scale down
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("ppm")
                    
                    # Convert to PIL Image
                    import io
                    img = Image.open(io.BytesIO(img_data))
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    doc.close()
                    return ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"PDF preview error: {e}")
                return None
        
        return None
    
    def hidetip(self):
        """Hide the tooltip."""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class DatabaseWindow:
    """Database management window for company information."""
    
    def __init__(self, parent, database_manager):
        self.parent = parent
        self.db_manager = database_manager
        self.window = None
        self.current_company = None
        
    def show_database_window(self):
        """Show the database management window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Database Management - Company Information")
        self.window.geometry("900x700")
        self.window.transient(self.parent)
        
        self.setup_database_gui()
        self.refresh_company_list()
    
    def setup_database_gui(self):
        """Setup the database management GUI."""
        # Main paned window
        main_paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Company list
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Company list
        ttk.Label(left_frame, text="Companies", font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.company_listbox = tk.Listbox(list_frame)
        company_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.company_listbox.yview)
        self.company_listbox.config(yscrollcommand=company_scrollbar.set)
        
        self.company_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        company_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.company_listbox.bind('<<ListboxSelect>>', self.on_company_select)
        
        # Company buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="New Company", command=self.add_new_company).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Import from Document", command=self.import_from_document).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Database Stats", command=self.show_database_stats).pack(fill=tk.X)
        
        # Right panel - Company details
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        # Company details notebook
        self.details_notebook = ttk.Notebook(right_frame)
        self.details_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Setup tabs
        self.setup_company_tab()
        self.setup_contacts_tab()
        self.setup_financial_tab()
        self.setup_project_costs_tab()
        self.setup_bank_account_tab()
        self.setup_certifications_tab()
        self.setup_insurance_tab()
        self.setup_experience_tab()
        self.setup_autofill_tab()
    
    def setup_company_tab(self):
        """Setup company information tab."""
        self.company_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.company_frame, text="Company Info")
        
        # Scrollable frame
        canvas = tk.Canvas(self.company_frame)
        scrollbar = ttk.Scrollbar(self.company_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Company information fields
        self.company_vars = {}
        fields = [
            ('Company Name', 'company_name'),
            ('Country', 'country'),
            # Australian Identifiers
            ('ABN (Australian)', 'abn'),
            ('ACN (Australian)', 'acn'),
            # New Zealand Identifiers  
            ('NZBN (NZ Business Number)', 'nzbn'),
            ('Company Number (NZ)', 'company_number'),
            ('Charity Number (NZ)', 'charity_number'),
            ('GST Number (NZ)', 'gst_number'),
            # Contact Information
            ('Business Address', 'business_address'),
            ('Postal Address', 'postal_address'),
            ('Phone', 'phone'),
            ('Email', 'email'),
            ('Website', 'website'),
            # Business Details
            ('Established Date', 'established_date'),
            ('Number of Employees', 'employees_count'),
            ('Annual Revenue', 'annual_revenue'),
            ('Business Type', 'business_type'),
            ('Industry Sector', 'industry_sector')
        ]
        
        for i, (label, field) in enumerate(fields):
            ttk.Label(scrollable_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            
            if field in ['business_address', 'postal_address']:
                # Multi-line text for addresses
                var = tk.Text(scrollable_frame, height=3, width=40)
                var.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            else:
                var = tk.StringVar()
                entry = ttk.Entry(scrollable_frame, textvariable=var, width=40)
                entry.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            
            self.company_vars[field] = var
        
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Save Company Info", 
                  command=self.save_company_info).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Refresh Data", 
                  command=self.refresh_current_company).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Clear Form", 
                  command=self.clear_company_form).pack(side=tk.LEFT)
    
    def setup_contacts_tab(self):
        """Setup contacts tab."""
        self.contacts_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.contacts_frame, text="Contacts")
        
        # Contacts list
        ttk.Label(self.contacts_frame, text="Team Contacts", font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        
        contacts_list_frame = ttk.Frame(self.contacts_frame)
        contacts_list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.contacts_tree = ttk.Treeview(contacts_list_frame, columns=('Role', 'Name', 'Phone', 'Email'), show='headings')
        self.contacts_tree.heading('Role', text='Role')
        self.contacts_tree.heading('Name', text='Name')
        self.contacts_tree.heading('Phone', text='Phone')
        self.contacts_tree.heading('Email', text='Email')
        
        contacts_scrollbar = ttk.Scrollbar(contacts_list_frame, orient="vertical", command=self.contacts_tree.yview)
        self.contacts_tree.configure(yscrollcommand=contacts_scrollbar.set)
        
        self.contacts_tree.pack(side="left", fill="both", expand=True)
        contacts_scrollbar.pack(side="right", fill="y")
        
        # Contacts buttons
        contacts_btn_frame = ttk.Frame(self.contacts_frame)
        contacts_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(contacts_btn_frame, text="Add Contact", command=self.add_contact).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(contacts_btn_frame, text="Edit Contact", command=self.edit_contact).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(contacts_btn_frame, text="Remove Contact", command=self.remove_contact).pack(side=tk.LEFT)
    
    def setup_financial_tab(self):
        """Setup financial information tab."""
        self.financial_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.financial_frame, text="Financial")
        
        ttk.Label(self.financial_frame, text="Financial Information", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Financial fields
        self.financial_vars = {}
        financial_fields = [
            ('Financial Year', 'financial_year'),
            ('Annual Turnover ($)', 'annual_turnover'),
            ('Profit/Loss ($)', 'profit_loss'),
            ('Assets Value ($)', 'assets_value'),
            ('Liabilities Value ($)', 'liabilities_value'),
            ('Cash Flow ($)', 'cash_flow'),
            ('Credit Rating', 'credit_rating')
        ]
        
        financial_input_frame = ttk.Frame(self.financial_frame)
        financial_input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        for i, (label, field) in enumerate(financial_fields):
            ttk.Label(financial_input_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            
            var = tk.StringVar()
            entry = ttk.Entry(financial_input_frame, textvariable=var, width=30)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
            
            self.financial_vars[field] = var
        
        financial_input_frame.columnconfigure(1, weight=1)
        
        ttk.Button(financial_input_frame, text="Save Financial Info", 
                  command=self.save_financial_info).grid(row=len(financial_fields), column=0, columnspan=2, pady=20)
    
    def setup_project_costs_tab(self):
        """Setup project costs breakdown tab."""
        self.project_costs_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.project_costs_frame, text="Project Costs")
        
        ttk.Label(self.project_costs_frame, text="Project Cost Breakdown", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Create scrollable frame for all cost categories
        canvas = tk.Canvas(self.project_costs_frame)
        scrollbar_costs = ttk.Scrollbar(self.project_costs_frame, orient="vertical", command=canvas.yview)
        scrollable_costs_frame = ttk.Frame(canvas)
        
        scrollable_costs_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_costs_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_costs.set)
        
        self.project_costs_vars = {}
        
        # Labor Costs Section
        labor_frame = ttk.LabelFrame(scrollable_costs_frame, text="Labor Costs")
        labor_frame.pack(fill=tk.X, padx=10, pady=5)
        
        labor_costs = [
            ('Project Manager Salary/Rate ($/hour or $/month)', 'project_manager_rate'),
            ('Site Supervisor Salary/Rate ($/hour)', 'site_supervisor_rate'),
            ('Skilled Tradesperson Rate ($/hour)', 'skilled_trades_rate'),
            ('General Laborer Rate ($/hour)', 'general_labor_rate'),
            ('Administrative Staff Costs ($/month)', 'admin_staff_costs'),
            ('Overtime Rates ($/hour)', 'overtime_rates'),
            ('Holiday/Leave Provisions (%)', 'holiday_provisions'),
            ('Accident Compensation (ACC) (% of wages)', 'acc_percentage'),
            ('KiwiSaver Employer Contributions (% of wages)', 'kiwisaver_contributions')
        ]
        
        for i, (label, field) in enumerate(labor_costs):
            ttk.Label(labor_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(labor_frame, textvariable=var, width=20)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            self.project_costs_vars[field] = var
        
        labor_frame.columnconfigure(1, weight=1)
        
        # Equipment & Materials Section
        equipment_frame = ttk.LabelFrame(scrollable_costs_frame, text="Equipment & Materials")
        equipment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        equipment_costs = [
            ('Heavy Machinery Rental ($/day)', 'heavy_machinery_rental'),
            ('Tools & Small Equipment ($/month)', 'tools_equipment'),
            ('Vehicle Fleet Costs ($/month)', 'vehicle_fleet_costs'),
            ('Fuel & Transportation ($/week)', 'fuel_transport'),
            ('Raw Materials Budget ($)', 'raw_materials'),
            ('Safety Equipment & PPE ($/person)', 'safety_equipment'),
            ('Technology & Software Licenses ($/month)', 'technology_licenses')
        ]
        
        for i, (label, field) in enumerate(equipment_costs):
            ttk.Label(equipment_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(equipment_frame, textvariable=var, width=20)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            self.project_costs_vars[field] = var
        
        equipment_frame.columnconfigure(1, weight=1)
        
        # Operational Costs Section
        operational_frame = ttk.LabelFrame(scrollable_costs_frame, text="Operational Costs")
        operational_frame.pack(fill=tk.X, padx=10, pady=5)
        
        operational_costs = [
            ('Office Rent ($/month)', 'office_rent'),
            ('Site Office/Facilities Rent ($/month)', 'site_office_rent'),
            ('Utilities (Electricity, Water, Internet) ($/month)', 'utilities'),
            ('Phone & Communication ($/month)', 'communications'),
            ('Insurance Premiums ($/year)', 'insurance_premiums'),
            ('Professional Services (Legal, Accounting) ($/month)', 'professional_services'),
            ('Marketing & Business Development ($/month)', 'marketing_costs'),
            ('Training & Certification ($/year)', 'training_costs')
        ]
        
        for i, (label, field) in enumerate(operational_costs):
            ttk.Label(operational_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(operational_frame, textvariable=var, width=20)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            self.project_costs_vars[field] = var
        
        operational_frame.columnconfigure(1, weight=1)
        
        # Project-Specific Costs Section
        project_frame = ttk.LabelFrame(scrollable_costs_frame, text="Project-Specific Costs")
        project_frame.pack(fill=tk.X, padx=10, pady=5)
        
        project_costs = [
            ('Permits & Consent Fees ($)', 'permits_consents'),
            ('Environmental Compliance Costs ($)', 'environmental_compliance'),
            ('Quality Assurance/Testing ($)', 'quality_assurance'),
            ('Sub-contractor Costs ($/project)', 'subcontractor_costs'),
            ('Contingency Fund (% of total)', 'contingency_percentage'),
            ('Risk Management Provisions ($)', 'risk_provisions'),
            ('Bond & Guarantee Costs ($)', 'bond_guarantee_costs')
        ]
        
        for i, (label, field) in enumerate(project_costs):
            ttk.Label(project_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(project_frame, textvariable=var, width=20)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            self.project_costs_vars[field] = var
        
        project_frame.columnconfigure(1, weight=1)
        
        # Overhead & Profit Section
        overhead_frame = ttk.LabelFrame(scrollable_costs_frame, text="Overhead & Profit")
        overhead_frame.pack(fill=tk.X, padx=10, pady=5)
        
        overhead_costs = [
            ('General Overhead (% of project cost)', 'general_overhead_percentage'),
            ('Administration Overhead (% of project cost)', 'admin_overhead_percentage'),
            ('Profit Margin (% of total cost)', 'profit_margin_percentage'),
            ('GST/Tax Considerations (% where applicable)', 'tax_percentage')
        ]
        
        for i, (label, field) in enumerate(overhead_costs):
            ttk.Label(overhead_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(overhead_frame, textvariable=var, width=20)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            self.project_costs_vars[field] = var
        
        overhead_frame.columnconfigure(1, weight=1)
        
        # Cost calculation and save button
        calc_frame = ttk.Frame(scrollable_costs_frame)
        calc_frame.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(calc_frame, text="Calculate Total Project Cost", 
                  command=self.calculate_project_costs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(calc_frame, text="Save Project Costs", 
                  command=self.save_project_costs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(calc_frame, text="Clear All Costs", 
                  command=self.clear_project_costs).pack(side=tk.LEFT)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        scrollbar_costs.pack(side="right", fill="y")
    
    def setup_bank_account_tab(self):
        """Setup bank account information tab."""
        self.bank_account_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.bank_account_frame, text="Bank Account")
        
        ttk.Label(self.bank_account_frame, text="Bank Account Information", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Bank account details
        bank_details_frame = ttk.LabelFrame(self.bank_account_frame, text="Account Details")
        bank_details_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.bank_vars = {}
        bank_fields = [
            ('Bank Name', 'bank_name'),
            ('Account Name', 'bank_account_name'),
            ('Account Number', 'bank_account_number')
        ]
        
        for i, (label, field) in enumerate(bank_fields):
            ttk.Label(bank_details_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            
            var = tk.StringVar()
            entry = ttk.Entry(bank_details_frame, textvariable=var, width=40)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
            
            self.bank_vars[field] = var
        
        bank_details_frame.columnconfigure(1, weight=1)
        
        # Bank document evidence section
        bank_docs_frame = ttk.LabelFrame(self.bank_account_frame, text="Bank Statement Evidence")
        bank_docs_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Documents list
        docs_list_frame = ttk.Frame(bank_docs_frame)
        docs_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.bank_docs_tree = ttk.Treeview(docs_list_frame, columns=('Type', 'Filename', 'Size'), show='headings')
        self.bank_docs_tree.heading('Type', text='Document Type')
        self.bank_docs_tree.heading('Filename', text='Filename')
        self.bank_docs_tree.heading('Size', text='File Size')
        
        bank_docs_scrollbar = ttk.Scrollbar(docs_list_frame, orient="vertical", command=self.bank_docs_tree.yview)
        self.bank_docs_tree.configure(yscrollcommand=bank_docs_scrollbar.set)
        
        self.bank_docs_tree.pack(side="left", fill="both", expand=True)
        bank_docs_scrollbar.pack(side="right", fill="y")
        
        # Setup image preview tooltip for bank documents
        self.bank_docs_tooltip = ImagePreviewTooltip(self.bank_docs_tree)
        self.bank_docs_tree.bind('<Button-3>', self.show_bank_doc_preview)  # Right-click for now
        self.bank_docs_tree.bind('<Double-Button-1>', self.show_bank_doc_preview)  # Double-click
        self.bank_docs_tree.bind('<Leave>', self.on_bank_docs_leave)
        
        # Bank account buttons
        bank_btn_frame = ttk.Frame(self.bank_account_frame)
        bank_btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(bank_btn_frame, text="Save Bank Info", command=self.save_bank_account_info).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(bank_btn_frame, text="Upload Bank Document", command=self.upload_bank_document).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(bank_btn_frame, text="Delete Selected Document", command=self.delete_bank_document).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(bank_btn_frame, text="Refresh Documents", command=self.refresh_bank_documents).pack(side=tk.LEFT)
    
    def setup_certifications_tab(self):
        """Setup certifications tab."""
        self.certifications_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.certifications_frame, text="Certifications")
        
        ttk.Label(self.certifications_frame, text="Licenses & Certifications", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        
        # Certifications tree
        cert_list_frame = ttk.Frame(self.certifications_frame)
        cert_list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.cert_tree = ttk.Treeview(cert_list_frame, columns=('Type', 'Name', 'Authority', 'Expiry'), show='headings')
        self.cert_tree.heading('Type', text='Type')
        self.cert_tree.heading('Name', text='Name')
        self.cert_tree.heading('Authority', text='Authority')
        self.cert_tree.heading('Expiry', text='Expiry Date')
        
        cert_scrollbar = ttk.Scrollbar(cert_list_frame, orient="vertical", command=self.cert_tree.yview)
        self.cert_tree.configure(yscrollcommand=cert_scrollbar.set)
        
        self.cert_tree.pack(side="left", fill="both", expand=True)
        cert_scrollbar.pack(side="right", fill="y")
        
        # Certification buttons
        cert_btn_frame = ttk.Frame(self.certifications_frame)
        cert_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(cert_btn_frame, text="Add Certification", command=self.add_certification).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cert_btn_frame, text="Edit Certification", command=self.edit_certification).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cert_btn_frame, text="Remove Certification", command=self.remove_certification).pack(side=tk.LEFT)
    
    def setup_insurance_tab(self):
        """Setup insurance tab."""
        self.insurance_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.insurance_frame, text="Insurance")
        
        ttk.Label(self.insurance_frame, text="Insurance Coverage", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        
        # Insurance tree
        ins_list_frame = ttk.Frame(self.insurance_frame)
        ins_list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.insurance_tree = ttk.Treeview(ins_list_frame, columns=('Type', 'Provider', 'Coverage', 'Expiry'), show='headings')
        self.insurance_tree.heading('Type', text='Type')
        self.insurance_tree.heading('Provider', text='Provider')
        self.insurance_tree.heading('Coverage', text='Coverage Amount')
        self.insurance_tree.heading('Expiry', text='Expiry Date')
        
        ins_scrollbar = ttk.Scrollbar(ins_list_frame, orient="vertical", command=self.insurance_tree.yview)
        self.insurance_tree.configure(yscrollcommand=ins_scrollbar.set)
        
        self.insurance_tree.pack(side="left", fill="both", expand=True)
        ins_scrollbar.pack(side="right", fill="y")
        
        # Insurance buttons
        ins_btn_frame = ttk.Frame(self.insurance_frame)
        ins_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(ins_btn_frame, text="Add Insurance", command=self.add_insurance).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ins_btn_frame, text="Edit Insurance", command=self.edit_insurance).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ins_btn_frame, text="Remove Insurance", command=self.remove_insurance).pack(side=tk.LEFT)
    
    def setup_experience_tab(self):
        """Setup experience tab."""
        self.experience_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.experience_frame, text="Experience")
        
        ttk.Label(self.experience_frame, text="Project Experience", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        
        # Experience tree
        exp_list_frame = ttk.Frame(self.experience_frame)
        exp_list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.experience_tree = ttk.Treeview(exp_list_frame, columns=('Project', 'Client', 'Type', 'Value'), show='headings')
        self.experience_tree.heading('Project', text='Project Name')
        self.experience_tree.heading('Client', text='Client')
        self.experience_tree.heading('Type', text='Type')
        self.experience_tree.heading('Value', text='Value')
        
        exp_scrollbar = ttk.Scrollbar(exp_list_frame, orient="vertical", command=self.experience_tree.yview)
        self.experience_tree.configure(yscrollcommand=exp_scrollbar.set)
        
        self.experience_tree.pack(side="left", fill="both", expand=True)
        exp_scrollbar.pack(side="right", fill="y")
        
        # Experience buttons
        exp_btn_frame = ttk.Frame(self.experience_frame)
        exp_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(exp_btn_frame, text="Add Project", command=self.add_experience).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(exp_btn_frame, text="Edit Project", command=self.edit_experience).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(exp_btn_frame, text="Remove Project", command=self.remove_experience).pack(side=tk.LEFT)
    
    def setup_autofill_tab(self):
        """Setup auto-fill testing tab."""
        self.autofill_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.autofill_frame, text="Auto-Fill Test")
        
        ttk.Label(self.autofill_frame, text="Test Auto-Fill Suggestions", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Question input
        ttk.Label(self.autofill_frame, text="Enter a question or field description:").pack(anchor='w', padx=20)
        
        self.question_var = tk.StringVar()
        question_entry = ttk.Entry(self.autofill_frame, textvariable=self.question_var, width=60)
        question_entry.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(self.autofill_frame, text="Get Suggestions", 
                  command=self.test_autofill).pack(pady=10)
        
        # Results area
        ttk.Label(self.autofill_frame, text="Auto-Fill Suggestions:").pack(anchor='w', padx=20, pady=(20, 5))
        
        # Suggestions tree
        suggestions_frame = ttk.Frame(self.autofill_frame)
        suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        self.suggestions_tree = ttk.Treeview(suggestions_frame, columns=('Category', 'Field', 'Value', 'Confidence'), show='headings')
        self.suggestions_tree.heading('Category', text='Category')
        self.suggestions_tree.heading('Field', text='Field')
        self.suggestions_tree.heading('Value', text='Suggested Value')
        self.suggestions_tree.heading('Confidence', text='Confidence')
        
        sugg_scrollbar = ttk.Scrollbar(suggestions_frame, orient="vertical", command=self.suggestions_tree.yview)
        self.suggestions_tree.configure(yscrollcommand=sugg_scrollbar.set)
        
        self.suggestions_tree.pack(side="left", fill="both", expand=True)
        sugg_scrollbar.pack(side="right", fill="y")
        
        # Sample questions
        sample_frame = ttk.LabelFrame(self.autofill_frame, text="Sample Questions", padding=10)
        sample_frame.pack(fill=tk.X, padx=20, pady=10)
        
        sample_questions = [
            "What is your company ABN?",
            "Provide your annual turnover",
            "List your insurance coverage",
            "Describe your recent project experience",
            "What certifications do you hold?"
        ]
        
        for i, question in enumerate(sample_questions):
            btn = ttk.Button(sample_frame, text=question, 
                           command=lambda q=question: self.set_sample_question(q))
            btn.grid(row=i//2, column=i%2, sticky='ew', padx=2, pady=2)
        
        sample_frame.columnconfigure(0, weight=1)
        sample_frame.columnconfigure(1, weight=1)
    
    def refresh_company_list(self):
        """Refresh the company list."""
        self.company_listbox.delete(0, tk.END)
        companies = self.db_manager.list_companies()
        
        for company in companies:
            self.company_listbox.insert(tk.END, company)
    
    def on_company_select(self, event):
        """Handle company selection."""
        selection = self.company_listbox.curselection()
        if selection:
            company_name = self.company_listbox.get(selection[0])
            self.current_company = company_name
            self.load_company_data(company_name)
    
    def load_company_data(self, company_name: str):
        """Load company data into the form."""
        profile = self.db_manager.get_company_profile(company_name)
        
        if not profile:
            return
        
        # Load company info
        for field, var in self.company_vars.items():
            value = profile.get(field, '')
            if isinstance(var, tk.Text):
                var.delete('1.0', tk.END)
                if value:
                    var.insert('1.0', str(value))
            else:
                var.set(str(value))
        
        # Load contacts
        self.contacts_tree.delete(*self.contacts_tree.get_children())
        for contact in profile.get('contacts', []):
            self.contacts_tree.insert('', 'end', values=(
                contact.get('role', ''),
                f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                contact.get('phone', ''),
                contact.get('email', '')
            ))
        
        # Load financial info
        financial = profile.get('financial', {})
        if hasattr(self, 'financial_vars'):
            for field, var in self.financial_vars.items():
                value = financial.get(field, '')
                # Format numeric values nicely
                if field in ['annual_turnover', 'profit_loss', 'assets_value', 'liabilities_value', 'cash_flow'] and value:
                    try:
                        if isinstance(value, (int, float)) and value != 0:
                            var.set(f"{value:,.0f}")
                        else:
                            var.set(str(value))
                    except:
                        var.set(str(value))
                else:
                    var.set(str(value))
        
        # Load certifications
        self.cert_tree.delete(*self.cert_tree.get_children())
        for cert in profile.get('certifications', []):
            self.cert_tree.insert('', 'end', values=(
                cert.get('certification_type', ''),
                cert.get('name', ''),
                cert.get('issuing_authority', ''),
                cert.get('expiry_date', '')
            ))
        
        # Load insurance
        self.insurance_tree.delete(*self.insurance_tree.get_children())
        for ins in profile.get('insurance', []):
            coverage = ins.get('coverage_amount', 0)
            coverage_str = f"${coverage:,.0f}" if coverage else ''
            self.insurance_tree.insert('', 'end', values=(
                ins.get('insurance_type', ''),
                ins.get('provider', ''),
                coverage_str,
                ins.get('end_date', '')
            ))
        
        # Load experience
        self.experience_tree.delete(*self.experience_tree.get_children())
        for exp in profile.get('experience', []):
            value = exp.get('project_value', 0)
            value_str = f"${value:,.0f}" if value else ''
            self.experience_tree.insert('', 'end', values=(
                exp.get('project_name', ''),
                exp.get('client_name', ''),
                exp.get('project_type', ''),
                value_str
            ))
        
        # Load bank account info
        if hasattr(self, 'bank_vars'):
            bank_info = self.db_manager.get_bank_account_info(company_name)
            for field, var in self.bank_vars.items():
                value = bank_info.get(field, '') if bank_info else ''
                var.set(str(value))
            
            # Load bank documents
            self.refresh_bank_documents()
        
        # Load project costs
        if hasattr(self, 'project_costs_vars'):
            project_costs = self.db_manager.get_project_costs(company_name)
            for field, var in self.project_costs_vars.items():
                value = project_costs.get(field, '') if project_costs else ''
                var.set(str(value))
    
    def save_company_info(self):
        """Save company information."""
        if not self.current_company:
            messagebox.showwarning("No Company", "Please select a company first.")
            return
        
        try:
            # Extract data from form
            company_data = {}
            for field, var in self.company_vars.items():
                if isinstance(var, tk.Text):
                    value = var.get('1.0', tk.END).strip()
                else:
                    value = var.get().strip()
                
                # Store value even if empty to allow clearing fields
                company_data[field] = value if value else None
            
            # Update database
            company_id = self.db_manager.get_or_create_company(self.current_company)
            self.db_manager._update_company_info(company_id, company_data)
            
            # Reload the data to reflect changes
            self.load_company_data(self.current_company)
            
            messagebox.showinfo("Success", "Company information saved and reloaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save company information: {str(e)}")
    
    def save_financial_info(self):
        """Save financial information."""
        if not self.current_company:
            messagebox.showwarning("No Company", "Please select a company first.")
            return
        
        try:
            # Extract financial data
            financial_data = {}
            for field, var in self.financial_vars.items():
                value = var.get().strip()
                if value:
                    # Try to convert numeric fields
                    if field in ['annual_turnover', 'profit_loss', 'assets_value', 'liabilities_value', 'cash_flow']:
                        try:
                            financial_data[field] = float(value.replace(',', '').replace('$', ''))
                        except ValueError:
                            financial_data[field] = value  # Store as string if conversion fails
                    else:
                        financial_data[field] = value
            
            if financial_data:
                company_id = self.db_manager.get_or_create_company(self.current_company)
                self.db_manager._store_financial_info(company_id, financial_data)
                
                # Reload the data to reflect changes
                self.load_company_data(self.current_company)
                
                messagebox.showinfo("Success", "Financial information saved and reloaded successfully!")
            else:
                messagebox.showwarning("No Data", "No financial information to save.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save financial information: {str(e)}")
    
    def test_autofill(self):
        """Test auto-fill suggestions."""
        if not self.current_company:
            messagebox.showwarning("No Company", "Please select a company first.")
            return
        
        question = self.question_var.get().strip()
        if not question:
            messagebox.showwarning("No Question", "Please enter a question.")
            return
        
        # Get suggestions
        suggestions = self.db_manager.get_auto_fill_suggestions(question, self.current_company)
        
        # Clear and populate suggestions tree
        self.suggestions_tree.delete(*self.suggestions_tree.get_children())
        
        for suggestion in suggestions:
            confidence_str = f"{suggestion['confidence']:.1%}"
            self.suggestions_tree.insert('', 'end', values=(
                suggestion['category'],
                suggestion['field'],
                suggestion['value'],
                confidence_str
            ))
        
        if not suggestions:
            messagebox.showinfo("No Suggestions", "No auto-fill suggestions found for this question.")
    
    def set_sample_question(self, question: str):
        """Set a sample question."""
        self.question_var.set(question)
    
    def clear_company_form(self):
        """Clear all company form fields."""
        for field, var in self.company_vars.items():
            if isinstance(var, tk.Text):
                var.delete('1.0', tk.END)
            else:
                var.set('')
        
        # Clear financial form if it exists
        if hasattr(self, 'financial_vars'):
            for field, var in self.financial_vars.items():
                var.set('')
        
        # Clear bank account form if it exists
        if hasattr(self, 'bank_vars'):
            for field, var in self.bank_vars.items():
                var.set('')
        
        # Clear project costs form if it exists
        if hasattr(self, 'project_costs_vars'):
            for field, var in self.project_costs_vars.items():
                var.set('')
        
        # Clear trees
        for tree in [self.contacts_tree, self.cert_tree, self.insurance_tree, self.experience_tree]:
            if tree.winfo_exists():
                tree.delete(*tree.get_children())
        
        # Clear bank documents tree if it exists
        if hasattr(self, 'bank_docs_tree') and self.bank_docs_tree.winfo_exists():
            self.bank_docs_tree.delete(*self.bank_docs_tree.get_children())
    
    def refresh_current_company(self):
        """Refresh the current company data from database."""
        if self.current_company:
            print(f"DEBUG: Refreshing data for {self.current_company}")
            self.load_company_data(self.current_company)
            messagebox.showinfo("Refreshed", f"Data refreshed for {self.current_company}")
        else:
            messagebox.showwarning("No Company", "Please select a company first.")
    
    def add_new_company(self):
        """Add a new company."""
        company_name = simpledialog.askstring("New Company", "Enter company name:")
        if company_name:
            self.db_manager.get_or_create_company(company_name)
            self.refresh_company_list()
            messagebox.showinfo("Success", f"Company '{company_name}' added successfully!")
    
    def import_from_document(self):
        """Import company information from document."""
        if not self.current_company:
            messagebox.showwarning("No Company", "Please select a company first.")
            return
        
        messagebox.showinfo("Coming Soon", "Document import feature coming soon!\n\nThis will extract information from uploaded documents and automatically populate the database.")
    
    def show_database_stats(self):
        """Show database statistics."""
        stats = self.db_manager.get_database_stats()
        
        stats_text = "Database Statistics:\\n\\n"
        for table, count in stats.items():
            table_name = table.replace('_', ' ').title()
            stats_text += f"{table_name}: {count}\\n"
        
        messagebox.showinfo("Database Statistics", stats_text)
    
    # Placeholder methods for other functionality
    def add_contact(self):
        messagebox.showinfo("Coming Soon", "Add contact feature coming soon!")
    
    def edit_contact(self):
        messagebox.showinfo("Coming Soon", "Edit contact feature coming soon!")
    
    def remove_contact(self):
        messagebox.showinfo("Coming Soon", "Remove contact feature coming soon!")
    
    def add_certification(self):
        messagebox.showinfo("Coming Soon", "Add certification feature coming soon!")
    
    def edit_certification(self):
        messagebox.showinfo("Coming Soon", "Edit certification feature coming soon!")
    
    def remove_certification(self):
        messagebox.showinfo("Coming Soon", "Remove certification feature coming soon!")
    
    def add_insurance(self):
        messagebox.showinfo("Coming Soon", "Add insurance feature coming soon!")
    
    def edit_insurance(self):
        messagebox.showinfo("Coming Soon", "Edit insurance feature coming soon!")
    
    def remove_insurance(self):
        messagebox.showinfo("Coming Soon", "Remove insurance feature coming soon!")
    
    def add_experience(self):
        messagebox.showinfo("Coming Soon", "Add experience feature coming soon!")
    
    def edit_experience(self):
        messagebox.showinfo("Coming Soon", "Edit experience feature coming soon!")
    
    def remove_experience(self):
        messagebox.showinfo("Coming Soon", "Remove experience feature coming soon!")
    
    def save_bank_account_info(self):
        """Save bank account information."""
        if not self.current_company:
            messagebox.showwarning("No Company", "Please select a company first.")
            return
        
        try:
            # Get bank account data
            bank_data = {}
            for field, var in self.bank_vars.items():
                bank_data[field] = var.get().strip()
            
            # Update bank account info
            success = self.db_manager.update_bank_account_info(self.current_company, **bank_data)
            
            if success:
                messagebox.showinfo("Success", "Bank account information saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save bank account information.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bank account info: {str(e)}")
    
    def upload_bank_document(self):
        """Upload a bank statement document."""
        if not self.current_company:
            messagebox.showwarning("No Company", "Please select a company first.")
            return
        
        # File selection dialog
        file_path = filedialog.askopenfilename(
            title="Select Bank Statement Document",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Document type selection
        doc_type = simpledialog.askstring(
            "Document Type", 
            "Enter document type (e.g., 'Bank Statement', 'Account Verification'):",
            initialvalue="Bank Statement"
        )
        
        if not doc_type:
            return
        
        try:
            # Extract filename from file path
            import os
            file_name = os.path.basename(file_path)
            
            # Upload document
            success = self.db_manager.upload_bank_document(
                self.current_company, 
                doc_type.strip(),
                file_path,
                file_name
            )
            
            if success:
                messagebox.showinfo("Success", "Bank document uploaded successfully!")
                self.refresh_bank_documents()
            else:
                messagebox.showerror("Error", "Failed to upload bank document.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload document: {str(e)}")
    
    def delete_bank_document(self):
        """Delete selected bank document."""
        selection = self.bank_docs_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a document to delete.")
            return
        
        # Get selected item
        item = self.bank_docs_tree.item(selection[0])
        filename = item['values'][1]  # Filename is in second column
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", f"Delete document '{filename}'?"):
            try:
                # Find document ID by filename (we'll need to get this from the database)
                bank_docs = self.db_manager.get_bank_documents(self.current_company)
                doc_id = None
                for doc in bank_docs:
                    if doc['file_name'] == filename:
                        doc_id = doc['id']
                        break
                
                if doc_id:
                    success = self.db_manager.delete_bank_document(doc_id)
                    if success:
                        messagebox.showinfo("Success", "Document deleted successfully!")
                        self.refresh_bank_documents()
                    else:
                        messagebox.showerror("Error", "Failed to delete document.")
                else:
                    messagebox.showerror("Error", "Could not find document to delete.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete document: {str(e)}")
    
    def refresh_bank_documents(self):
        """Refresh the bank documents list."""
        if not self.current_company:
            return
        
        try:
            # Clear existing items
            self.bank_docs_tree.delete(*self.bank_docs_tree.get_children())
            
            # Get bank documents
            bank_docs = self.db_manager.get_bank_documents(self.current_company)
            
            # Populate tree
            for doc in bank_docs:
                # Format file size
                size_mb = doc['file_size'] / (1024 * 1024) if doc['file_size'] else 0
                size_str = f"{size_mb:.1f} MB" if size_mb > 0 else "Unknown"
                
                self.bank_docs_tree.insert('', 'end', values=(
                    doc['document_type'],
                    doc['file_name'],
                    size_str
                ))
        except Exception as e:
            print(f"Error refreshing bank documents: {e}")
            messagebox.showerror("Error", f"Failed to refresh documents: {str(e)}")
    
    def show_bank_doc_preview(self, event):
        """Show bank document preview on right-click or double-click."""
        try:
            # Get selected item
            selection = self.bank_docs_tree.selection()
            if not selection:
                # If no selection, try to get item under cursor
                item = self.bank_docs_tree.identify_row(event.y)
                if item:
                    self.bank_docs_tree.selection_set(item)
                    selection = [item]
            
            if selection:
                # Get item data
                item_data = self.bank_docs_tree.item(selection[0])
                values = item_data['values']
                
                if len(values) >= 2:
                    doc_type = values[0]
                    filename = values[1]
                    file_size = values[2] if len(values) > 2 else "Unknown"
                    
                    # Find the full file path
                    bank_docs = self.db_manager.get_bank_documents(self.current_company)
                    file_path = None
                    
                    for doc in bank_docs:
                        if doc['file_name'] == filename:
                            file_path = doc['file_path']
                            break
                    
                    # Create tooltip text
                    tooltip_text = f"Document: {filename}\nType: {doc_type}\nSize: {file_size}\n\nRight-click or double-click to preview"
                    
                    # Show tooltip with image preview
                    self.bank_docs_tooltip.hidetip()  # Hide any existing tooltip first
                    self.bank_docs_tooltip.showtip(tooltip_text, file_path)
        except Exception as e:
            print(f"Error in preview handler: {e}")
    
    def on_bank_docs_leave(self, event):
        """Handle mouse leave from bank documents tree."""
        # Add a small delay before hiding tooltip to prevent flickering
        self.bank_docs_tree.after(1000, self.bank_docs_tooltip.hidetip)
    
    def calculate_project_costs(self):
        """Calculate and display total project costs."""
        try:
            total_cost = 0
            breakdown = {}
            
            # Calculate labor costs (convert hourly/daily to project estimates)
            labor_total = 0
            for field, var in self.project_costs_vars.items():
                if field.endswith('_rate') or field.endswith('_costs'):
                    value = var.get().strip()
                    if value:
                        try:
                            amount = float(value.replace('$', '').replace(',', ''))
                            labor_total += amount
                        except ValueError:
                            continue
            
            breakdown['Labor Costs'] = labor_total
            
            # Calculate equipment costs
            equipment_total = 0
            equipment_fields = ['heavy_machinery_rental', 'tools_equipment', 'vehicle_fleet_costs', 
                              'fuel_transport', 'raw_materials', 'safety_equipment', 'technology_licenses']
            
            for field in equipment_fields:
                if field in self.project_costs_vars:
                    value = self.project_costs_vars[field].get().strip()
                    if value:
                        try:
                            amount = float(value.replace('$', '').replace(',', ''))
                            equipment_total += amount
                        except ValueError:
                            continue
            
            breakdown['Equipment & Materials'] = equipment_total
            
            # Calculate operational costs
            operational_total = 0
            operational_fields = ['office_rent', 'site_office_rent', 'utilities', 'communications', 
                                'insurance_premiums', 'professional_services', 'marketing_costs', 'training_costs']
            
            for field in operational_fields:
                if field in self.project_costs_vars:
                    value = self.project_costs_vars[field].get().strip()
                    if value:
                        try:
                            amount = float(value.replace('$', '').replace(',', ''))
                            operational_total += amount
                        except ValueError:
                            continue
            
            breakdown['Operational Costs'] = operational_total
            
            # Calculate project-specific costs
            project_total = 0
            project_fields = ['permits_consents', 'environmental_compliance', 'quality_assurance', 
                            'subcontractor_costs', 'risk_provisions', 'bond_guarantee_costs']
            
            for field in project_fields:
                if field in self.project_costs_vars:
                    value = self.project_costs_vars[field].get().strip()
                    if value:
                        try:
                            amount = float(value.replace('$', '').replace(',', ''))
                            project_total += amount
                        except ValueError:
                            continue
            
            breakdown['Project-Specific Costs'] = project_total
            
            # Calculate subtotal
            subtotal = labor_total + equipment_total + operational_total + project_total
            
            # Apply overhead and profit percentages
            overhead_pct = 0
            profit_pct = 0
            contingency_pct = 0
            
            if 'general_overhead_percentage' in self.project_costs_vars:
                overhead_val = self.project_costs_vars['general_overhead_percentage'].get().strip()
                if overhead_val:
                    try:
                        overhead_pct = float(overhead_val.replace('%', ''))
                    except ValueError:
                        pass
            
            if 'profit_margin_percentage' in self.project_costs_vars:
                profit_val = self.project_costs_vars['profit_margin_percentage'].get().strip()
                if profit_val:
                    try:
                        profit_pct = float(profit_val.replace('%', ''))
                    except ValueError:
                        pass
            
            if 'contingency_percentage' in self.project_costs_vars:
                contingency_val = self.project_costs_vars['contingency_percentage'].get().strip()
                if contingency_val:
                    try:
                        contingency_pct = float(contingency_val.replace('%', ''))
                    except ValueError:
                        pass
            
            overhead_amount = subtotal * (overhead_pct / 100)
            contingency_amount = subtotal * (contingency_pct / 100)
            profit_amount = (subtotal + overhead_amount + contingency_amount) * (profit_pct / 100)
            
            total_cost = subtotal + overhead_amount + contingency_amount + profit_amount
            
            # Display results
            result_text = "Project Cost Breakdown:\\n\\n"
            result_text += f"Labor Costs: ${labor_total:,.2f}\\n"
            result_text += f"Equipment & Materials: ${equipment_total:,.2f}\\n"
            result_text += f"Operational Costs: ${operational_total:,.2f}\\n"
            result_text += f"Project-Specific Costs: ${project_total:,.2f}\\n"
            result_text += f"Subtotal: ${subtotal:,.2f}\\n\\n"
            result_text += f"Overhead ({overhead_pct}%): ${overhead_amount:,.2f}\\n"
            result_text += f"Contingency ({contingency_pct}%): ${contingency_amount:,.2f}\\n"
            result_text += f"Profit ({profit_pct}%): ${profit_amount:,.2f}\\n\\n"
            result_text += f"TOTAL PROJECT COST: ${total_cost:,.2f}"
            
            messagebox.showinfo("Project Cost Calculation", result_text)
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error calculating project costs: {str(e)}")
    
    def save_project_costs(self):
        """Save project costs information."""
        if not self.current_company:
            messagebox.showwarning("No Company", "Please select a company first.")
            return
        
        try:
            # Extract project costs data
            costs_data = {}
            for field, var in self.project_costs_vars.items():
                value = var.get().strip()
                costs_data[field] = value if value else None
            
            # Update database (we'll need to add this method to database manager)
            success = self.db_manager.update_project_costs(self.current_company, costs_data)
            
            if success:
                messagebox.showinfo("Success", "Project costs saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save project costs.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project costs: {str(e)}")
    
    def clear_project_costs(self):
        """Clear all project cost fields."""
        for field, var in self.project_costs_vars.items():
            var.set('')
        messagebox.showinfo("Cleared", "All project cost fields have been cleared.")