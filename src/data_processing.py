import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
import logging
from tqdm import tqdm
from typing import Dict

class SaberProProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.setup_logging()
        
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
        
    def create_database(self) -> Path:
        """Create SQLite database with proper schema"""
        # Use absolute path
        db_path = Path(__file__).parent.parent / 'data' / 'processed' / 'saber_pro.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Creating database at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        
        # Drop existing table if it exists
        conn.execute("DROP TABLE IF EXISTS saber_pro")
        
        # Create the main table with all columns
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS saber_pro (
            periodo TEXT,
            estu_consecutivo TEXT,
            estu_tipodocumento TEXT,
            estu_pais_reside TEXT,
            estu_cod_reside_depto TEXT,
            estu_depto_reside TEXT,
            estu_cod_reside_mcpio TEXT,
            estu_mcpio_reside TEXT,
            estu_coddane_cole_termino TEXT,
            estu_cod_cole_mcpio_termino TEXT,
            estu_cod_depto_presentacion TEXT,
            inst_cod_institucion TEXT,
            inst_nombre_institucion TEXT,
            inst_caracter_academico TEXT,
            estu_nucleo_pregrado TEXT,
            estu_inst_departamento TEXT,
            estu_inst_codmunicipio TEXT,
            estu_inst_municipio TEXT,
            estu_prgm_academico TEXT,
            estu_prgm_departamento TEXT,
            estu_prgm_codmunicipio TEXT,
            estu_prgm_municipio TEXT,
            estu_nivel_prgm_academico TEXT,
            estu_metodo_prgm TEXT,
            estu_valormatriculauniversidad TEXT,
            estu_depto_presentacion TEXT,
            estu_cod_mcpio_presentacion TEXT,
            estu_mcpio_presentacion TEXT,
            estu_pagomatriculabeca TEXT,
            estu_pagomatriculacredito TEXT,
            estu_horassemanatrabaja TEXT,
            estu_snies_prgmacademico TEXT,
            estu_privado_libertad TEXT,
            estu_nacionalidad TEXT,
            estu_estudiante TEXT,
            estu_genero TEXT,
            estu_cole_termino TEXT,
            estu_pagomatriculapadres TEXT,
            estu_estadoinvestigacion TEXT,
            estu_fechanacimiento TEXT,
            estu_pagomatriculapropio TEXT,
            estu_tipodocumentosb11 TEXT,
            fami_educacionpadre TEXT,
            fami_tieneautomovil TEXT,
            fami_tienelavadora TEXT,
            fami_estratovivienda TEXT,
            fami_tienecomputador TEXT,
            fami_tieneinternet TEXT,
            fami_educacionmadre TEXT,
            inst_origen TEXT,
            mod_razona_cuantitat_punt REAL,
            mod_comuni_escrita_punt REAL,
            mod_comuni_escrita_desem TEXT,
            mod_ingles_desem TEXT,
            mod_lectura_critica_punt REAL,
            mod_ingles_punt REAL,
            mod_competen_ciudada_punt REAL
        )
        """
        
        conn.execute(create_table_sql)
        conn.close()
        
        return db_path
    
    def process_data(self, chunk_size: int = 50000) -> None:
        """Process the entire dataset in chunks"""
        db_path = self.create_database()
        conn = sqlite3.connect(db_path)
        
        # Calculate total chunks for progress bar
        total_rows = sum(1 for _ in open(self.file_path)) - 1
        total_chunks = (total_rows // chunk_size) + 1
        
        self.logger.info(f"Starting data processing: {total_rows:,} total rows")
        
        chunks = pd.read_csv(self.file_path, chunksize=chunk_size)
        for i, chunk in enumerate(tqdm(chunks, total=total_chunks, desc="Processing chunks")):
            try:
                # Convert column names to lowercase
                chunk.columns = chunk.columns.str.lower()
                
                # Write to SQLite
                chunk.to_sql('saber_pro', conn, if_exists='append', index=False)
                
                # Commit every chunk
                conn.commit()
                
            except Exception as e:
                self.logger.error(f"Error processing chunk {i}: {str(e)}")
                conn.rollback()
                raise
        
        # Create indexes for better query performance
        print("\nCreating indexes...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_periodo ON saber_pro(periodo)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_genero ON saber_pro(estu_genero)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_estrato ON saber_pro(fami_estratovivienda)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_inst_caracter ON saber_pro(inst_caracter_academico)")
        
        # Verify data loading
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM saber_pro")
        total_count = cursor.fetchone()[0]
        print(f"\nTotal records loaded: {total_count:,}")
        
        conn.close()
        self.logger.info("Data processing completed successfully")
    
    def get_basic_stats(self) -> Dict:
        """Calculate basic statistics from the processed database"""
        db_path = Path(__file__).parent.parent / 'data' / 'processed' / 'saber_pro.db'
        conn = sqlite3.connect(db_path)
        
        stats = {}
        
        # Get period distribution
        period_query = """
        SELECT periodo, COUNT(*) as count
        FROM saber_pro
        GROUP BY periodo
        ORDER BY periodo
        """
        stats['period_distribution'] = pd.read_sql_query(period_query, conn)
        
        # Get average scores by period
        scores_query = """
        SELECT 
            periodo,
            ROUND(AVG(mod_razona_cuantitat_punt), 2) as avg_math,
            ROUND(AVG(mod_lectura_critica_punt), 2) as avg_reading,
            ROUND(AVG(mod_ingles_punt), 2) as avg_english
        FROM saber_pro
        GROUP BY periodo
        ORDER BY periodo
        """
        stats['average_scores'] = pd.read_sql_query(scores_query, conn)
        
        conn.close()
        return stats 

def query_db(query, params=None):
    """Helper function to run SQL queries"""
    try:
        # Use absolute path with Path
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

# Remove the __main__ block from the file 