# Tender Management System

A comprehensive desktop application for managing tender information, creating personalized checklists, automating form filling, and tracking project costs. Built specifically for New Zealand business requirements with support for NZBN, bank account verification, and compliance documentation.

## 🚀 Features

### **Document Processing & OCR**
- **Multi-format support**: PDF, Word, Excel, Text files
- **Advanced OCR**: Extract text from scanned PDFs and images using Tesseract
- **Smart parsing**: Automatic fallback chain (PyPDF2 → pdfplumber → OCR)
- **Document persistence**: Auto-reload documents on startup

### **Intelligent Search Engine**
- **TF-IDF scoring**: Advanced relevance-based search
- **Content analysis**: Document statistics and insights
- **Quick search**: Find information across all uploaded documents
- **Search history**: Track and revisit previous searches

### **Database Management System**
- **Company profiles**: Comprehensive business information storage
- **NZ Business identifiers**: NZBN, Company Number, GST Number support
- **Contact management**: Team contacts with roles and details
- **Financial records**: Annual turnover, assets, liabilities tracking
- **Certifications & insurance**: License and policy management
- **Project experience**: Previous work and client history

### **Bank Account Management**
- **NZ bank details**: Bank name, account name, account number
- **Document evidence**: Upload bank statements and verification documents
- **Image preview**: Hover to preview uploaded bank documents
- **File management**: Store and organize financial evidence

### **Project Cost Breakdown System**
- **35+ cost categories**: Labor, equipment, operational, project-specific costs
- **NZ compliance**: ACC, KiwiSaver, GST, holiday provisions
- **Smart calculator**: Automatic totaling with overhead and profit margins
- **Professional breakdowns**: Detailed cost analysis and reporting

### **PDF Form Auto-Fill**
- **Form analysis**: Detect and analyze fillable PDF fields
- **Smart mapping**: Auto-match form fields to database information
- **Static PDF conversion**: Transform non-fillable PDFs to fillable forms
- **Auto-suggestions**: Generate completion suggestions for any PDF

### **Web Form Automation**
- **Browser automation**: Auto-fill web forms using Selenium
- **Field detection**: Smart identification of form elements
- **Data mapping**: Connect database info to web form fields
- **Multi-browser support**: Chrome, Firefox, Edge compatibility

### **Personalized Checklists**
- **AI-generated tasks**: Custom checklists based on tender requirements
- **Progress tracking**: Mark completion and track progress
- **Export options**: Save checklists for external use
- **Template system**: Reusable checklist templates

## 📋 Requirements

### **Core Dependencies**
```
Python 3.13.5+
tkinter (GUI framework)
SQLite (database)
```

### **Document Processing**
```
PyPDF2>=3.0.1         # PDF processing
pdfplumber>=0.11.0     # Advanced PDF extraction
pytesseract>=0.3.13    # OCR functionality
pdf2image>=1.17.0      # PDF to image conversion
python-docx>=0.8.11    # Word document processing
openpyxl>=3.1.2        # Excel processing
pandas>=2.0.0          # Data analysis
```

### **Image & Graphics**
```
Pillow>=10.0.0         # Image processing
PyMuPDF>=1.23.0        # PDF preview generation
```

### **Web Automation**
```
selenium>=4.15.0       # Web form automation
beautifulsoup4>=4.12.0 # HTML parsing
requests>=2.31.0       # HTTP requests
```

### **PDF Creation & Forms**
```
reportlab>=4.0.0       # PDF creation
PyPDF4>=3.0.0          # PDF manipulation
fdfgen>=0.16.1         # PDF form field generation
```

### **Build & Distribution**
```
pyinstaller>=6.0.0     # Executable building
```

## 🛠️ Installation

### **Quick Start**
```bash
# Clone repository
git clone <repository-url>
cd Tender_streamline

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### **OCR Setup (Required for scanned PDFs)**
1. **Download Tesseract**: https://github.com/UB-Mannheim/tesseract/wiki
2. **Install Tesseract** to default location
3. **Verify installation**: `tesseract --version`

### **Poppler Setup (Required for PDF to image conversion)**
- Poppler binaries are included in the `poppler/` directory
- No additional installation required

## 🏗️ Building Executable

```bash
# Build standalone executable
pyinstaller TenderManagement.spec

# Or manual build
pyinstaller --onefile --windowed --name "TenderManagement" \
  --add-data "tessdata;tessdata" \
  --add-data "poppler;poppler" \
  main.py
