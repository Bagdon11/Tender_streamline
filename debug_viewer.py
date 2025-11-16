#!/usr/bin/env python3
"""
Debug script to test the GUI document upload and viewing
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import os
sys.path.insert(0, 'src')

from src.core.document_parser import DocumentParser

def debug_gui():
    # Test document parsing
    parser = DocumentParser()
    
    try:
        content = parser.parse_file('sample_tender.txt')
        print(f"Parsed content length: {len(content)}")
        print(f"Content type: {type(content)}")
        print(f"First 100 chars: {repr(content[:100])}")
        
        # Create simple GUI to test viewer
        root = tk.Tk()
        root.title("Debug Document Viewer")
        root.geometry("800x600")
        
        text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert content
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        
        print("GUI created, starting mainloop...")
        root.mainloop()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_gui()