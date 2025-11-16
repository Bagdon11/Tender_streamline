# Bank Account Image Preview Feature

## Overview
The Tender Management Application now includes **image preview functionality** for bank account documents. This feature allows you to quickly preview uploaded bank statements and verification documents without opening external applications.

## How to Use Image Preview

### 1. Access Bank Account Management
1. Open the Tender Management Application
2. Click **"Manage Database"**
3. Select or create a company
4. Go to the **"Bank Account"** tab

### 2. Upload Bank Documents
1. Click **"Upload Bank Document"**
2. Select your bank statement file (supports images and PDFs)
3. Enter document type (e.g., "Bank Statement", "Account Verification")
4. Click save

### 3. Preview Images
**Method 1: Right-Click Preview**
- Right-click on any document in the list
- A tooltip will appear showing:
  - Document information
  - Thumbnail preview of the image/PDF

**Method 2: Double-Click Preview**
- Double-click on any document in the list
- Same preview functionality as right-click

### 4. Supported File Types
- **Images**: JPG, JPEG, PNG, BMP, TIFF, GIF
- **PDFs**: First page preview (requires PyMuPDF)
- **Preview Size**: Automatically scaled to 200x150 pixels

## Features
- ✅ **Instant Preview**: No need to open external applications
- ✅ **Multiple Formats**: Supports both images and PDF documents  
- ✅ **Smart Scaling**: Images automatically resized for optimal viewing
- ✅ **Document Info**: Shows file name, type, and size
- ✅ **PDF Support**: Preview first page of PDF documents
- ✅ **Error Handling**: Graceful fallback if preview fails

## Tips
- **File Organization**: Use descriptive document types for easy identification
- **File Size**: Smaller files load faster for preview
- **PDF Quality**: Higher quality PDFs provide better preview images
- **Multiple Documents**: Upload multiple statements for complete records

## Troubleshooting
- **No Preview Showing**: Check file exists and is supported format
- **PDF Preview Issues**: Ensure file is not corrupted or password protected
- **Slow Loading**: Large files may take a moment to generate preview
- **Preview Errors**: Error message will display if preview cannot be generated

## Technical Notes
- Previews are generated in real-time (not stored)
- Original files are preserved unchanged
- Memory usage is optimized with thumbnail scaling
- Supports both relative and absolute file paths

This feature enhances the document management workflow by providing immediate visual confirmation of uploaded bank account verification materials.