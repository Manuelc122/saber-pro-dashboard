#!/usr/bin/env python

from src.data_processing import SaberProProcessor
import sys
import os


def main():
    # Specify your CSV file path here - update this to the correct path of your CSV file
    csv_file_path = "/Users/manuelcastillo/Documents/Saber_pro_dataset/Resultados__nicos_Saber_Pro_20250201.csv"
    
    if not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        sys.exit(1)
        
    print("Starting database creation process...")
    processor = SaberProProcessor(csv_file_path)
    processor.process_data()
    print("Database created and populated successfully!")


if __name__ == '__main__':
    main() 