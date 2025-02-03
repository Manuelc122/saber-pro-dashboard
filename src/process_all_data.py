from data_processing import SaberProProcessor

def main():
    # File path to your dataset
    file_path = '/Users/manuelcastillo/Documents/Saber_pro_dataset/Resultados__nicos_Saber_Pro_20250201.csv'
    
    # Initialize and run processor
    processor = SaberProProcessor(file_path)
    processor.process_data(chunk_size=50000)

if __name__ == "__main__":
    main() 