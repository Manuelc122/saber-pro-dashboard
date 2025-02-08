import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
import logging
from tqdm import tqdm
from typing import Dict
import os

class SaberProProcessor:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.db_path = Path('data/processed/saber_pro.db')
        self.setup_logging()
        self.setup_database()
    
    def setup_logging(self):
        """Configure logging for the data processing"""
        log_path = Path(__file__).parent.parent / 'data' / 'processed' / 'data_processing.log'
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(log_path)),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        # Create the processed directory if it doesn't exist
        os.makedirs(self.db_path.parent, exist_ok=True)
        self.logger.info(f"Creating database at: {self.db_path}")
        
        # Create connection and table
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS saber_pro (
            periodo TEXT,
            year TEXT,
            period_number TEXT,
            estu_consecutivo TEXT,
            estu_genero TEXT,
            estu_valormatriculauniversidad TEXT,
            fami_estratovivienda TEXT,
            fami_educacionpadre TEXT,
            fami_educacionmadre TEXT,
            fami_tieneinternet TEXT,
            fami_tienecomputador TEXT,
            fami_tieneautomovil TEXT,
            fami_tienelavadora TEXT,
            estu_horassemanatrabaja TEXT,
            inst_origen TEXT,
            mod_razona_cuantitat_punt REAL,
            mod_lectura_critica_punt REAL,
            mod_ingles_punt REAL,
            mod_competen_ciudada_punt REAL
        )
        """)
        conn.close()
    
    def process_data(self, chunk_size=50000, max_rows=None):
        self.logger.info("Starting data processing...")
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        
        # Process CSV in chunks
        chunks = pd.read_csv(
            self.csv_path,
            chunksize=chunk_size,
            dtype={'PERIODO': str},  # Ensure periodo is read as string
            usecols=[
                'PERIODO', 'ESTU_CONSECUTIVO', 'ESTU_GENERO',
                'ESTU_VALORMATRICULAUNIVERSIDAD', 'FAMI_ESTRATOVIVIENDA',
                'FAMI_EDUCACIONPADRE', 'FAMI_EDUCACIONMADRE',
                'FAMI_TIENEINTERNET', 'FAMI_TIENECOMPUTADOR',
                'FAMI_TIENEAUTOMOVIL', 'FAMI_TIENELAVADORA',
                'ESTU_HORASSEMANATRABAJA', 'INST_ORIGEN',
                'MOD_RAZONA_CUANTITAT_PUNT', 'MOD_LECTURA_CRITICA_PUNT',
                'MOD_INGLES_PUNT', 'MOD_COMPETEN_CIUDADA_PUNT'
            ]
        )
        
        rows_processed = 0
        for chunk in chunks:
            # Rename columns to match database schema
            chunk.columns = [col.lower() for col in chunk.columns]
            
            # Format year from periodo (e.g., '20183' to '2018')
            chunk['year'] = chunk['periodo'].astype(str).str[:4]
            chunk['period_number'] = chunk['periodo'].astype(str).str[4:]
            
            # Convert numeric columns
            numeric_cols = ['mod_razona_cuantitat_punt', 'mod_lectura_critica_punt',
                          'mod_ingles_punt', 'mod_competen_ciudada_punt']
            for col in numeric_cols:
                chunk[col] = pd.to_numeric(chunk[col], errors='coerce')
            
            # Save to database
            chunk.to_sql('saber_pro', conn, if_exists='append', index=False)
            
            rows_processed += len(chunk)
            self.logger.info(f"Processed {rows_processed:,} rows")
            
            if max_rows and rows_processed >= max_rows:
                break
        
        # Create indexes for better performance
        self.logger.info("Creating indexes...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_year ON saber_pro(year)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_periodo ON saber_pro(periodo)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_genero ON saber_pro(estu_genero)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_estrato ON saber_pro(fami_estratovivienda)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_inst_origen ON saber_pro(inst_origen)")
        
        # Get total count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM saber_pro")
        total_count = cursor.fetchone()[0]
        self.logger.info(f"Total records in database: {total_count:,}")
        
        conn.close()
        self.logger.info("Data processing completed!")
    
    def get_basic_stats(self):
        conn = sqlite3.connect(self.db_path)
        
        # Get year and period distribution
        period_dist = pd.read_sql("""
            SELECT 
                year,
                period_number,
                COUNT(*) as count
            FROM saber_pro
            GROUP BY year, period_number
            ORDER BY year, period_number
        """, conn)
        
        # Get average scores by year
        avg_scores = pd.read_sql("""
            SELECT 
                year,
                ROUND(AVG(mod_razona_cuantitat_punt), 2) as avg_razona_cuantitat,
                ROUND(AVG(mod_lectura_critica_punt), 2) as avg_lectura_critica,
                ROUND(AVG(mod_ingles_punt), 2) as avg_ingles,
                ROUND(AVG(mod_competen_ciudada_punt), 2) as avg_competen_ciudada,
                COUNT(*) as students
            FROM saber_pro
            GROUP BY year
            ORDER BY year
        """, conn)
        
        conn.close()
        
        return {
            'period_distribution': period_dist,
            'average_scores': avg_scores
        }

def query_db(query, params=None):
    """Helper function to run SQL queries"""
    try:
        # Use the same path configuration as app.py
        if os.environ.get('RENDER'):
            # Production path on Render
            db_path = Path('/opt/render/project/src/data/processed/saber_pro.db')
        else:
            # Development path
            db_path = Path(__file__).parent.parent / 'data' / 'processed' / 'saber_pro.db'
        
        if not db_path.exists():
            print(f"Database not found at: {db_path}")
            return pd.DataFrame()
            
        conn = sqlite3.connect(db_path)
        
        try:
            if params:
                result = pd.read_sql_query(query, conn, params=params)
            else:
                result = pd.read_sql_query(query, conn)
                
            # Add debug information
            print(f"Query successful. Returned {len(result)} rows")
            return result
            
        except sqlite3.Error as e:
            print(f"SQLite error: {str(e)}")
            print(f"Query: {query}")
            if params:
                print(f"Parameters: {params}")
            return pd.DataFrame()
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Database error: {str(e)}")
        print(f"Using database path: {db_path}")
        return pd.DataFrame()

def get_regression_data():
    """Get clean data for regression analysis"""
    with open('sql/queries.sql', 'r') as file:
        queries = file.read().split(';')
    
    # Run data quality check
    quality_check = query_db(queries[0])
    print("Data quality check:")
    print(quality_check)
    
    # Get regression data
    regression_data = query_db(queries[1])
    
    # Clean and prepare data
    regression_data_clean = regression_data.dropna()
    
    return regression_data_clean

def prepare_regression_variables(data):
    """Prepare variables for regression analysis"""
    X = data[[
        'estrato', 'is_public', 'is_male', 'father_education', 'mother_education',
        'has_internet', 'has_computer', 'self_paid', 'parent_paid'
    ]].astype(float)
    
    y = data['avg_score'].astype(float)
    
    return X, y 

if __name__ == '__main__':
    # Path to the actual CSV file
    csv_path = '/Users/manuelcastillo/Documents/Saber_pro_dataset/Resultados__nicos_Saber_Pro_20250201.csv'
    
    # Create processor instance
    processor = SaberProProcessor(csv_path)
    
    try:
        # Process only 10,000 records with a smaller chunk size
        processor.process_data(chunk_size=1000, max_rows=10000)
        print("Data processing completed successfully!")
        
        # Calculate and display basic stats
        stats = processor.get_basic_stats()
        print("\nBasic Statistics:")
        print("\nPeriod Distribution:")
        print(stats['period_distribution'])
        print("\nAverage Scores by Period:")
        print(stats['average_scores'])
        
    except Exception as e:
        print(f"Error processing data: {str(e)}") 