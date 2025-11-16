"""
Main Window - Primary GUI interface for the Tender Management System
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
from datetime import datetime
from typing import Dict, List, Any

from ..core.document_parser import DocumentParser
from ..core.search_engine import SearchEngine
from ..core.checklist_generator import ChecklistGenerator
from ..core.database_manager import DatabaseManager
from ..core.web_form_filler import WebFormWindow
from ..core.pdf_form_filler import PDFFormWindow
from .database_window import DatabaseWindow

class MainWindow:
    """Main application window with document management and navigation."""
    
    def __init__(self, root: tk.Tk, config):
        self.root = root
        self.config = config
        
        # Initialize core components
        self.document_parser = DocumentParser()
        self.search_engine = SearchEngine()
        self.checklist_generator = ChecklistGenerator()
        self.database_manager = DatabaseManager()
        
        # Initialize GUI components
        self.database_window = DatabaseWindow(self.root, self.database_manager)
        self.web_form_window = WebFormWindow(self.root, self.database_manager)
        self.pdf_form_window = PDFFormWindow(self.root, self.database_manager)
        
        # Data storage
        self.uploaded_documents: List[Dict[str, Any]] = []
        self.documents_file = "data/uploaded_documents.json"
        
        # Initialize GUI
        self.setup_gui()
        self.setup_menu()
        
        # Load previously uploaded documents
        self.load_uploaded_documents()
        
    def setup_gui(self):
        """Setup the main GUI layout."""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create paned window for layout
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Document list and search
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Document list section
        doc_frame = ttk.LabelFrame(left_frame, text="Documents", padding=10)
        doc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Document listbox with scrollbar
        list_frame = ttk.Frame(doc_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.doc_listbox = tk.Listbox(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.doc_listbox.yview)
        self.doc_listbox.config(yscrollcommand=scrollbar.set)
        
        self.doc_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Document buttons
        btn_frame = ttk.Frame(doc_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Upload Documents", command=self.upload_documents).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_document).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="View Document", command=self.view_document).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📄 Fill PDF Form", command=self.show_pdf_form_filler).pack(side=tk.LEFT)
        
        # Search section
        search_frame = ttk.LabelFrame(left_frame, text="Search Documents", padding=10)
        search_frame.pack(fill=tk.X)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, pady=(0, 5))
        search_entry.bind('<Return>', self.search_documents)
        
        ttk.Button(search_frame, text="Search", command=self.search_documents).pack()
        
        # Right panel - Main content area
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Welcome tab
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="Welcome")
        
        welcome_text = """Welcome to Tender Management System

✨ Core Features:
• Upload and parse tender documents (PDF, Word, Excel) with OCR
• 📁 Persistent document storage - uploaded documents remain available
• Search through document contents with intelligent ranking
• Generate personalized checklists from document analysis
• Store company information in intelligent database
• Auto-fill online forms with saved company data
• Visual progress tracking and management

🚀 Form Auto-Fill:
• 📄 PDF Form Auto-Fill - Open PDF forms directly and get field suggestions
• 🌐 Online Form Auto-Fill - Auto-fill web forms with database information
• Support for Kiwi Gaming Grant and other PDF applications
• New Zealand business number support (NZBN, Company Number, etc.)
• Smart field detection and mapping

📋 Document Management:
• Uploaded documents persist between sessions
• Grant applications remain in your document list
• Easy access to all your tender and grant documents
• Re-parse documents automatically when app restarts

