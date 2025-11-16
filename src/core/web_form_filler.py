"""
Web Form Auto-Fill System - Automatically fill online forms with database information
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import time
import re
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
from bs4 import BeautifulSoup

class WebFormAutoFill:
    """Automatically fill web forms using database information."""
    
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.driver = None
        self.current_company = None
        
        # Common form field patterns and their database mappings
        self.field_mappings = {
            # Company Information
            r'company[_\s]?name|organization[_\s]?name|business[_\s]?name|organisation[_\s]?name': 'company_name',
            
            # Australian Business Identifiers
            r'abn|australian[_\s]?business[_\s]?number': 'abn',
            r'acn|australian[_\s]?company[_\s]?number': 'acn',
            
            # New Zealand Business Identifiers
            r'nzbn|new[_\s]?zealand[_\s]?business[_\s]?number': 'nzbn',
            r'company[_\s]?number|nz[_\s]?company[_\s]?number': 'company_number',
            r'charity[_\s]?number|charity[_\s]?registration|charities[_\s]?number': 'charity_number',
            r'gst[_\s]?number|goods[_\s]?and[_\s]?services[_\s]?tax': 'gst_number',
            
            # Address and Contact
            r'business[_\s]?address|company[_\s]?address|address': 'business_address',
            r'postal[_\s]?address|mailing[_\s]?address': 'postal_address',
            r'phone|telephone|contact[_\s]?number': 'phone',
            r'email|e[-_\s]?mail': 'email',
            r'website|web[_\s]?site|url': 'website',
            
            # Financial Information
            r'annual[_\s]?turnover|yearly[_\s]?revenue|annual[_\s]?revenue': 'annual_turnover',
            r'assets?[_\s]?value|total[_\s]?assets': 'assets_value',
            r'profit|net[_\s]?income': 'profit_loss',
            r'bank[_\s]?name|banking[_\s]?institution': 'bank_name',
            
            # Contact Information
            r'contact[_\s]?person|primary[_\s]?contact|representative': 'primary_contact_name',
            r'contact[_\s]?phone|rep[_\s]?phone': 'contact_phone',
            r'contact[_\s]?email|rep[_\s]?email': 'contact_email',
            
            # Business Details
            r'employees?[_\s]?count|staff[_\s]?size|number[_\s]?of[_\s]?employees': 'employees_count',
            r'business[_\s]?type|company[_\s]?type|organization[_\s]?type': 'business_type',
            r'industry|sector|business[_\s]?sector': 'industry_sector',
            r'established|founded|start[_\s]?date': 'established_date',
        }
        
        # Insurance field patterns
        self.insurance_patterns = {
            r'public[_\s]?liability|general[_\s]?liability': 'Public Liability',
            r'professional[_\s]?indemnity|pi[_\s]?insurance': 'Professional Indemnity',
            r'workers?[_\s]?comp|workers?[_\s]?compensation': 'Workers Compensation',
            r'product[_\s]?liability': 'Product Liability',
        }
    
    def setup_browser(self) -> bool:
        """Setup Chrome browser with appropriate options."""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Try to use Chrome (adjust path if needed)
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return True
            except WebDriverException:
                messagebox.showerror("Browser Error", 
                    "Chrome browser not found. Please install Chrome or update the Chrome driver path.")
                return False
                
        except Exception as e:
            messagebox.showerror("Setup Error", f"Failed to setup browser: {str(e)}")
            return False
    
    def open_form_url(self, url: str, company_name: str) -> bool:
        """Open a web form URL and prepare for auto-filling."""
        self.current_company = company_name
        
        if not self.driver:
            if not self.setup_browser():
                return False
        
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            return True
            
        except TimeoutException:
            messagebox.showwarning("Page Load", "No forms found on this page or page took too long to load.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open URL: {str(e)}")
            return False
    
    def analyze_form_fields(self) -> Dict[str, Any]:
        """Analyze the current form and identify fillable fields."""
        if not self.driver:
            return {}
        
        form_analysis = {
            'detected_fields': [],
            'fillable_fields': [],
            'form_info': {}
        }
        
        try:
            # Find all input fields
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            
            all_fields = inputs + textareas + selects
            
            for field in all_fields:
                try:
                    field_info = self.analyze_field(field)
                    if field_info:
                        form_analysis['detected_fields'].append(field_info)
                        
                        # Check if we can fill this field
                        suggested_data = self.get_field_data(field_info)
                        if suggested_data:
                            field_info['suggested_value'] = suggested_data
                            field_info['confidence'] = suggested_data.get('confidence', 0.5)
                            form_analysis['fillable_fields'].append(field_info)
                
                except Exception as e:
                    continue
            
            # Get form metadata
            try:
                form_element = self.driver.find_element(By.TAG_NAME, "form")
                form_analysis['form_info'] = {
                    'action': form_element.get_attribute('action') or 'Not specified',
                    'method': form_element.get_attribute('method') or 'GET',
                    'title': self.driver.title,
                    'url': self.driver.current_url
                }
            except:
                pass
            
            return form_analysis
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze form: {str(e)}")
            return {}
    
    def analyze_field(self, field) -> Optional[Dict[str, Any]]:
        """Analyze a single form field to determine its purpose."""
        try:
            field_info = {
                'element': field,
                'tag': field.tag_name,
                'type': field.get_attribute('type') or 'text',
                'id': field.get_attribute('id') or '',
                'name': field.get_attribute('name') or '',
                'placeholder': field.get_attribute('placeholder') or '',
                'label': '',
                'required': field.get_attribute('required') is not None,
                'value': field.get_attribute('value') or ''
            }
            
            # Try to find associated label
            try:
                if field_info['id']:
                    label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_info['id']}']")
                    field_info['label'] = label.text.strip()
            except:
                # Try to find nearby label
                try:
                    parent = field.find_element(By.XPATH, "..")
                    label_elements = parent.find_elements(By.TAG_NAME, "label")
                    if label_elements:
                        field_info['label'] = label_elements[0].text.strip()
                except:
                    pass
            
            # Skip hidden fields and buttons
            if field_info['type'] in ['hidden', 'submit', 'button', 'reset']:
                return None
            
            # Skip fields that already have values (unless it's a default placeholder)
            if field_info['value'] and field_info['value'] != field_info['placeholder']:
                return None
            
            return field_info
            
        except Exception:
            return None
    
    def get_field_data(self, field_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get appropriate data for a field based on its characteristics."""
        if not self.current_company:
            return None
        
        # Get company profile
        profile = self.db_manager.get_company_profile(self.current_company)
        if not profile:
            return None
        
        # Combine all field identifiers for matching
        field_identifiers = " ".join([
            field_info.get('id', ''),
            field_info.get('name', ''),
            field_info.get('label', ''),
            field_info.get('placeholder', '')
        ]).lower()
        
        if not field_identifiers.strip():
            return None
        
        # Check against field mappings
        for pattern, db_field in self.field_mappings.items():
            if re.search(pattern, field_identifiers, re.IGNORECASE):
                value = profile.get(db_field)
                if value:
                    return {
                        'value': str(value),
                        'source': db_field,
                        'confidence': 0.9
                    }
        
        # Check insurance patterns
        for pattern, insurance_type in self.insurance_patterns.items():
            if re.search(pattern, field_identifiers, re.IGNORECASE):
                insurance_list = profile.get('insurance', [])
                for ins in insurance_list:
                    if ins.get('insurance_type') == insurance_type:
                        if 'amount' in field_identifiers or 'coverage' in field_identifiers:
                            return {
                                'value': f"${ins.get('coverage_amount', 0):,.0f}",
                                'source': f'{insurance_type} Coverage',
                                'confidence': 0.8
                            }
                        else:
                            return {
                                'value': ins.get('provider', insurance_type),
                                'source': f'{insurance_type} Provider',
                                'confidence': 0.8
                            }
        
        # Check for contact information
        contacts = profile.get('contacts', [])
        if contacts and re.search(r'contact|representative', field_identifiers, re.IGNORECASE):
            primary_contact = contacts[0]  # Use first contact as primary
            
            if re.search(r'name', field_identifiers):
                full_name = f"{primary_contact.get('first_name', '')} {primary_contact.get('last_name', '')}".strip()
                if full_name:
                    return {
                        'value': full_name,
                        'source': 'Primary Contact Name',
                        'confidence': 0.8
                    }
            
            if re.search(r'phone', field_identifiers):
                phone = primary_contact.get('phone')
                if phone:
                    return {
                        'value': phone,
                        'source': 'Primary Contact Phone',
                        'confidence': 0.8
                    }
        
        return None
    
    def auto_fill_form(self, fill_fields: List[str] = None) -> Dict[str, Any]:
        """Automatically fill the form with database information."""
        if not self.driver or not self.current_company:
            return {'success': False, 'message': 'Browser not initialized or no company selected'}
        
        form_analysis = self.analyze_form_fields()
        if not form_analysis.get('fillable_fields'):
            return {'success': False, 'message': 'No fillable fields detected'}
        
        results = {
            'success': True,
            'filled_fields': [],
            'failed_fields': [],
            'total_fields': len(form_analysis['fillable_fields'])
        }
        
        for field_info in form_analysis['fillable_fields']:
            # Skip if specific fields requested and this isn't one of them
            if fill_fields and field_info.get('name') not in fill_fields:
                continue
            
            try:
                element = field_info['element']
                suggested_value = field_info.get('suggested_value', {})
                value = suggested_value.get('value', '')
                
                if not value:
                    continue
                
                # Fill the field based on its type
                if field_info['tag'] == 'select':
                    # Handle dropdown selections
                    self.select_dropdown_option(element, value)
                elif field_info['type'] in ['checkbox', 'radio']:
                    # Handle checkboxes and radio buttons
                    if value.lower() in ['true', 'yes', '1', 'on']:
                        if not element.is_selected():
                            element.click()
                else:
                    # Handle text inputs and textareas
                    element.clear()
                    element.send_keys(value)
                
                results['filled_fields'].append({
                    'field': field_info.get('name') or field_info.get('id', 'Unknown'),
                    'label': field_info.get('label', ''),
                    'value': value,
                    'source': suggested_value.get('source', 'Database')
                })
                
                # Small delay between fields
                time.sleep(0.1)
                
            except Exception as e:
                results['failed_fields'].append({
                    'field': field_info.get('name') or field_info.get('id', 'Unknown'),
                    'error': str(e)
                })
        
        results['message'] = f"Filled {len(results['filled_fields'])} of {results['total_fields']} fields"
        return results
    
    def select_dropdown_option(self, select_element, target_value: str):
        """Select an option in a dropdown that best matches the target value."""
        try:
            from selenium.webdriver.support.ui import Select
            select = Select(select_element)
            
            # Try exact match first
            try:
                select.select_by_value(target_value)
                return
            except:
                pass
            
            # Try visible text match
            try:
                select.select_by_visible_text(target_value)
                return
            except:
                pass
            
            # Try partial match
            options = select.options
            target_lower = target_value.lower()
            
            for option in options:
                option_text = option.text.lower()
                option_value = option.get_attribute('value').lower()
                
                if target_lower in option_text or target_lower in option_value:
                    select.select_by_visible_text(option.text)
                    return
                    
        except Exception:
            pass
    
    def get_form_preview(self, url: str) -> Dict[str, Any]:
        """Get a preview of form fields without opening browser (using requests)."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all forms
            forms = soup.find_all('form')
            if not forms:
                return {'success': False, 'message': 'No forms found on page'}
            
            form_data = {
                'success': True,
                'title': soup.title.string if soup.title else 'Unknown',
                'forms': []
            }
            
            for i, form in enumerate(forms):
                form_info = {
                    'form_index': i,
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET'),
                    'fields': []
                }
                
                # Find all input fields
                inputs = form.find_all(['input', 'textarea', 'select'])
                for field in inputs:
                    field_type = field.get('type', 'text')
                    
                    if field_type not in ['hidden', 'submit', 'button', 'reset']:
                        field_info = {
                            'name': field.get('name', ''),
                            'id': field.get('id', ''),
                            'type': field_type,
                            'placeholder': field.get('placeholder', ''),
                            'required': field.has_attr('required'),
                            'label': ''
                        }
                        
                        # Try to find label
                        if field_info['id']:
                            label = soup.find('label', {'for': field_info['id']})
                            if label:
                                field_info['label'] = label.get_text(strip=True)
                        
                        form_info['fields'].append(field_info)
                
                form_data['forms'].append(form_info)
            
            return form_data
            
        except requests.RequestException as e:
            return {'success': False, 'message': f'Failed to load page: {str(e)}'}
        except Exception as e:
            return {'success': False, 'message': f'Error analyzing page: {str(e)}'}
    
    def close_browser(self):
        """Close the browser and cleanup."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None


