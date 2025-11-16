#!/usr/bin/env python3
"""
Tender Management Application
Main entry point for the tender management system.
"""
                                                  # C:/Users/steve/Tender_streamline/.venv/Scripts/python.exe main.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MainWindow
from src.utils.config import Config

def main():
    """Main application entry point."""
    try:
        # Initialize configuration
        config = Config()
        
        # Create main window
        root = tk.Tk()
        root.title("Tender Management System")
        root.geometry("1200x800")
        root.minsize(800, 600)
        
        # Set application icon (if available)
        try:
            root.iconbitmap('assets/icon.ico')
        except:
            pass  # Icon file not found, continue without it
        
        # Create and run the main application
        app = MainWindow(root, config)
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() - root.winfo_width()) // 2
        y = (root.winfo_screenheight() - root.winfo_height()) // 2
        root.geometry(f"+{x}+{y}")
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()