```

## 📁 Project Structure

```
Tender_streamline/
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
├── TenderManagement.spec      # PyInstaller configuration
├── config.json               # Application configuration
│
├── src/                       # Source code
│   ├── core/                 # Core functionality
│   │   ├── database_manager.py      # SQLite database operations
│   │   ├── document_parser.py       # Multi-format document processing
│   │   ├── search_engine.py         # TF-IDF search implementation
│   │   ├── checklist_generator.py   # AI checklist creation
│   │   ├── pdf_converter.py         # PDF processing utilities
│   │   ├── pdf_form_filler.py       # PDF form automation
│   │   └── web_form_filler.py       # Web form automation
│   │
│   ├── gui/                  # GUI components
│   │   ├── main_window.py           # Primary application window
│   │   └── database_window.py       # Database management interface
│   │
│   └── utils/                # Utility functions
│       └── config.py               # Configuration management
│
├── data/                      # Data storage (auto-created)
│   ├── uploaded_documents.json     # Document metadata
│   ├── tender_management.db        # SQLite database
│   ├── documents/                  # Uploaded document files
│   ├── checklists/                # Generated checklists
│   └── projects/                  # Project-specific data
│
├── tessdata/                 # Tesseract OCR data
│   ├── eng.traineddata
│   └── osd.traineddata
│
├── poppler/                  # Poppler PDF utilities
│   └── poppler-23.01.0/
│
├── temp/                     # Temporary processing files
└── assets/                   # Application resources
```

## 🎯 Usage Guide

### **1. Document Management**
```
1. Launch application: python main.py
2. Upload documents using "Upload Documents" button
3. View document content and statistics
4. Search across all documents using the search bar
5. Documents auto-reload on next startup
```

### **2. Company Database**
```
1. Click "Manage Database"
2. Add/select company
3. Fill in business details (NZBN, GST, etc.)
4. Add team contacts and certifications
5. Enter financial information
6. Upload bank account details and statements
7. Configure project cost breakdowns
```

### **3. PDF Form Auto-Fill**
```
1. Click "Auto-Fill PDF Forms"
2. Select PDF file (fillable or static)
3. Choose company profile
4. Review suggested field mappings
5. Generate filled PDF or fillable version
```

### **4. Web Form Automation**
```
1. Click "Auto-Fill Web Forms"
2. Enter website URL
3. Select company profile
4. Browser opens with auto-filled form
5. Review and submit
```

### **5. Project Cost Calculation**
```
1. Go to Database → Project Costs tab
2. Enter labor rates and operational costs
3. Add equipment and material costs
4. Set overhead and profit percentages
5. Calculate total project cost
6. Use in tender applications
```

## 📊 New Zealand Compliance Features

### **Business Identifiers**
- ✅ **NZBN (New Zealand Business Number)** validation
- ✅ **Company Number** for incorporated entities
- ✅ **GST Number** for tax-registered businesses
- ✅ **Charity Number** for registered charities

### **Employment Compliance**
- ✅ **ACC levy calculations** (% of wages)
- ✅ **KiwiSaver employer contributions** (minimum 3%)
- ✅ **Holiday pay provisions** (8% minimum)
- ✅ **Overtime rate calculations**

### **Financial Requirements**
- ✅ **Bank account verification** with document upload
- ✅ **GST calculations** (15% where applicable)
- ✅ **Professional service costs** (legal, accounting)
- ✅ **Insurance premium tracking**

## 🔧 Current Status

### **✅ Fully Implemented**
- ✅ **Document processing** (PDF, Word, Excel with OCR)
- ✅ **Advanced search engine** with TF-IDF scoring
- ✅ **Complete database system** with NZ business support
- ✅ **Bank account management** with document evidence
- ✅ **Image preview functionality** for documents
- ✅ **Project cost breakdown** with 35+ categories
- ✅ **PDF form auto-fill** with static-to-fillable conversion
- ✅ **Web form automation** with browser control
- ✅ **Checklist generation** with AI assistance
- ✅ **Data persistence** with auto-loading
- ✅ **Professional cost calculations** with NZ compliance

### **🎯 Ready for Production Use**
The application is fully functional for:
- Professional tender document management
- Comprehensive business information storage
- Automated form filling (PDF and web)
- Accurate project cost estimation
- NZ compliance and regulatory requirements

## 🚀 Advanced Features

### **Smart Form Field Recognition**
- Automatic detection of company name, address, phone fields
- Recognition of financial fields (turnover, profit, costs)
- Bank account field identification
- Project cost and rate field mapping

### **Professional Cost Calculations**
```
Example Calculation:
Labor Costs:        $50,000
Equipment:          $20,000  
Operational:        $15,000
Project-Specific:   $10,000
Subtotal:          $95,000

Overhead (15%):     $14,250
Contingency (10%):   $9,500
Profit (12.5%):     $14,844
TOTAL:            $133,594
```

### **Document Evidence Management**
- Upload bank statements as verification
- Image preview on hover for quick identification
- File size tracking and organization
- Secure local storage with database references

## 🔐 Security & Privacy

- **Local storage only**: All data stored on your computer
- **No cloud dependencies**: Complete offline operation
- **Encrypted document handling**: Secure file processing
- **User control**: Full control over data and access

## 📞 Support & Documentation

- **Feature guides**: See `*.md` files for detailed feature documentation
- **Cost breakdown guide**: `PROJECT_COST_BREAKDOWN.md`
- **Bank account setup**: `BANK_IMAGE_PREVIEW.md`
- **Database features**: `DATABASE_SYSTEM.md`
- **Web automation**: `WEB_FORM_AUTOFILL.md`

## 📄 License

MIT License - See LICENSE file for details

---

**Built for New Zealand businesses** - Supporting local compliance requirements and tender processes with professional-grade automation and cost management.