from data_processing import SaberProProcessor
import time

def main():
    # File path to your dataset
    file_path = '/Users/manuelcastillo/Documents/Saber_pro_dataset/Resultados__nicos_Saber_Pro_20250201.csv'
    
    # Initialize processor
    processor = SaberProProcessor(file_path)
    
    # Process data
    start_time = time.time()
    processor.process_data(chunk_size=50000)
    
    # Get and print basic stats
    stats = processor.get_basic_stats()
    print("\nData Processing Summary:")
    print("\nPeriod Distribution:")
    print(stats['period_distribution'])
    print("\nAverage Scores by Period:")
    print(stats['average_scores'])
    
    elapsed_time = time.time() - start_time
    print(f"\nTotal processing time: {elapsed_time/60:.2f} minutes")

if __name__ == "__main__":
    main() 