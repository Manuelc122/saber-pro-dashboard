import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import os

# Create the processed directory if it doesn't exist
os.makedirs('data/processed', exist_ok=True)

# Database path
db_path = Path('data/processed/saber_pro.db')

# Create connection
conn = sqlite3.connect(db_path)

# Create table
conn.execute("""
CREATE TABLE IF NOT EXISTS saber_pro (
    periodo TEXT,
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

# Generate sample data
np.random.seed(42)
n_samples = 10000

# Generate data
data = {
    'periodo': np.random.choice(['2018', '2019', '2020', '2021', '2022'], n_samples),
    'estu_consecutivo': [f'EST{i:06d}' for i in range(n_samples)],
    'estu_genero': np.random.choice(['M', 'F'], n_samples),
    'estu_valormatriculauniversidad': np.random.choice([
        'Menos de 500 mil',
        'Entre 500 mil y menos de 1 millón',
        'Entre 1 millón y menos de 2.5 millones',
        'Entre 2.5 millones y menos de 4 millones',
        'Entre 4 millones y menos de 5.5 millones',
        'Entre 5.5 millones y menos de 7 millones',
        'Más de 7 millones'
    ], n_samples),
    'fami_estratovivienda': [f'Estrato {i}' for i in np.random.randint(1, 7, n_samples)],
    'fami_educacionpadre': np.random.choice([
        'Ninguno',
        'Primaria incompleta',
        'Primaria completa',
        'Secundaria (Bachillerato) incompleta',
        'Secundaria (Bachillerato) completa',
        'Técnica o tecnológica incompleta',
        'Técnica o tecnológica completa',
        'Educación profesional incompleta',
        'Educación profesional completa',
        'Postgrado'
    ], n_samples),
    'fami_educacionmadre': np.random.choice([
        'Ninguno',
        'Primaria incompleta',
        'Primaria completa',
        'Secundaria (Bachillerato) incompleta',
        'Secundaria (Bachillerato) completa',
        'Técnica o tecnológica incompleta',
        'Técnica o tecnológica completa',
        'Educación profesional incompleta',
        'Educación profesional completa',
        'Postgrado'
    ], n_samples),
    'fami_tieneinternet': np.random.choice(['Si', 'No'], n_samples),
    'fami_tienecomputador': np.random.choice(['Si', 'No'], n_samples),
    'fami_tieneautomovil': np.random.choice(['Si', 'No'], n_samples),
    'fami_tienelavadora': np.random.choice(['Si', 'No'], n_samples),
    'estu_horassemanatrabaja': np.random.choice([
        'No trabaja',
        'Menos de 10 horas',
        'Entre 11 y 20 horas',
        'Entre 21 y 30 horas',
        'Más de 30 horas'
    ], n_samples),
    'inst_origen': np.random.choice([
        'OFICIAL',
        'NO OFICIAL',
        'REGIMEN ESPECIAL'
    ], n_samples),
    'mod_razona_cuantitat_punt': np.random.normal(150, 30, n_samples),
    'mod_lectura_critica_punt': np.random.normal(150, 30, n_samples),
    'mod_ingles_punt': np.random.normal(150, 30, n_samples),
    'mod_competen_ciudada_punt': np.random.normal(150, 30, n_samples)
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to database
df.to_sql('saber_pro', conn, if_exists='replace', index=False)

# Create indexes for better performance
print("Creating indexes...")
conn.execute("CREATE INDEX IF NOT EXISTS idx_periodo ON saber_pro(periodo)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_genero ON saber_pro(estu_genero)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_estrato ON saber_pro(fami_estratovivienda)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_inst_origen ON saber_pro(inst_origen)")

# Verify data
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM saber_pro")
count = cursor.fetchone()[0]
print(f"Total records in database: {count:,}")

# Close connection
conn.close()

print("Test database created successfully!") 