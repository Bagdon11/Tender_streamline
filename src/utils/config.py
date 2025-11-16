"""
Configuration Manager - Handle application settings and configuration
"""

import json
import os
from typing import Dict, Any, Optional

class Config:
    """Application configuration manager."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.settings: Dict[str, Any] = {}
        
        # Default settings
        self.default_settings = {
            "app": {
                "name": "Tender Management System",
                "version": "1.0.0",
                "window_geometry": "1200x800",
                "theme": "default"
            },
            "paths": {
                "data_dir": "data",
                "documents_dir": "data/documents",
                "checklists_dir": "data/checklists", 
                "projects_dir": "data/projects",
                "temp_dir": "temp"
            },
            "parsing": {
                "max_file_size_mb": 50,
                "supported_formats": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt"],
                "encoding_fallback": "utf-8"
            },
            "search": {
                "min_word_length": 3,
                "max_results": 20,
                "snippet_length": 200
            },
            "pipeline": {
                "auto_save": True,
                "backup_frequency_minutes": 30,
                "max_file_uploads_per_section": 50
            },
            "ui": {
                "show_tips": True,
                "confirm_deletions": True,
                "auto_refresh": True,
                "font_size": 10
            }
        }
        
        # Load settings
        self.load_settings()
        
        # Ensure required directories exist
        self.create_directories()
    
    def load_settings(self):
        """Load settings from config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    
                # Merge with defaults (preserve any new defaults)
                self.settings = self._merge_settings(self.default_settings, loaded_settings)
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load config file: {e}")
                self.settings = self.default_settings.copy()
        else:
            # Use defaults and save them
            self.settings = self.default_settings.copy()
            self.save_settings()
    
    def save_settings(self):
        """Save current settings to config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save config file: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation.
        
        Args:
            key_path: Path to setting (e.g., 'app.name' or 'paths.data_dir')
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        keys = key_path.split('.')
        value = self.settings
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        Set a setting value using dot notation.
        
        Args:
            key_path: Path to setting (e.g., 'app.theme')
            value: Value to set
        """
        keys = key_path.split('.')
        current = self.settings
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final key
        current[keys[-1]] = value
        
        # Auto-save if enabled
        if self.get('pipeline.auto_save', True):
            self.save_settings()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        return self.settings.get(section, {})
    
    def update_section(self, section: str, updates: Dict[str, Any]):
        """Update multiple settings in a section."""
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section].update(updates)
        
        if self.get('pipeline.auto_save', True):
            self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = self.default_settings.copy()
        self.save_settings()
    
    def create_directories(self):
        """Create required directories if they don't exist."""
        paths = self.get_section('paths')
        
        for path_key, path_value in paths.items():
            if path_value and not os.path.exists(path_value):
                try:
                    os.makedirs(path_value, exist_ok=True)
                except OSError as e:
                    print(f"Warning: Could not create directory {path_value}: {e}")
    
    def get_data_path(self, filename: str = "") -> str:
        """Get path within the data directory."""
        data_dir = self.get('paths.data_dir', 'data')
        if filename:
            return os.path.join(data_dir, filename)
        return data_dir
    
    def get_documents_path(self, filename: str = "") -> str:
        """Get path within the documents directory."""
        docs_dir = self.get('paths.documents_dir', 'data/documents')
        if filename:
            return os.path.join(docs_dir, filename)
        return docs_dir
    
    def get_projects_path(self, filename: str = "") -> str:
        """Get path within the projects directory."""
        projects_dir = self.get('paths.projects_dir', 'data/projects')
        if filename:
            return os.path.join(projects_dir, filename)
        return projects_dir
    
    def is_file_supported(self, filepath: str) -> bool:
        """Check if file format is supported."""
        _, ext = os.path.splitext(filepath.lower())
        supported_formats = self.get('parsing.supported_formats', [])
        return ext in supported_formats
    
    def get_max_file_size(self) -> int:
        """Get maximum allowed file size in bytes."""
        max_mb = self.get('parsing.max_file_size_mb', 50)
        return max_mb * 1024 * 1024
    
    def _merge_settings(self, defaults: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge loaded settings with defaults."""
        result = defaults.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def export_config(self, filepath: str):
        """Export current configuration to a file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            raise IOError(f"Failed to export config to {filepath}: {e}")
    
    def import_config(self, filepath: str):
        """Import configuration from a file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                imported_settings = json.load(f)
                
            # Merge with current settings
            self.settings = self._merge_settings(self.settings, imported_settings)
            self.save_settings()
            
        except (json.JSONDecodeError, IOError) as e:
            raise IOError(f"Failed to import config from {filepath}: {e}")
    
    def validate_config(self) -> bool:
        """Validate current configuration."""
        required_sections = ['app', 'paths', 'parsing', 'search', 'pipeline', 'ui']
        
        for section in required_sections:
            if section not in self.settings:
                print(f"Warning: Missing config section: {section}")
                return False
        
        # Validate paths exist
        paths = self.get_section('paths')
        for path_name, path_value in paths.items():
            if not os.path.exists(path_value):
                print(f"Warning: Path does not exist: {path_name} = {path_value}")
        
        return True