🎯 Getting Started:
1. Upload documents → They stay in your list permanently
2. Extract to database → Build reusable company profiles  
3. Generate checklists → Smart analysis of requirements
4. Use 'Forms' menu → Auto-fill PDF forms or online applications
"""
        
        welcome_label = tk.Label(welcome_frame, text=welcome_text, justify=tk.LEFT, font=('Arial', 11))
        welcome_label.pack(padx=20, pady=20)
        
        # Search results tab
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Search Results")
        
        self.search_results = scrolledtext.ScrolledText(self.search_frame, wrap=tk.WORD)
        self.search_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Checklist tab
        self.checklist_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.checklist_frame, text="Checklist")
        
        # Checklist controls
        checklist_controls = ttk.Frame(self.checklist_frame)
        checklist_controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(checklist_controls, text="Generate Checklist", 
                  command=self.generate_checklist).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(checklist_controls, text="Save Checklist", 
                  command=self.save_checklist).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(checklist_controls, text="Load Checklist", 
                  command=self.load_checklist).pack(side=tk.LEFT)
        
        # Progress frame
        progress_frame = ttk.Frame(checklist_controls)
        progress_frame.pack(side=tk.RIGHT)
        
        self.progress_label = ttk.Label(progress_frame, text="Progress: 0%")
        self.progress_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Checklist display area with scrollable frame
        self.setup_checklist_display()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_menu(self):
        """Setup application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Upload Documents...", command=self.upload_documents)
        file_menu.add_separator()
        file_menu.add_command(label="Generate Checklist...", command=self.generate_checklist)
        file_menu.add_command(label="New Pipeline Project...", command=self.create_pipeline)
        file_menu.add_separator()
        file_menu.add_command(label="Reload Documents", command=self.reload_documents)
        file_menu.add_command(label="Clear All Documents", command=self.clear_all_documents)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Forms menu
        forms_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Forms", menu=forms_menu)
        forms_menu.add_command(label="📄 Auto-Fill PDF Forms", command=self.show_pdf_form_filler)
        forms_menu.add_command(label="🌐 Auto-Fill Online Forms", command=self.show_web_form_filler)
        forms_menu.add_separator()
        forms_menu.add_command(label="Open Kiwi Gaming Grant", command=self.open_kiwi_gaming_grant)
        forms_menu.add_command(label="Open Business.gov.au Grants", command=self.open_business_grants)
        
        # Database menu
        database_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Database", menu=database_menu)
        database_menu.add_command(label="Manage Company Information", command=self.show_database_manager)
        database_menu.add_command(label="Extract from Documents", command=self.extract_to_database)
        database_menu.add_separator()
        database_menu.add_command(label="Database Statistics", command=self.show_database_stats)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Document Statistics", command=self.show_document_stats)
        tools_menu.add_command(label="Auto-Fill Test", command=self.test_autofill)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def upload_documents(self):
        """Handle document upload."""
        filetypes = [
            ("All Supported", "*.pdf *.docx *.doc *.xlsx *.xls *.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx *.doc"),
            ("Excel files", "*.xlsx *.xls"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
        
        filenames = filedialog.askopenfilenames(
            title="Select Documents",
            filetypes=filetypes
        )
        
        if filenames:
            self.status_var.set("Processing documents...")
            self.root.update()
            
            successful_uploads = 0
            
            for filename in filenames:
                try:
                    # Parse document
                    content = self.document_parser.parse_file(filename)
                    
                    # Debug: Check content
                    print(f"DEBUG: Parsed {filename}, content length: {len(content)}")
                    print(f"DEBUG: Content preview: {content[:100]}...")
                    
                    # Check if PDF parsing produced minimal content
                    if filename.lower().endswith('.pdf') and len(content.strip()) < 50:
                        response = messagebox.askyesno(
                            "PDF Parsing Issue",
                            f"The PDF '{os.path.basename(filename)}' produced very little text content.\n\n"
                            "This often happens with:\n"
                            "• Scanned documents or images\n"
                            "• Complex formatted PDFs\n"
                            "• Encrypted PDFs\n\n"
                            "Do you want to add it anyway? You can still view the parsing results."
                        )
                        if not response:
                            continue
                    
                    # Add to document list with persistent storage
                    doc_info = {
                        'filename': os.path.basename(filename),
                        'filepath': filename,
                        'content': content,
                        'size': os.path.getsize(filename),
                        'upload_date': datetime.now().isoformat()
                    }
                    
                    self.add_document_to_persistent_storage(doc_info)
                    successful_uploads += 1
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process {filename}: {str(e)}")
            
            self.status_var.set(f"Successfully loaded {successful_uploads} documents")
            
    def remove_document(self):
        """Remove selected document from list and persistent storage."""
        selection = self.doc_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to remove.")
            return
            
        index = selection[0]
        
        # Confirm removal
        doc_name = self.uploaded_documents[index]['filename']
        if messagebox.askyesno("Confirm Removal", f"Remove '{doc_name}' from the document list?\n\nThis will remove it from your uploaded documents but won't delete the original file."):
            removed_doc = self.remove_document_from_storage(index)
            if removed_doc:
                self.status_var.set(f"Removed '{removed_doc['filename']}' from document list")
        
    def view_document(self):
        """View selected document content."""
        selection = self.doc_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to view.")
            return
            
        index = selection[0]
        doc_info = self.uploaded_documents[index]
        
        # Debug: Check what we have
        print(f"DEBUG: Viewing document {doc_info['filename']}")
        print(f"DEBUG: Content length: {len(doc_info.get('content', 'NO CONTENT'))}")
        print(f"DEBUG: Content preview: {doc_info.get('content', 'NO CONTENT')[:100]}...")
        
        # Create document viewer window
        viewer = tk.Toplevel(self.root)
        viewer.title(f"Document Viewer - {doc_info['filename']}")
        viewer.geometry("800x600")
        
        text_widget = scrolledtext.ScrolledText(viewer, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        content = doc_info.get('content', 'No content available')
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        
    def search_documents(self, event=None):
        """Search through uploaded documents."""
        query = self.search_var.get().strip()
        if not query:
            return
            
        if not self.uploaded_documents:
            messagebox.showwarning("Warning", "Please upload some documents first.")
            return
            
        # Perform search
        results = self.search_engine.search(query)
        
        # Display results
        self.search_results.delete(1.0, tk.END)
        
        if results:
            self.search_results.insert(tk.END, f"Search Results for '{query}':\\n\\n")
            for i, result in enumerate(results, 1):
                self.search_results.insert(tk.END, f"{i}. {result['document']}\\n")
                self.search_results.insert(tk.END, f"   Score: {result['score']:.2f}\\n")
                self.search_results.insert(tk.END, f"   Preview: {result['snippet'][:200]}...\\n\\n")
        else:
            self.search_results.insert(tk.END, f"No results found for '{query}'")
            
        # Switch to search results tab
        self.notebook.select(1)
        self.status_var.set(f"Found {len(results)} results")
        
    def generate_checklist(self):
        """Generate a personalized checklist."""
        if not self.uploaded_documents:
            messagebox.showwarning("Warning", "Please upload some documents first.")
            return
            
        messagebox.showinfo("Coming Soon", 
                          "Checklist generation feature will be implemented next!\\n\\n" +
                          "Your documents have been processed and can be searched.\\n" +
                          "The checklist generator will analyze these documents to\\n" +
                          "create personalized checklists based on tender requirements.")
        
    def create_pipeline(self):
        """Create a new pipeline project.""" 
        if not self.uploaded_documents:
            messagebox.showwarning("Warning", "Please upload some documents first.")
            return
            
        messagebox.showinfo("Coming Soon",
                          "Pipeline management feature will be implemented next!\\n\\n" +
                          "Your documents are ready for analysis.\\n" +
                          "The pipeline manager will create section-based workflows\\n" +
                          "with progress tracking and file upload capabilities.")
        
    def show_document_stats(self):
        """Show document statistics."""
        if not self.uploaded_documents:
            messagebox.showinfo("Statistics", "No documents loaded.")
            return
            
        total_docs = len(self.uploaded_documents)
        total_size = sum(doc['size'] for doc in self.uploaded_documents)
        avg_size = total_size / total_docs
        
        stats = f"""Document Statistics:
        
Total Documents: {total_docs}
Total Size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)
Average Size: {avg_size:,.0f} bytes ({avg_size/1024:.1f} KB)

Document Types:
"""
        
        # Count by extension
        extensions = {}
        for doc in self.uploaded_documents:
            ext = os.path.splitext(doc['filename'])[1].lower()
            extensions[ext] = extensions.get(ext, 0) + 1
            
        for ext, count in extensions.items():
            stats += f"{ext or 'No extension'}: {count}\\n"
            
        messagebox.showinfo("Document Statistics", stats)
        
    def show_about(self):
        """Show about dialog."""
        about_text = """Tender Management System v1.0

A comprehensive solution for managing tender information,
creating personalized checklists, and tracking project pipelines.

Features:
• Document processing and parsing
• Intelligent search capabilities  
• Automated checklist generation
• Pipeline management with progress tracking
• Section-based file uploads
• Visual progress indicators

Built with Python and tkinter.

This is a demonstration version showcasing the user interface.
Full functionality includes document parsing, search engine,
checklist generation, and pipeline management."""

        messagebox.showinfo("About", about_text)
    
    def setup_checklist_display(self):
        """Setup the checklist display area with scrollable frame."""
        # Create scrollable frame for checklist
        canvas = tk.Canvas(self.checklist_frame)
        scrollbar_checklist = ttk.Scrollbar(self.checklist_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_checklist.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar_checklist.pack(side="right", fill="y", pady=10)
        
        # Store references
        self.checklist_canvas = canvas
        self.checklist_scrollbar = scrollbar_checklist
        self.current_checklist = None
        
        # Add initial message
        self.show_checklist_message("No checklist generated yet. Upload documents and click 'Generate Checklist' to begin.")
    
    def show_checklist_message(self, message: str):
        """Show a message in the checklist area."""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Show message
        msg_label = ttk.Label(self.scrollable_frame, text=message, font=('Arial', 12))
        msg_label.pack(pady=50)
    
    def generate_checklist(self):
        """Generate checklist from uploaded documents."""
        if not self.uploaded_documents:
            messagebox.showwarning("No Documents", "Please upload some documents first.")
            return
        
        self.status_var.set("Generating checklist...")
        self.root.update()
        
        try:
            # Combine all document content
            combined_content = ""
            for doc in self.uploaded_documents:
                if doc.get('content'):
                    combined_content += f"\n--- {doc['filename']} ---\n"
                    combined_content += doc['content']
                    combined_content += "\n"
            
            if not combined_content.strip():
                messagebox.showwarning("No Content", "No content found in uploaded documents. Make sure documents contain text.")
                return
            
            # Generate checklist
            checklist_data = self.checklist_generator.generate_checklist(combined_content)
            self.current_checklist = checklist_data
            
            # Display checklist
            self.display_checklist(checklist_data)
            
            # Switch to checklist tab
            self.notebook.select(self.checklist_frame)
            
            self.status_var.set(f"Checklist generated with {self.count_total_items(checklist_data)} items")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate checklist: {str(e)}")
            self.status_var.set("Ready")
    
    def display_checklist(self, checklist_data: Dict[str, Any]):
        """Display the generated checklist."""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Title and summary
        title_frame = ttk.Frame(self.scrollable_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text=checklist_data['title'], 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        # Summary information
        summary = checklist_data.get('summary', {})
        if summary:
            summary_frame = ttk.LabelFrame(self.scrollable_frame, text="Document Analysis", padding=10)
            summary_frame.pack(fill=tk.X, pady=(0, 20))
            
            info_text = f"""Document Type: {summary.get('document_type', 'Unknown')}
Word Count: {summary.get('word_count', 0):,}
Requirements Found: {summary.get('requirements_found', 0)}
Estimated Completion: {checklist_data.get('estimated_completion_time', {}).get('estimated_days', 'Unknown')} days
"""
            ttk.Label(summary_frame, text=info_text, justify=tk.LEFT).pack()
        
        # Categories and items
        self.checklist_vars = {}  # Store checkbox variables
        total_items = 0
        completed_items = 0
        
        for category_name, category_data in checklist_data.get('categories', {}).items():
            # Category frame
            category_frame = ttk.LabelFrame(self.scrollable_frame, text=category_name, padding=10)
            category_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Category header with progress
            header_frame = ttk.Frame(category_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            priority_color = {"high": "red", "medium": "orange", "low": "green"}.get(
                category_data.get('priority', 'low'), 'black'
            )
            
            ttk.Label(header_frame, text=f"Priority: {category_data.get('priority', 'medium').title()}", 
                     foreground=priority_color).pack(side=tk.LEFT)
            
            progress_text = f"{category_data.get('completed', 0)}/{category_data.get('total', 0)} completed"
            ttk.Label(header_frame, text=progress_text).pack(side=tk.RIGHT)
            
            # Items
            for item in category_data.get('items', []):
                item_frame = ttk.Frame(category_frame)
                item_frame.pack(fill=tk.X, pady=2)
                
                # Checkbox
                var = tk.BooleanVar(value=item.get('completed', False))
                self.checklist_vars[item['id']] = var
                
                checkbox = ttk.Checkbutton(item_frame, variable=var, 
                                         command=lambda: self.update_progress())
                checkbox.pack(side=tk.LEFT)
                
                # Item text
                item_text = item['text']
                if item.get('estimated_hours'):
                    item_text += f" (Est. {item['estimated_hours']}h)"
                
                item_label = ttk.Label(item_frame, text=item_text, wraplength=600)
                item_label.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
                
                # Priority indicator
                if item.get('priority') == 'high':
                    priority_label = ttk.Label(item_frame, text="HIGH", foreground="red", 
                                             font=('Arial', 8, 'bold'))
                    priority_label.pack(side=tk.RIGHT)
                
                total_items += 1
                if item.get('completed', False):
                    completed_items += 1
        
        # Update progress bar
        self.update_progress()
        
        # Deadlines section
        deadlines = checklist_data.get('critical_deadlines', [])
        if deadlines:
            deadline_frame = ttk.LabelFrame(self.scrollable_frame, text="Critical Deadlines", padding=10)
            deadline_frame.pack(fill=tk.X, pady=(0, 15))
            
            for deadline in deadlines[:5]:  # Show first 5 deadlines
                deadline_text = f"{deadline.get('type', 'Deadline')}: {deadline.get('date', 'TBD')}"
                ttk.Label(deadline_frame, text=deadline_text, font=('Arial', 10)).pack(anchor=tk.W)
        
        # Scroll to top
        self.checklist_canvas.yview_moveto(0)
    
    def update_progress(self):
        """Update the progress bar and label."""
        if not self.current_checklist or not hasattr(self, 'checklist_vars'):
            return
        
        total_items = 0
        completed_items = 0
        
        for category_data in self.current_checklist.get('categories', {}).values():
            for item in category_data.get('items', []):
                total_items += 1
                if self.checklist_vars.get(item['id'], tk.BooleanVar()).get():
                    completed_items += 1
        
        if total_items > 0:
            progress_percent = (completed_items / total_items) * 100
            self.progress_bar['value'] = progress_percent
            self.progress_label.config(text=f"Progress: {progress_percent:.1f}%")
        else:
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Progress: 0%")
    
    def count_total_items(self, checklist_data: Dict[str, Any]) -> int:
        """Count total items in checklist."""
        total = 0
        for category_data in checklist_data.get('categories', {}).values():
            total += len(category_data.get('items', []))
        return total
    
    def save_checklist(self):
        """Save the current checklist to a file."""
        if not self.current_checklist:
            messagebox.showwarning("No Checklist", "No checklist to save. Generate a checklist first.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Checklist",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                import json
                
                # Update completion status from GUI
                for category_data in self.current_checklist.get('categories', {}).values():
                    for item in category_data.get('items', []):
                        if item['id'] in self.checklist_vars:
                            item['completed'] = self.checklist_vars[item['id']].get()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_checklist, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Checklist saved to {filename}")
                self.status_var.set(f"Checklist saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save checklist: {str(e)}")
    
    def load_checklist(self):
        """Load a checklist from a file."""
        filename = filedialog.askopenfilename(
            title="Load Checklist",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                import json
                
                with open(filename, 'r', encoding='utf-8') as f:
                    checklist_data = json.load(f)
                
                self.current_checklist = checklist_data
                self.display_checklist(checklist_data)
                
                # Switch to checklist tab
                self.notebook.select(self.checklist_frame)
                
                total_items = self.count_total_items(checklist_data)
                messagebox.showinfo("Success", f"Checklist loaded with {total_items} items")
                self.status_var.set(f"Checklist loaded from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load checklist: {str(e)}")
    
    def create_pipeline(self):
        """Create a new pipeline project (placeholder for now)."""
        messagebox.showinfo("Coming Soon", "Pipeline management feature is coming soon!")
        self.status_var.set("Pipeline management feature coming soon")
    
    def show_database_manager(self):
        """Show the database management window."""
        self.database_window.show_database_window()
    
    def extract_to_database(self):
        """Extract information from uploaded documents to database."""
        if not self.uploaded_documents:
            messagebox.showwarning("No Documents", "Please upload some documents first.")
            return
        
        # Ask for company name
        from tkinter import simpledialog
        company_name = simpledialog.askstring(
            "Company Name", 
            "Enter company name for database extraction:",
            initialvalue="My Company"
        )
        
        if not company_name:
            return
        
        self.status_var.set("Extracting information to database...")
        self.root.update()
        
        try:
            # Combine all document content
            combined_content = ""
            for doc in self.uploaded_documents:
                if doc.get('content'):
                    combined_content += f"\n--- {doc['filename']} ---\n"
                    combined_content += doc['content']
                    combined_content += "\n"
            
            if not combined_content.strip():
                messagebox.showwarning("No Content", "No content found in uploaded documents.")
                return
            
            # Extract and store information
            extracted_info = self.database_manager.extract_and_store_information(
                combined_content, company_name
            )
            
            # Show results
            results_text = f"Information extracted for: {company_name}\n\n"
            
            if extracted_info.get('company'):
                company_info = extracted_info['company']
                results_text += "Company Information:\n"
                for key, value in company_info.items():
                    results_text += f"  {key}: {value}\n"
                results_text += "\n"
            
            if extracted_info.get('financial'):
                financial_info = extracted_info['financial']
                results_text += "Financial Information:\n"
                for key, value in financial_info.items():
                    if isinstance(value, (int, float)):
                        results_text += f"  {key}: ${value:,.0f}\n"
                    else:
                        results_text += f"  {key}: {value}\n"
                results_text += "\n"
            
            # Count extracted items
            total_items = 0
            for category, items in extracted_info.items():
                if isinstance(items, list):
                    total_items += len(items)
                elif isinstance(items, dict) and items:
                    total_items += len(items)
            
            results_text += f"Total items extracted: {total_items}"
            
            if total_items > 0:
                messagebox.showinfo("Extraction Complete", results_text)
                self.status_var.set(f"Extracted {total_items} items to database for {company_name}")
            else:
                messagebox.showinfo("Extraction Complete", f"Company '{company_name}' added to database.\nNo specific information items were extracted from the documents.")
                self.status_var.set(f"Company {company_name} added to database")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract information: {str(e)}")
            self.status_var.set("Ready")
    
    def show_database_stats(self):
        """Show database statistics."""
        try:
            stats = self.database_manager.get_database_stats()
            companies = self.database_manager.list_companies()
            
            stats_text = f"Database Statistics\n{'='*30}\n\n"
            stats_text += f"Companies: {len(companies)}\n"
            
            if companies:
                stats_text += "\nCompany List:\n"
                for company in companies[:10]:  # Show first 10
                    stats_text += f"  • {company}\n"
                if len(companies) > 10:
                    stats_text += f"  ... and {len(companies) - 10} more\n"
            
            stats_text += f"\nData Records:\n"
            for table, count in stats.items():
                if count > 0:
                    table_name = table.replace('_', ' ').title()
                    stats_text += f"  {table_name}: {count}\n"
            
            messagebox.showinfo("Database Statistics", stats_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get database statistics: {str(e)}")
    
    def test_autofill(self):
        """Test auto-fill functionality."""
        if not self.database_manager.list_companies():
            messagebox.showwarning("No Data", "No companies in database. Please extract information from documents first.")
            return
        
        # Show database manager with auto-fill tab selected
        self.database_window.show_database_window()
        # Switch to auto-fill tab
        if hasattr(self.database_window, 'details_notebook'):
            self.database_window.details_notebook.select(self.database_window.autofill_frame)
    
    def show_pdf_form_filler(self):
        """Show the PDF form auto-fill window."""
        companies = self.database_manager.list_companies()
        if not companies:
            result = messagebox.askyesno(
                "No Company Data", 
                "No company information found in database. Would you like to extract information from your uploaded documents first?"
            )
            if result:
                self.extract_to_database()
                return
        
        self.pdf_form_window.show_pdf_form_window()
    
    def show_web_form_filler(self):
        """Show the web form auto-fill window."""
        companies = self.database_manager.list_companies()
        if not companies:
            result = messagebox.askyesno(
                "No Company Data", 
                "No company information found in database. Would you like to extract information from your uploaded documents first?"
            )
            if result:
                self.extract_to_database()
                return
        
        self.web_form_window.show_web_form_window()
    
    def open_kiwi_gaming_grant(self):
        """Open Kiwi Gaming Grant application directly."""
        companies = self.database_manager.list_companies()
        if not companies:
            messagebox.showwarning("No Company Data", "Please extract company information to database first.")
            return
        
        # For demonstration - would be actual Kiwi Gaming Grant URL
        grant_url = "https://www.business.govt.nz/help-for-my-business/grants-finder/"
        
        # Open in default browser for now
        import webbrowser
        webbrowser.open(grant_url)
        
        # Show auto-fill window
        self.web_form_window.show_web_form_window()
        self.web_form_window.set_url(grant_url)
        
        messagebox.showinfo(
            "Web Form Auto-Fill", 
            "The Kiwi Gaming Grant page has been opened in your browser.\n\n"
            "Use the Web Form Auto-Fill window to:\n"
            "1. Enter the form URL\n"
            "2. Select your company\n"
            "3. Click 'Open Form' to load it in the auto-fill browser\n"
            "4. Click 'Analyze Fields' to detect fillable fields\n"
            "5. Click 'Auto-Fill All' to populate the form automatically!"
        )
    
    def open_business_grants(self):
        """Open business.gov.au grants page."""
        business_grants_url = "https://www.business.gov.au/grants-and-programs"
        
        import webbrowser
        webbrowser.open(business_grants_url)
        
        self.web_form_window.show_web_form_window()
        self.web_form_window.set_url(business_grants_url)
        
        messagebox.showinfo(
            "Business Grants", 
            "The business.gov.au grants page has been opened.\n\n"
            "Navigate to a specific grant application form, then use the Web Form Auto-Fill window to automatically populate it with your company information."
        )
    
    def save_uploaded_documents(self):
        """Save uploaded documents list to file for persistence."""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.documents_file), exist_ok=True)
            
            # Prepare documents data for saving
            documents_data = []
            for doc in self.uploaded_documents:
                doc_data = {
                    'filename': doc['filename'],
                    'filepath': doc['filepath'],
                    'size': doc['size'],
                    'upload_date': doc.get('upload_date', datetime.now().isoformat()),
                    'content_length': len(doc.get('content', '')),
                    # Don't save content to reduce file size - will re-parse when needed
                }
                documents_data.append(doc_data)
            
            # Save to JSON file
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                import json
                json.dump({
                    'documents': documents_data,
                    'last_updated': datetime.now().isoformat(),
                    'total_count': len(documents_data)
                }, f, indent=2, ensure_ascii=False)
            
            print(f"DEBUG: Saved {len(documents_data)} documents to {self.documents_file}")
            
        except Exception as e:
            print(f"DEBUG: Failed to save documents: {str(e)}")
    
    def load_uploaded_documents(self):
        """Load previously uploaded documents from file."""
        try:
            if not os.path.exists(self.documents_file):
                print("DEBUG: No saved documents file found")
                return
            
            with open(self.documents_file, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
            
            documents_data = data.get('documents', [])
            successful_loads = 0
            
            for doc_data in documents_data:
                try:
                    filepath = doc_data['filepath']
                    
                    # Check if file still exists
                    if not os.path.exists(filepath):
                        print(f"DEBUG: Skipping missing file: {filepath}")
                        continue
                    
                    # Re-parse the document to get current content
                    content = self.document_parser.parse_file(filepath)
                    
                    # Add to current document list
                    doc_info = {
                        'filename': doc_data['filename'],
                        'filepath': filepath,
                        'content': content,
                        'size': doc_data['size'],
                        'upload_date': doc_data.get('upload_date', 'Unknown'),
                        'reloaded': True  # Mark as reloaded from storage
                    }
                    
                    self.uploaded_documents.append(doc_info)
                    self.doc_listbox.insert(tk.END, f"📄 {doc_info['filename']}")
                    
                    # Add to search engine
                    self.search_engine.add_document(doc_info['filename'], content)
                    
                    successful_loads += 1
                    
                except Exception as e:
                    print(f"DEBUG: Failed to reload {doc_data.get('filename', 'unknown')}: {str(e)}")
            
            if successful_loads > 0:
                self.status_var.set(f"Reloaded {successful_loads} previously uploaded documents")
                print(f"DEBUG: Successfully reloaded {successful_loads} documents")
            
        except Exception as e:
            print(f"DEBUG: Failed to load documents: {str(e)}")
    
    def add_document_to_persistent_storage(self, doc_info: Dict[str, Any]):
        """Add a document and save to persistent storage."""
        # Add upload date if not present
        if 'upload_date' not in doc_info:
            doc_info['upload_date'] = datetime.now().isoformat()
        
        # Add to current list
        self.uploaded_documents.append(doc_info)
        
        # Add document icon to distinguish from reloaded documents
        if doc_info.get('reloaded'):
            display_name = f"📄 {doc_info['filename']}"
        else:
            display_name = f"📄 {doc_info['filename']} (New)"
        
        self.doc_listbox.insert(tk.END, display_name)
        
        # Add to search engine
        self.search_engine.add_document(doc_info['filename'], doc_info['content'])
        
        # Save to persistent storage
        self.save_uploaded_documents()
    
    def remove_document_from_storage(self, index: int):
        """Remove document from both memory and persistent storage."""
        if 0 <= index < len(self.uploaded_documents):
            doc_info = self.uploaded_documents[index]
            
            # Remove from memory
            self.uploaded_documents.pop(index)
            self.doc_listbox.delete(index)
            
            # Remove from search engine
            self.search_engine.remove_document(doc_info['filename'])
            
            # Update persistent storage
            self.save_uploaded_documents()
            
            return doc_info
        return None
    
    def reload_documents(self):
        """Manually reload documents from storage."""
        # Clear current documents
        self.uploaded_documents.clear()
        self.doc_listbox.delete(0, tk.END)
        self.search_engine = SearchEngine()  # Reset search engine
        
        # Reload from storage
        self.load_uploaded_documents()
        
        messagebox.showinfo("Reload Complete", f"Reloaded {len(self.uploaded_documents)} documents from storage.")
    
    def clear_all_documents(self):
        """Clear all uploaded documents."""
        if not self.uploaded_documents:
            messagebox.showinfo("No Documents", "No documents to clear.")
            return
        
        count = len(self.uploaded_documents)
        if messagebox.askyesno("Clear All Documents", 
                              f"Remove all {count} uploaded documents from the list?\n\n"
                              "This will clear your document list but won't delete the original files.\n"
                              "You can re-upload documents anytime."):
            
            # Clear everything
            self.uploaded_documents.clear()
            self.doc_listbox.delete(0, tk.END)
            self.search_engine = SearchEngine()  # Reset search engine
            
            # Clear storage file
            try:
                if os.path.exists(self.documents_file):
                    os.remove(self.documents_file)
            except Exception as e:
                print(f"DEBUG: Failed to remove storage file: {str(e)}")
            
            self.status_var.set("All documents cleared")
            messagebox.showinfo("Cleared", f"Cleared {count} documents from the list.")