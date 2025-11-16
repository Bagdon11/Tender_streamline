# OCR Setup Instructions

## Enable OCR (Optical Character Recognition) for Scanned PDFs

Your Tender Management Application can extract text from scanned PDFs and image-based documents using OCR technology.

### Quick Setup (Windows)

1. **Download Tesseract OCR**:
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest Windows installer (usually named `tesseract-ocr-w64-setup-*.exe`)

2. **Install Tesseract**:
   - Run the installer as Administrator
   - Install to the default location: `C:\Program Files\Tesseract-OCR\`
   - Make sure to check "Add to PATH" if available

3. **Restart the Application**:
   - Close and restart your Tender Management app
   - OCR will be automatically detected and enabled

### What OCR Enables

✅ **Extract text from scanned PDFs**
✅ **Process image-based documents** 
✅ **Handle complex formatted PDFs**
✅ **Work with forms and applications that are scanned**

### Testing OCR

Once installed, when you upload a PDF:
1. The app will try normal text extraction first
2. If that fails, it will automatically use OCR
3. You'll see progress messages like "OCR processing page 1/4..."
4. The extracted text will be marked as "[OCR EXTRACTED TEXT]"

### Alternative: Online OCR Tools

If you prefer not to install Tesseract, you can:
1. Use online PDF to text converters
2. Convert your PDF to Word format first
3. Save scanned documents as text files before uploading

### For Advanced Users

- Tesseract supports 100+ languages
- You can adjust OCR accuracy settings
- Batch processing is supported for multiple documents

**The application will work fine without OCR - it just won't be able to extract text from scanned/image-based PDFs.**