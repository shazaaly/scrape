"""
Data export utilities for the Playwright Web Scraper.
"""

import json
import csv
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class DataExporter:
    """
    Handles exporting scraped data to various formats.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def export(self, data: List[Dict[str, Any]], filename: str, format_type: str) -> str:
        """
        Export data to specified format.
        
        Args:
            data: List of dictionaries containing scraped data
            filename: Output filename (without extension)
            format_type: Export format ('json', 'csv', 'excel')
            
        Returns:
            Full path to the exported file
        """
        if not data:
            self.logger.warning("No data to export")
            return None
        
        # Clean and validate data
        cleaned_data = self.clean_data(data)
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{filename}_{timestamp}"
        
        if format_type.lower() == 'json':
            return self.export_json(cleaned_data, base_filename)
        elif format_type.lower() == 'csv':
            return self.export_csv(cleaned_data, base_filename)
        elif format_type.lower() == 'excel':
            return self.export_excel(cleaned_data, base_filename)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def clean_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and validate scraped data.
        
        Args:
            data: Raw scraped data
            
        Returns:
            Cleaned data
        """
        cleaned_data = []
        
        for item in data:
            if not isinstance(item, dict):
                continue
            
            cleaned_item = {}
            
            for key, value in item.items():
                # Skip None values
                if value is None:
                    continue
                
                # Clean string values
                if isinstance(value, str):
                    cleaned_value = value.strip()
                    if cleaned_value:  # Only keep non-empty strings
                        cleaned_item[key] = cleaned_value
                elif isinstance(value, dict):
                    # Keep dictionaries as JSON strings for CSV compatibility
                    if value:  # Only keep non-empty dicts
                        cleaned_item[key] = value
                elif isinstance(value, list):
                    # Keep lists as JSON strings for CSV compatibility
                    if value:  # Only keep non-empty lists
                        cleaned_item[key] = value
                else:
                    cleaned_item[key] = value
            
            if cleaned_item:  # Only add non-empty items
                cleaned_data.append(cleaned_item)
        
        self.logger.info(f"Cleaned data: {len(data)} -> {len(cleaned_data)} items")
        return cleaned_data
    
    def export_json(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Export data to JSON format.
        
        Args:
            data: Cleaned scraped data
            filename: Output filename
            
        Returns:
            Full path to the exported file
        """
        output_file = f"{filename}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'exported_at': datetime.now().isoformat(),
                        'total_items': len(data),
                        'format': 'json'
                    },
                    'data': data
                }, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Data exported to JSON: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {str(e)}")
            raise
    
    def export_csv(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Export data to CSV format.
        
        Args:
            data: Cleaned scraped data
            filename: Output filename
            
        Returns:
            Full path to the exported file
        """
        output_file = f"{filename}.csv"
        
        if not data:
            self.logger.warning("No data to export to CSV")
            return output_file
        
        try:
            # Flatten nested dictionaries and lists for CSV compatibility
            flattened_data = []
            for item in data:
                flattened_item = self.flatten_dict(item)
                flattened_data.append(flattened_item)
            
            # Use pandas for better CSV handling
            df = pd.DataFrame(flattened_data)
            
            # Clean column names
            df.columns = [self.clean_column_name(col) for col in df.columns]
            
            # Export to CSV
            df.to_csv(output_file, index=False, encoding='utf-8')
            
            self.logger.info(f"Data exported to CSV: {output_file}")
            self.logger.info(f"CSV shape: {df.shape[0]} rows, {df.shape[1]} columns")
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {str(e)}")
            raise
    
    def export_excel(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Export data to Excel format.
        
        Args:
            data: Cleaned scraped data
            filename: Output filename
            
        Returns:
            Full path to the exported file
        """
        output_file = f"{filename}.xlsx"
        
        if not data:
            self.logger.warning("No data to export to Excel")
            return output_file
        
        try:
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Clean column names
            df.columns = [self.clean_column_name(col) for col in df.columns]
            
            # Export to Excel with metadata sheet
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Main data sheet
                df.to_excel(writer, sheet_name='Scraped_Data', index=False)
                
                # Metadata sheet
                metadata_df = pd.DataFrame({
                    'Property': ['Exported At', 'Total Items', 'Columns', 'Format'],
                    'Value': [
                        datetime.now().isoformat(),
                        len(data),
                        df.shape[1],
                        'excel'
                    ]
                })
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            self.logger.info(f"Data exported to Excel: {output_file}")
            self.logger.info(f"Excel shape: {df.shape[0]} rows, {df.shape[1]} columns")
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"Failed to export Excel: {str(e)}")
            raise
    
    def flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """
        Flatten nested dictionary for CSV export.
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to JSON strings
                items.append((new_key, json.dumps(v, default=str)))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def clean_column_name(self, name: str) -> str:
        """
        Clean column names for better readability.
        
        Args:
            name: Original column name
            
        Returns:
            Cleaned column name
        """
        # Replace underscores with spaces and title case
        cleaned = name.replace('_', ' ').title()
        
        # Handle common abbreviations
        replacements = {
            'Url': 'URL',
            'Html': 'HTML',
            'Css': 'CSS',
            'Id': 'ID',
            'Api': 'API'
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned
    
    def get_summary_stats(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for scraped data.
        
        Args:
            data: Scraped data
            
        Returns:
            Dictionary containing summary statistics
        """
        if not data:
            return {'total_items': 0}
        
        # Basic stats
        stats = {
            'total_items': len(data),
            'unique_urls': len(set(item.get('url', '') for item in data)),
            'unique_selectors': len(set(item.get('selector', '') for item in data))
        }
        
        # Field coverage
        all_fields = set()
        for item in data:
            all_fields.update(item.keys())
        
        field_coverage = {}
        for field in all_fields:
            count = sum(1 for item in data if field in item and item[field])
            field_coverage[field] = {
                'count': count,
                'percentage': (count / len(data)) * 100
            }
        
        stats['total_fields'] = len(all_fields)
        stats['field_coverage'] = field_coverage
        
        return stats
