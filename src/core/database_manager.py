"""
Database Manager - Store and retrieve reusable application information
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import re

class DatabaseManager:
    """Manage database for storing reusable application information."""
    
    def __init__(self, db_path: str = "data/application_database.db"):
        self.db_path = db_path
        self.ensure_database_directory()
        self.init_database()
    
    def ensure_database_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # Only create directory if path has a directory component
            os.makedirs(db_dir, exist_ok=True)
    
    def init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            # First create tables if they don't exist
            conn.executescript("""
                -- Company/Organization Information
                CREATE TABLE IF NOT EXISTS company_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT UNIQUE,
                    -- Australian identifiers
                    abn TEXT,
                    acn TEXT,
                    -- New Zealand identifiers
                    nzbn TEXT,  -- New Zealand Business Number (13 digits)
                    company_number TEXT,  -- NZ Company Number (7-8 digits)
                    charity_number TEXT,  -- NZ Charity Registration Number (7 digits)
                    gst_number TEXT,  -- NZ GST Number (8-9 digits)
                    -- Common fields
                    business_address TEXT,
                    postal_address TEXT,
                    phone TEXT,
                    email TEXT,
                    website TEXT,
                    established_date TEXT,
                    employees_count TEXT,  -- Changed to TEXT to handle various input formats
                    annual_revenue TEXT,
                    business_type TEXT,
                    industry_sector TEXT,
                    country TEXT DEFAULT 'New Zealand',  -- Country identifier
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Contact People
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    role TEXT,  -- CEO, Director, Project Manager, etc.
                    first_name TEXT,
                    last_name TEXT,
                    title TEXT,
                    phone TEXT,
                    email TEXT,
                    linkedin TEXT,
                    is_primary BOOLEAN DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Certifications and Licenses
                CREATE TABLE IF NOT EXISTS certifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    certification_type TEXT,  -- License, Permit, Certification, etc.
                    name TEXT,
                    issuing_authority TEXT,
                    certificate_number TEXT,
                    issue_date TEXT,
                    expiry_date TEXT,
                    file_path TEXT,  -- Path to certificate file
                    status TEXT DEFAULT 'active',  -- active, expired, pending
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Financial Information
                CREATE TABLE IF NOT EXISTS financial_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    financial_year TEXT,
                    annual_turnover REAL,
                    profit_loss REAL,
                    assets_value REAL,
                    liabilities_value REAL,
                    cash_flow REAL,
                    bank_name TEXT,
                    bank_account TEXT,
                    credit_rating TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Insurance Information
                CREATE TABLE IF NOT EXISTS insurance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    insurance_type TEXT,  -- Public Liability, Professional Indemnity, etc.
                    provider TEXT,
                    policy_number TEXT,
                    coverage_amount REAL,
                    start_date TEXT,
                    end_date TEXT,
                    file_path TEXT,
                    status TEXT DEFAULT 'active',
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Experience and Projects
                CREATE TABLE IF NOT EXISTS experience (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    project_name TEXT,
                    client_name TEXT,
                    project_type TEXT,
                    project_value REAL,
                    start_date TEXT,
                    end_date TEXT,
                    description TEXT,
                    outcomes TEXT,
                    reference_contact TEXT,
                    reference_phone TEXT,
                    reference_email TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Team Members and Qualifications
                CREATE TABLE IF NOT EXISTS team_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    first_name TEXT,
                    last_name TEXT,
                    role TEXT,
                    qualifications TEXT,  -- JSON array of qualifications
                    experience_years INTEGER,
                    specializations TEXT,  -- JSON array
                    cv_file_path TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Equipment and Resources
                CREATE TABLE IF NOT EXISTS equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    equipment_type TEXT,
                    name TEXT,
                    model TEXT,
                    capacity TEXT,
                    condition TEXT,
                    purchase_date TEXT,
                    value REAL,
                    location TEXT,
                    availability TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Document Templates and Responses
                CREATE TABLE IF NOT EXISTS template_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    question_category TEXT,  -- Financial, Technical, Experience, etc.
                    question_keywords TEXT,  -- Keywords that trigger this response
                    response_text TEXT,
                    last_used TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Application History
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    application_type TEXT,  -- Tender, Grant, etc.
                    title TEXT,
                    organization TEXT,
                    submission_date TEXT,
                    status TEXT,  -- submitted, won, lost, pending
                    value REAL,
                    document_path TEXT,
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Bank Account Documents and Evidence
                CREATE TABLE IF NOT EXISTS bank_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    document_type TEXT,  -- 'bank_statement', 'account_verification', 'letterhead' etc
                    file_name TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Project cost breakdown
                CREATE TABLE IF NOT EXISTS project_costs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    -- Labor Costs
                    project_manager_rate REAL,
                    site_supervisor_rate REAL,
                    skilled_trades_rate REAL,
                    general_labor_rate REAL,
                    admin_staff_costs REAL,
                    overtime_rates REAL,
                    holiday_provisions REAL,
                    acc_percentage REAL,
                    kiwisaver_contributions REAL,
                    -- Equipment & Materials
                    heavy_machinery_rental REAL,
                    tools_equipment REAL,
                    vehicle_fleet_costs REAL,
                    fuel_transport REAL,
                    raw_materials REAL,
                    safety_equipment REAL,
                    technology_licenses REAL,
                    -- Operational Costs
                    office_rent REAL,
                    site_office_rent REAL,
                    utilities REAL,
                    communications REAL,
                    insurance_premiums REAL,
                    professional_services REAL,
                    marketing_costs REAL,
                    training_costs REAL,
                    -- Project-Specific Costs
                    permits_consents REAL,
                    environmental_compliance REAL,
                    quality_assurance REAL,
                    subcontractor_costs REAL,
                    contingency_percentage REAL,
                    risk_provisions REAL,
                    bond_guarantee_costs REAL,
                    -- Overhead & Profit
                    general_overhead_percentage REAL,
                    admin_overhead_percentage REAL,
                    profit_margin_percentage REAL,
                    tax_percentage REAL,
                    -- Metadata
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES company_info (id)
                );
                
                -- Create indexes for better performance
                CREATE INDEX IF NOT EXISTS idx_company_name ON company_info(company_name);
                CREATE INDEX IF NOT EXISTS idx_certification_type ON certifications(certification_type);
                CREATE INDEX IF NOT EXISTS idx_insurance_type ON insurance(insurance_type);
                CREATE INDEX IF NOT EXISTS idx_application_type ON applications(application_type);
                CREATE INDEX IF NOT EXISTS idx_template_keywords ON template_responses(question_keywords);
            """)
            
            # Apply database migrations for new columns
            self._apply_migrations(conn)
    
    def get_or_create_company(self, company_name: str) -> int:
        """Get existing company ID or create new company record."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Try to find existing company
            cursor.execute("SELECT id FROM company_info WHERE company_name = ?", (company_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            # Create new company
            cursor.execute("""
                INSERT INTO company_info (company_name, created_date)
                VALUES (?, ?)
            """, (company_name, datetime.now().isoformat()))
            
            return cursor.lastrowid
    
    def extract_and_store_information(self, document_content: str, company_name: str) -> Dict[str, Any]:
        """Extract information from document content and store in database."""
        company_id = self.get_or_create_company(company_name)
        extracted_info = {}
        
        # Extract different types of information
        extracted_info['company'] = self._extract_company_info(document_content, company_id)
        extracted_info['contacts'] = self._extract_contact_info(document_content, company_id)
        extracted_info['financial'] = self._extract_financial_info(document_content, company_id)
        extracted_info['experience'] = self._extract_experience_info(document_content, company_id)
        extracted_info['certifications'] = self._extract_certification_info(document_content, company_id)
        extracted_info['insurance'] = self._extract_insurance_info(document_content, company_id)
        
        return extracted_info
    
    def _extract_company_info(self, content: str, company_id: int) -> Dict[str, Any]:
        """Extract company information from document content."""
        info = {}
        content_lower = content.lower()
        
        # Extract ABN (Australian)
        abn_match = re.search(r'abn[:\s]*(\d{2}\s?\d{3}\s?\d{3}\s?\d{3})', content_lower)
        if abn_match:
            info['abn'] = abn_match.group(1).replace(' ', '')
        
        # Extract ACN (Australian)
        acn_match = re.search(r'acn[:\s]*(\d{3}\s?\d{3}\s?\d{3})', content_lower)
        if acn_match:
            info['acn'] = acn_match.group(1).replace(' ', '')
        
        # Extract NZBN (New Zealand Business Number) - 13 digits
        nzbn_match = re.search(r'(?:nzbn|new zealand business number)[:\s]*(\d{4}\s?\d{3}\s?\d{3}\s?\d{3})', content_lower)
        if nzbn_match:
            info['nzbn'] = nzbn_match.group(1).replace(' ', '')
        
        # Extract Charity Registration Number (New Zealand) - 7 digits
        charity_match = re.search(r'(?:charity|charities)[:\s]*(?:registration[:\s]*)?(?:number[:\s]*)?(\d{7})', content_lower)
        if charity_match:
            info['charity_number'] = charity_match.group(1)
        
        # Extract Company Number (New Zealand) - 7-8 digits
        company_match = re.search(r'(?:company number|nz company)[:\s]*(\d{7,8})', content_lower)
        if company_match:
            info['company_number'] = company_match.group(1)
        
        # Extract GST Number (New Zealand) - 8-9 digits
        gst_match = re.search(r'(?:gst|goods and services tax)[:\s]*(?:number[:\s]*)?(\d{8,9})', content_lower)
        if gst_match:
            info['gst_number'] = gst_match.group(1)
        
        # Extract phone numbers
        phone_patterns = [
            r'(?:phone|tel|telephone)[:\s]*(\(?(?:\+61|0)[2-8]\)?\s?\d{4}\s?\d{4})',
            r'(\(?(?:\+61|0)[2-8]\)?\s?\d{4}\s?\d{4})'
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, content_lower)
            if phone_match:
                info['phone'] = phone_match.group(1)
                break
        
        # Extract email
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
        if email_match:
            info['email'] = email_match.group(1)
        
        # Extract address
        address_patterns = [
            r'address[:\s]*([^\n\r]+(?:\n[^\n\r]+)*?)(?:\n\s*\n|\n\s*[A-Z]|$)',
            r'postal address[:\s]*([^\n\r]+(?:\n[^\n\r]+)*?)(?:\n\s*\n|\n\s*[A-Z]|$)'
        ]
        for pattern in address_patterns:
            address_match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if address_match:
                info['business_address'] = address_match.group(1).strip()
                break
        
        # Update database if we found information
        if info:
            self._update_company_info(company_id, info)
        
        return info
    
    def _extract_contact_info(self, content: str, company_id: int) -> List[Dict[str, Any]]:
        """Extract contact information from document content."""
        contacts = []
        
        # Look for contact patterns
        contact_patterns = [
            r'(?:contact person|project manager|director|ceo)[:\s]*([^\n\r]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+).*?(?:director|manager|ceo|contact)',
        ]
        
        for pattern in contact_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                contact_text = match.group(1).strip()
                if len(contact_text) > 3 and len(contact_text) < 100:
                    # Try to parse name and role
                    parts = contact_text.split()
                    if len(parts) >= 2:
                        contacts.append({
                            'first_name': parts[0],
                            'last_name': parts[-1],
                            'role': 'Contact',
                            'full_text': contact_text
                        })
        
        # Store contacts in database
        for contact in contacts:
            self._store_contact(company_id, contact)
        
        return contacts
    
    def _extract_financial_info(self, content: str, company_id: int) -> Dict[str, Any]:
        """Extract financial information from document content."""
        financial_info = {}
        
        # Extract financial figures
        money_patterns = [
            (r'annual turnover[:\s]*\$?([\d,]+)', 'annual_turnover'),
            (r'revenue[:\s]*\$?([\d,]+)', 'annual_turnover'),
            (r'profit[:\s]*\$?([\d,]+)', 'profit_loss'),
            (r'assets[:\s]*\$?([\d,]+)', 'assets_value'),
        ]
        
        for pattern, field in money_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    financial_info[field] = float(amount_str)
                except ValueError:
                    pass
        
        # Store financial info if found
        if financial_info:
            self._store_financial_info(company_id, financial_info)
        
        return financial_info
    
    def _extract_experience_info(self, content: str, company_id: int) -> List[Dict[str, Any]]:
        """Extract experience and project information."""
        experiences = []
        
        # Look for project descriptions
        project_patterns = [
            r'project[:\s]*([^\n\r]+)',
            r'completed[:\s]*([^\n\r]+)',
            r'delivered[:\s]*([^\n\r]+)',
        ]
        
        for pattern in project_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                project_text = match.group(1).strip()
                if len(project_text) > 10 and len(project_text) < 500:
                    experiences.append({
                        'project_name': project_text[:100],
                        'description': project_text,
                        'project_type': 'Extracted from document'
                    })
        
        # Store experiences
        for exp in experiences:
            self._store_experience(company_id, exp)
        
        return experiences
    
    def _extract_certification_info(self, content: str, company_id: int) -> List[Dict[str, Any]]:
        """Extract certification and license information."""
        certifications = []
        
        cert_patterns = [
            r'(license|licence|permit|certification)[:\s]*([^\n\r]+)',
            r'certified[:\s]*([^\n\r]+)',
            r'accredited[:\s]*([^\n\r]+)',
        ]
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) > 1:
                    cert_type = match.group(1)
                    cert_name = match.group(2).strip()
                else:
                    cert_type = 'Certification'
                    cert_name = match.group(1).strip()
                
                if len(cert_name) > 3 and len(cert_name) < 200:
                    certifications.append({
                        'certification_type': cert_type,
                        'name': cert_name,
                        'status': 'active'
                    })
        
        # Store certifications
        for cert in certifications:
            self._store_certification(company_id, cert)
        
        return certifications
    
    def _extract_insurance_info(self, content: str, company_id: int) -> List[Dict[str, Any]]:
        """Extract insurance information."""
        insurance_info = []
        
        insurance_patterns = [
            r'(public liability|professional indemnity|insurance)[:\s]*\$?([\d,\.]+)',
            r'insured for[:\s]*\$?([\d,\.]+)',
        ]
        
        for pattern in insurance_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                insurance_type = match.group(1)
                amount_str = match.group(2).replace(',', '')
                
                try:
                    coverage_amount = float(amount_str)
                    insurance_info.append({
                        'insurance_type': insurance_type,
                        'coverage_amount': coverage_amount,
                        'status': 'active'
                    })
                except ValueError:
                    pass
        
        # Store insurance info
        for ins in insurance_info:
            self._store_insurance(company_id, ins)
        
        return insurance_info
    
    def _update_company_info(self, company_id: int, info: Dict[str, Any]):
        """Update company information in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query - include all possible company fields
            valid_fields = [
                'company_name', 'abn', 'acn', 'nzbn', 'company_number', 'charity_number', 'gst_number', 
                'phone', 'email', 'business_address', 'postal_address', 'website', 
                'employees_count', 'business_type', 'industry_sector', 'established_date', 
                'country', 'annual_revenue'
            ]
            
            update_fields = []
            values = []
            
            for field, value in info.items():
                if field in valid_fields:
                    update_fields.append(f"{field} = ?")
                    # Handle None values and empty strings
                    if value is None or value == '':
                        values.append(None)
                    else:
                        # Convert to string to ensure compatibility
                        values.append(str(value) if value is not None else None)
            
            if update_fields:
                update_fields.append("updated_date = ?")
                values.append(datetime.now().isoformat())
                values.append(company_id)
                
                query = f"UPDATE company_info SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, values)
                
                # Debug: Log what was updated
                print(f"DEBUG: Updated company {company_id} with {len(update_fields)-1} fields")
                for field, value in zip([f.split(' = ')[0] for f in update_fields[:-1]], values[:-2]):
                    if value:
                        print(f"  {field}: {value}")
    
    def _store_contact(self, company_id: int, contact: Dict[str, Any]):
        """Store contact information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO contacts 
                (company_id, first_name, last_name, role)
                VALUES (?, ?, ?, ?)
            """, (company_id, contact.get('first_name', ''), 
                  contact.get('last_name', ''), contact.get('role', 'Contact')))
    
    def _store_financial_info(self, company_id: int, financial: Dict[str, Any]):
        """Store financial information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if record exists for current year
            current_year = str(datetime.now().year)
            cursor.execute("""
                SELECT id FROM financial_info 
                WHERE company_id = ? AND financial_year = ?
            """, (company_id, current_year))
            
            if cursor.fetchone():
                # Update existing record
                update_fields = []
                values = []
                for field, value in financial.items():
                    update_fields.append(f"{field} = ?")
                    values.append(value)
                
                if update_fields:
                    values.extend([company_id, current_year])
                    query = f"""
                        UPDATE financial_info SET {', '.join(update_fields)}
                        WHERE company_id = ? AND financial_year = ?
                    """
                    cursor.execute(query, values)
            else:
                # Insert new record
                financial['company_id'] = company_id
                financial['financial_year'] = current_year
                
                fields = list(financial.keys())
                placeholders = ', '.join(['?' for _ in fields])
                values = list(financial.values())
                
                query = f"""
                    INSERT INTO financial_info ({', '.join(fields)})
                    VALUES ({placeholders})
                """
                cursor.execute(query, values)
    
    def _store_experience(self, company_id: int, experience: Dict[str, Any]):
        """Store experience information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO experience 
                (company_id, project_name, description, project_type)
                VALUES (?, ?, ?, ?)
            """, (company_id, experience.get('project_name', ''),
                  experience.get('description', ''), experience.get('project_type', '')))
    
    def _store_certification(self, company_id: int, cert: Dict[str, Any]):
        """Store certification information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO certifications 
                (company_id, certification_type, name, status)
                VALUES (?, ?, ?, ?)
            """, (company_id, cert.get('certification_type', ''),
                  cert.get('name', ''), cert.get('status', 'active')))
    
    def _store_insurance(self, company_id: int, insurance: Dict[str, Any]):
        """Store insurance information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO insurance 
                (company_id, insurance_type, coverage_amount, status)
                VALUES (?, ?, ?, ?)
            """, (company_id, insurance.get('insurance_type', ''),
                  insurance.get('coverage_amount', 0), insurance.get('status', 'active')))
    
    def get_company_profile(self, company_name: str) -> Dict[str, Any]:
        """Get complete company profile from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get company info
            cursor.execute("SELECT * FROM company_info WHERE company_name = ?", (company_name,))
            company = cursor.fetchone()
            
            if not company:
                return {}
            
            company_id = company['id']
            profile = dict(company)
            
            # Get related information
            cursor.execute("SELECT * FROM contacts WHERE company_id = ?", (company_id,))
            profile['contacts'] = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT * FROM certifications WHERE company_id = ? AND status = 'active'", (company_id,))
            profile['certifications'] = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT * FROM insurance WHERE company_id = ? AND status = 'active'", (company_id,))
            profile['insurance'] = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT * FROM financial_info WHERE company_id = ? ORDER BY financial_year DESC LIMIT 1", (company_id,))
            financial = cursor.fetchone()
            profile['financial'] = dict(financial) if financial else {}
            
            cursor.execute("SELECT * FROM experience WHERE company_id = ? ORDER BY created_date DESC", (company_id,))
            profile['experience'] = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT * FROM team_members WHERE company_id = ?", (company_id,))
            profile['team_members'] = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT * FROM equipment WHERE company_id = ?", (company_id,))
            profile['equipment'] = [dict(row) for row in cursor.fetchall()]
            
            return profile
    
    def get_auto_fill_suggestions(self, question_text: str, company_name: str) -> List[Dict[str, Any]]:
        """Get auto-fill suggestions based on question content."""
        profile = self.get_company_profile(company_name)
        suggestions = []
        
        if not profile:
            return suggestions
        
        question_lower = question_text.lower()
        
        # Company information suggestions
        if any(keyword in question_lower for keyword in ['company', 'organization', 'business', 'abn', 'acn', 'nzbn', 'charity', 'gst']):
            # Prioritize New Zealand identifiers for NZ forms
            if profile.get('nzbn'):
                suggestions.append({
                    'category': 'NZ Business Info',
                    'field': 'NZBN',
                    'value': profile['nzbn'],
                    'confidence': 0.95
                })
            
            if profile.get('company_number'):
                suggestions.append({
                    'category': 'NZ Business Info',
                    'field': 'Company Number',
                    'value': profile['company_number'],
                    'confidence': 0.9
                })
            
            if profile.get('charity_number'):
                suggestions.append({
                    'category': 'NZ Business Info',
                    'field': 'Charity Number',
                    'value': profile['charity_number'],
                    'confidence': 0.9
                })
            
            if profile.get('gst_number'):
                suggestions.append({
                    'category': 'NZ Business Info',
                    'field': 'GST Number',
                    'value': profile['gst_number'],
                    'confidence': 0.9
                })
            
            # Australian identifiers (lower priority for NZ forms)
            if profile.get('abn'):
                suggestions.append({
                    'category': 'Australian Business Info',
                    'field': 'ABN',
                    'value': profile['abn'],
                    'confidence': 0.8
                })
            
            if profile.get('business_address'):
                suggestions.append({
                    'category': 'Company Info',
                    'field': 'Business Address',
                    'value': profile['business_address'],
                    'confidence': 0.8
                })
        
        # Contact information suggestions
        if any(keyword in question_lower for keyword in ['contact', 'phone', 'email', 'representative']):
            if profile.get('phone'):
                suggestions.append({
                    'category': 'Contact',
                    'field': 'Phone',
                    'value': profile['phone'],
                    'confidence': 0.9
                })
            
            if profile.get('email'):
                suggestions.append({
                    'category': 'Contact',
                    'field': 'Email',
                    'value': profile['email'],
                    'confidence': 0.9
                })
        
        # Financial suggestions
        if any(keyword in question_lower for keyword in ['turnover', 'revenue', 'financial', 'income']):
            financial = profile.get('financial', {})
            if financial.get('annual_turnover'):
                suggestions.append({
                    'category': 'Financial',
                    'field': 'Annual Turnover',
                    'value': f"${financial['annual_turnover']:,.0f}",
                    'confidence': 0.8
                })
        
        # Insurance suggestions
        if any(keyword in question_lower for keyword in ['insurance', 'liability', 'coverage', 'indemnity']):
            for insurance in profile.get('insurance', []):
                suggestions.append({
                    'category': 'Insurance',
                    'field': insurance['insurance_type'],
                    'value': f"${insurance['coverage_amount']:,.0f}",
                    'confidence': 0.8
                })
        
        # Experience suggestions
        if any(keyword in question_lower for keyword in ['experience', 'project', 'previous', 'similar']):
            for exp in profile.get('experience', [])[:3]:  # Top 3 experiences
                suggestions.append({
                    'category': 'Experience',
                    'field': 'Project',
                    'value': exp['project_name'],
                    'confidence': 0.7
                })
        
        # Certification suggestions
        if any(keyword in question_lower for keyword in ['license', 'permit', 'certification', 'qualified']):
            for cert in profile.get('certifications', []):
                suggestions.append({
                    'category': 'Certifications',
                    'field': cert['certification_type'],
                    'value': cert['name'],
                    'confidence': 0.8
                })
        
        return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)
    
    def list_companies(self) -> List[str]:
        """Get list of all companies in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT company_name FROM company_info ORDER BY company_name")
            return [row[0] for row in cursor.fetchall()]
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            tables = ['company_info', 'contacts', 'certifications', 'financial_info', 
                     'insurance', 'experience', 'team_members', 'equipment', 'applications']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            
            return stats
    
    def _apply_migrations(self, conn):
        """Apply database migrations for new columns."""
        cursor = conn.cursor()
        
        # Check which columns exist in company_info table
        cursor.execute("PRAGMA table_info(company_info)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # List of new columns to add
        new_columns = {
            'nzbn': 'TEXT',
            'company_number': 'TEXT', 
            'charity_number': 'TEXT',
            'gst_number': 'TEXT',
            'country': 'TEXT DEFAULT "New Zealand"',
            'postal_address': 'TEXT',
            'annual_revenue': 'TEXT',
            # Bank Account Information
            'bank_name': 'TEXT',
            'bank_account_name': 'TEXT',
            'bank_account_number': 'TEXT',
            'bank_statement_image': 'TEXT'  # Path to uploaded bank statement image
        }
        
        # Add missing columns
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE company_info ADD COLUMN {column_name} {column_type}")
                    print(f"DEBUG: Added column {column_name} to company_info table")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"DEBUG: Failed to add column {column_name}: {e}")
        
        conn.commit()
    
    def update_bank_account_info(self, company_name: str, **kwargs) -> bool:
        """Update bank account information for a company."""
        try:
            company_id = self.get_or_create_company(company_name)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update bank account fields
                cursor.execute("""
                    UPDATE company_info 
                    SET bank_name = ?, 
                        bank_account_name = ?, 
                        bank_account_number = ?,
                        bank_statement_image = ?,
                        updated_date = ?
                    WHERE id = ?
                """, (
                    kwargs.get('bank_name', ''),
                    kwargs.get('bank_account_name', ''),
                    kwargs.get('bank_account_number', ''),
                    kwargs.get('bank_statement_image', ''),
                    datetime.now().isoformat(),
                    company_id
                ))
                
                conn.commit()
                print(f"DEBUG: Updated bank account info for company {company_name}")
                return True
                
        except Exception as e:
            print(f"Error updating bank account info: {e}")
            return False
    
    def upload_bank_document(self, company_name: str, document_type: str, file_path: str, 
                           file_name: str, description: str = "") -> bool:
        """Upload and store bank document information."""
        try:
            company_id = self.get_or_create_company(company_name)
            
            # Get file size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO bank_documents 
                    (company_id, document_type, file_name, file_path, file_size, description, upload_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id,
                    document_type,
                    file_name,
                    file_path,
                    file_size,
                    description,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                print(f"DEBUG: Uploaded bank document {file_name} for company {company_name}")
                return True
                
        except Exception as e:
            print(f"Error uploading bank document: {e}")
            return False
    
    def get_bank_account_info(self, company_name: str) -> Dict[str, str]:
        """Get bank account information for a company."""
        try:
            company_id = self.get_or_create_company(company_name)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT bank_name, bank_account_name, bank_account_number, bank_statement_image
                    FROM company_info WHERE id = ?
                """, (company_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'bank_name': result[0] or '',
                        'bank_account_name': result[1] or '',
                        'bank_account_number': result[2] or '',
                        'bank_statement_image': result[3] or ''
                    }
                
        except Exception as e:
            print(f"Error getting bank account info: {e}")
        
        return {
            'bank_name': '',
            'bank_account_name': '',
            'bank_account_number': '',
            'bank_statement_image': ''
        }
    
    def get_bank_documents(self, company_name: str) -> List[Dict[str, Any]]:
        """Get all bank documents for a company."""
        try:
            company_id = self.get_or_create_company(company_name)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, document_type, file_name, file_path, file_size, 
                           upload_date, description
                    FROM bank_documents WHERE company_id = ?
                    ORDER BY upload_date DESC
                """, (company_id,))
                
                results = cursor.fetchall()
                documents = []
                
                for row in results:
                    documents.append({
                        'id': row[0],
                        'document_type': row[1],
                        'file_name': row[2],
                        'file_path': row[3],
                        'file_size': row[4],
                        'upload_date': row[5],
                        'description': row[6]
                    })
                
                return documents
                
        except Exception as e:
            print(f"Error getting bank documents: {e}")
            return []
    
    def delete_bank_document(self, document_id: int) -> bool:
        """Delete a bank document record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get file path before deleting
                cursor.execute("SELECT file_path FROM bank_documents WHERE id = ?", (document_id,))
                result = cursor.fetchone()
                
                if result:
                    file_path = result[0]
                    
                    # Delete database record
                    cursor.execute("DELETE FROM bank_documents WHERE id = ?", (document_id,))
                    conn.commit()
                    
                    # Try to delete actual file
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except:
                        pass  # File deletion failed, but database record is removed
                    
                    print(f"DEBUG: Deleted bank document {document_id}")
                    return True
                
        except Exception as e:
            print(f"Error deleting bank document: {e}")
        
        return False
    
    def update_project_costs(self, company_name: str, costs_data: Dict[str, Any]) -> bool:
        """Update project costs information for a company."""
        try:
            company_id = self.get_or_create_company(company_name)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if project costs exist for this company
                cursor.execute("SELECT id FROM project_costs WHERE company_id = ?", (company_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing project costs
                    update_fields = []
                    update_values = []
                    
                    for field, value in costs_data.items():
                        if value is not None and value != '':
                            update_fields.append(f"{field} = ?")
                            # Convert to float if it's a numeric field
                            try:
                                clean_value = str(value).replace('$', '').replace(',', '').replace('%', '')
                                if clean_value:
                                    update_values.append(float(clean_value))
                                else:
                                    update_values.append(None)
                            except ValueError:
                                update_values.append(None)
                    
                    update_fields.append("updated_date = ?")
                    update_values.append(datetime.now().isoformat())
                    update_values.append(company_id)
                    
                    update_sql = f"UPDATE project_costs SET {', '.join(update_fields)} WHERE company_id = ?"
                    cursor.execute(update_sql, update_values)
                    
                else:
                    # Insert new project costs record
                    fields = list(costs_data.keys())
                    values = []
                    
                    for field in fields:
                        value = costs_data[field]
                        if value is not None and value != '':
                            try:
                                clean_value = str(value).replace('$', '').replace(',', '').replace('%', '')
                                if clean_value:
                                    values.append(float(clean_value))
                                else:
                                    values.append(None)
                            except ValueError:
                                values.append(None)
                        else:
                            values.append(None)
                    
                    placeholders = ', '.join(['?' for _ in fields])
                    fields_str = ', '.join(fields)
                    
                    cursor.execute(f"""
                        INSERT INTO project_costs (company_id, {fields_str}, created_date, updated_date)
                        VALUES (?, {placeholders}, ?, ?)
                    """, [company_id] + values + [datetime.now().isoformat(), datetime.now().isoformat()])
                
                conn.commit()
                print(f"DEBUG: Updated project costs for company {company_name}")
                return True
                
        except Exception as e:
            print(f"Error updating project costs: {e}")
            return False
    
    def get_project_costs(self, company_name: str) -> Dict[str, Any]:
        """Get project costs information for a company."""
        try:
            company_id = self.get_or_create_company(company_name)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM project_costs WHERE company_id = ?", (company_id,))
                result = cursor.fetchone()
                
                if result:
                    columns = [description[0] for description in cursor.description]
                    costs_dict = dict(zip(columns, result))
                    
                    # Remove metadata fields from returned data
                    costs_dict.pop('id', None)
                    costs_dict.pop('company_id', None)
                    costs_dict.pop('created_date', None)
                    costs_dict.pop('updated_date', None)
                    
                    # Convert None values to empty strings for GUI display
                    for key, value in costs_dict.items():
                        if value is None:
                            costs_dict[key] = ''
                        else:
                            costs_dict[key] = str(value)
                    
                    return costs_dict
                else:
                    return {}
                    
        except Exception as e:
            print(f"Error getting project costs: {e}")
            return {}