class WebFormWindow:
    """GUI window for web form auto-fill functionality."""
    
    def __init__(self, parent, database_manager):
        self.parent = parent
        self.db_manager = database_manager
        self.web_filler = WebFormAutoFill(database_manager)
        self.window = None
        
    def show_web_form_window(self):
        """Show the web form auto-fill window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Web Form Auto-Fill")
        self.window.geometry("800x600")
        self.window.transient(self.parent)
        
        self.setup_gui()
        
        # Cleanup on close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_gui(self):
        """Setup the web form GUI."""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # URL and company selection frame
        setup_frame = ttk.LabelFrame(main_frame, text="Setup", padding=10)
        setup_frame.pack(fill=tk.X, pady=(0, 10))
        
        # URL input
        ttk.Label(setup_frame, text="Form URL:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(setup_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=0, column=1, sticky='ew', padx=(0, 5))
        
        ttk.Button(setup_frame, text="Preview Form", 
                  command=self.preview_form).grid(row=0, column=2, padx=5)
        
        # Company selection
        ttk.Label(setup_frame, text="Company:").grid(row=1, column=0, sticky='w', padx=(0, 5), pady=(10, 0))
        self.company_var = tk.StringVar()
        company_combo = ttk.Combobox(setup_frame, textvariable=self.company_var, width=47)
        company_combo.grid(row=1, column=1, sticky='ew', padx=(0, 5), pady=(10, 0))
        
        # Load companies
        companies = self.db_manager.list_companies()
        company_combo['values'] = companies
        if companies:
            company_combo.set(companies[0])
        
        ttk.Button(setup_frame, text="Open Form", 
                  command=self.open_form).grid(row=1, column=2, padx=5, pady=(10, 0))
        
        setup_frame.columnconfigure(1, weight=1)
        
        # Sample URLs frame
        samples_frame = ttk.LabelFrame(main_frame, text="Sample Grant/Tender URLs", padding=10)
        samples_frame.pack(fill=tk.X, pady=(0, 10))
        
        sample_urls = [
            ("Kiwi Gaming Grant (Sample)", "https://forms.gov.au/sample-gaming-grant"),
            ("Business Grant Application", "https://business.gov.au/grants/sample-form"),
            ("Local Council Tender", "https://council.gov.au/tender-application"),
        ]
        
        for i, (name, url) in enumerate(sample_urls):
            btn = ttk.Button(samples_frame, text=name, 
                           command=lambda u=url: self.set_url(u))
            btn.grid(row=i//2, column=i%2, sticky='ew', padx=2, pady=2)
        
        samples_frame.columnconfigure(0, weight=1)
        samples_frame.columnconfigure(1, weight=1)
        
        # Form analysis frame
        analysis_frame = ttk.LabelFrame(main_frame, text="Form Analysis", padding=10)
        analysis_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons
        btn_frame = ttk.Frame(analysis_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Analyze Fields", 
                  command=self.analyze_form).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Auto-Fill All", 
                  command=self.auto_fill_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Fill Selected", 
                  command=self.fill_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear Results", 
                  command=self.clear_results).pack(side=tk.LEFT)
        
        # Results tree
        columns = ('Field', 'Label', 'Type', 'Suggested Value', 'Confidence', 'Fill')
        self.results_tree = ttk.Treeview(analysis_frame, columns=columns, show='headings')
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            if col == 'Suggested Value':
                self.results_tree.column(col, width=200)
            elif col == 'Fill':
                self.results_tree.column(col, width=50)
            else:
                self.results_tree.column(col, width=100)
        
        # Scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Enter a form URL to begin")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set_url(self, url: str):
        """Set URL in the entry field."""
        self.url_var.set(url)
    
    def preview_form(self):
        """Preview form fields without opening browser."""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a form URL.")
            return
        
        self.status_var.set("Previewing form...")
        self.window.update()
        
        try:
            preview_data = self.web_filler.get_form_preview(url)
            
            if not preview_data.get('success'):
                messagebox.showerror("Preview Failed", preview_data.get('message', 'Unknown error'))
                self.status_var.set("Ready")
                return
            
            # Clear existing results
            self.clear_results()
            
            # Show preview results
            forms = preview_data.get('forms', [])
            total_fields = 0
            
            for form in forms:
                for field in form.get('fields', []):
                    total_fields += 1
                    self.results_tree.insert('', 'end', values=(
                        field.get('name', 'N/A'),
                        field.get('label', ''),
                        field.get('type', 'text'),
                        'Preview mode - no suggestions',
                        'N/A',
                        '☐'
                    ))
            
            self.status_var.set(f"Preview complete - Found {total_fields} fields in {len(forms)} form(s)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview form: {str(e)}")
            self.status_var.set("Ready")
    
    def open_form(self):
        """Open the form in browser for auto-filling."""
        url = self.url_var.get().strip()
        company = self.company_var.get().strip()
        
        if not url:
            messagebox.showwarning("No URL", "Please enter a form URL.")
            return
        
        if not company:
            messagebox.showwarning("No Company", "Please select a company.")
            return
        
        self.status_var.set("Opening browser and loading form...")
        self.window.update()
        
        try:
            success = self.web_filler.open_form_url(url, company)
            if success:
                self.status_var.set("Form loaded - Ready for analysis and auto-fill")
                messagebox.showinfo("Success", "Form loaded successfully! You can now analyze fields and auto-fill.")
            else:
                self.status_var.set("Failed to load form")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open form: {str(e)}")
            self.status_var.set("Ready")
    
    def analyze_form(self):
        """Analyze the currently opened form."""
        if not self.web_filler.driver:
            messagebox.showwarning("No Browser", "Please open a form first.")
            return
        
        company = self.company_var.get().strip()
        if not company:
            messagebox.showwarning("No Company", "Please select a company.")
            return
        
        self.status_var.set("Analyzing form fields...")
        self.window.update()
        
        try:
            form_analysis = self.web_filler.analyze_form_fields()
            
            if not form_analysis:
                messagebox.showerror("Analysis Failed", "Failed to analyze form.")
                return
            
            # Clear existing results
            self.clear_results()
            
            # Show analysis results
            fillable_fields = form_analysis.get('fillable_fields', [])
            
            for field_info in fillable_fields:
                suggested = field_info.get('suggested_value', {})
                confidence = suggested.get('confidence', 0)
                confidence_str = f"{confidence:.0%}" if confidence else "N/A"
                
                self.results_tree.insert('', 'end', values=(
                    field_info.get('name') or field_info.get('id', 'N/A'),
                    field_info.get('label', ''),
                    field_info.get('type', 'text'),
                    suggested.get('value', 'No suggestion'),
                    confidence_str,
                    '☐'
                ))
            
            total_detected = len(form_analysis.get('detected_fields', []))
            self.status_var.set(f"Analysis complete - {len(fillable_fields)} fillable fields found (of {total_detected} total)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze form: {str(e)}")
            self.status_var.set("Ready")
    
    def auto_fill_all(self):
        """Auto-fill all detected fields."""
        if not self.web_filler.driver:
            messagebox.showwarning("No Browser", "Please open and analyze a form first.")
            return
        
        self.status_var.set("Auto-filling form...")
        self.window.update()
        
        try:
            results = self.web_filler.auto_fill_form()
            
            if results.get('success'):
                filled_count = len(results.get('filled_fields', []))
                failed_count = len(results.get('failed_fields', []))
                
                # Update tree with results
                for item in self.results_tree.get_children():
                    field_name = self.results_tree.item(item, 'values')[0]
                    
                    # Check if this field was filled
                    was_filled = any(f['field'] == field_name for f in results.get('filled_fields', []))
                    if was_filled:
                        # Update the checkbox to checked
                        values = list(self.results_tree.item(item, 'values'))
                        values[5] = '☑'
                        self.results_tree.item(item, values=values)
                
                message = f"Auto-fill complete!\nFilled: {filled_count} fields\nFailed: {failed_count} fields"
                messagebox.showinfo("Auto-Fill Results", message)
                self.status_var.set(f"Auto-fill complete - {filled_count} fields filled")
                
            else:
                messagebox.showerror("Auto-Fill Failed", results.get('message', 'Unknown error'))
                self.status_var.set("Auto-fill failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Auto-fill failed: {str(e)}")
            self.status_var.set("Ready")
    
    def fill_selected(self):
        """Fill only selected fields."""
        messagebox.showinfo("Coming Soon", "Fill selected fields feature coming soon!")
    
    def clear_results(self):
        """Clear the results tree."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
    
    def on_closing(self):
        """Handle window closing."""
        self.web_filler.close_browser()
        self.window.destroy()