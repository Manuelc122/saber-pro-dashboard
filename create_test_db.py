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

# Set random seed for reproducibility
np.random.seed(42)

# Define strata and sample size per stratum
strata = ['Estrato 1', 'Estrato 2', 'Estrato 3', 'Estrato 4', 'Estrato 5', 'Estrato 6']
samples_per_stratum = 2000
total_samples = len(strata) * samples_per_stratum

# Initialize empty lists for each column
data = {
    'periodo': [],
    'estu_consecutivo': [],
    'estu_genero': [],
    'estu_valormatriculauniversidad': [],
    'fami_estratovivienda': [],
    'fami_educacionpadre': [],
    'fami_educacionmadre': [],
    'fami_tieneinternet': [],
    'fami_tienecomputador': [],
    'fami_tieneautomovil': [],
    'fami_tienelavadora': [],
    'estu_horassemanatrabaja': [],
    'inst_origen': [],
    'mod_razona_cuantitat_punt': [],
    'mod_lectura_critica_punt': [],
    'mod_ingles_punt': [],
    'mod_competen_ciudada_punt': []
}

# Generate data for each stratum
for stratum in strata:
    # Adjust probabilities based on stratum
    stratum_num = int(stratum[-1])
    
    # Higher probability of better conditions for higher strata
    prob_internet = min(0.2 + stratum_num * 0.12, 0.95)
    prob_computer = min(0.2 + stratum_num * 0.12, 0.95)
    prob_car = min(0.1 + stratum_num * 0.15, 0.9)
    prob_washer = min(0.3 + stratum_num * 0.12, 0.95)
    
    # Score means increase slightly with stratum
    base_mean = 140 + stratum_num * 5
    score_std = 20
    
    for i in range(samples_per_stratum):
        data['periodo'].append(np.random.choice(['20181', '20182', '20191', '20192', '20201', '20202', '20211', '20212']))
        data['estu_consecutivo'].append(f'EST{len(data["estu_consecutivo"]):06d}')
        data['estu_genero'].append(np.random.choice(['M', 'F']))
        # Calculate probabilities for matricula values that sum to 1
        matricula_probs = np.array([
            max(0.3-0.05*stratum_num, 0.05),  # Menos de 500 mil
            max(0.3-0.05*stratum_num, 0.05),  # Entre 500 mil y menos de 1 millón
            0.2,                              # Entre 1 millón y menos de 2.5 millones
            min(0.1+0.02*stratum_num, 0.2),   # Entre 2.5 millones y menos de 4 millones
            min(0.05+0.02*stratum_num, 0.15), # Entre 4 millones y menos de 5.5 millones
            min(0.03+0.02*stratum_num, 0.13), # Entre 5.5 millones y menos de 7 millones
            min(0.02+0.02*stratum_num, 0.12)  # Más de 7 millones
        ])
        # Normalize probabilities to sum to 1
        matricula_probs = matricula_probs / matricula_probs.sum()
        
        data['estu_valormatriculauniversidad'].append(np.random.choice([
            'Menos de 500 mil',
            'Entre 500 mil y menos de 1 millón',
            'Entre 1 millón y menos de 2.5 millones',
            'Entre 2.5 millones y menos de 4 millones',
            'Entre 4 millones y menos de 5.5 millones',
            'Entre 5.5 millones y menos de 7 millones',
            'Más de 7 millones'
        ], p=matricula_probs))
        data['fami_estratovivienda'].append(stratum)
        
        # Education levels correlated with stratum
        education_levels = [
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
        ]
        
        # Adjust probabilities based on stratum
        edu_probs = np.array([0.15, 0.15, 0.15, 0.15, 0.15, 0.1, 0.1, 0.02, 0.02, 0.01])
        edu_probs = np.roll(edu_probs, stratum_num)  # Shift probabilities based on stratum
        edu_probs = edu_probs / edu_probs.sum()  # Normalize probabilities
        
        data['fami_educacionpadre'].append(np.random.choice(education_levels, p=edu_probs))
        data['fami_educacionmadre'].append(np.random.choice(education_levels, p=edu_probs))
        
        data['fami_tieneinternet'].append(np.random.choice(['Si', 'No'], p=[prob_internet, 1-prob_internet]))
        data['fami_tienecomputador'].append(np.random.choice(['Si', 'No'], p=[prob_computer, 1-prob_computer]))
        data['fami_tieneautomovil'].append(np.random.choice(['Si', 'No'], p=[prob_car, 1-prob_car]))
        data['fami_tienelavadora'].append(np.random.choice(['Si', 'No'], p=[prob_washer, 1-prob_washer]))
        
        # Calculate probabilities for working hours that sum to 1
        work_probs = np.array([
            0.4+0.05*stratum_num,  # No trabaja
            0.2,                   # Menos de 10 horas
            0.2,                   # Entre 11 y 20 horas
            0.1,                   # Entre 21 y 30 horas
            max(0.1-0.05*stratum_num, 0.01)  # Más de 30 horas (minimum 1%)
        ])
        # Normalize probabilities to sum to 1
        work_probs = work_probs / work_probs.sum()
        
        data['estu_horassemanatrabaja'].append(np.random.choice([
            'No trabaja',
            'Menos de 10 horas',
            'Entre 11 y 20 horas',
            'Entre 21 y 30 horas',
            'Más de 30 horas'
        ], p=work_probs))
        
        data['inst_origen'].append(np.random.choice([
            'OFICIAL',
            'NO OFICIAL',
            'REGIMEN ESPECIAL'
        ], p=[0.7-0.1*stratum_num, 0.25+0.1*stratum_num, 0.05]))
        
        # Generate correlated scores
        base_score = np.random.normal(base_mean, score_std)
        data['mod_razona_cuantitat_punt'].append(max(0, min(300, base_score + np.random.normal(0, 10))))
        data['mod_lectura_critica_punt'].append(max(0, min(300, base_score + np.random.normal(0, 10))))
        data['mod_ingles_punt'].append(max(0, min(300, base_score + np.random.normal(0, 15))))
        data['mod_competen_ciudada_punt'].append(max(0, min(300, base_score + np.random.normal(0, 10))))

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
total_count = cursor.fetchone()[0]
print(f"Total records in database: {total_count:,}")

# Verify distribution across strata
print("\nDistribution across strata:")
cursor.execute("""
    SELECT fami_estratovivienda, COUNT(*) as count
    FROM saber_pro
    GROUP BY fami_estratovivienda
    ORDER BY fami_estratovivienda
""")
for stratum, count in cursor.fetchall():
    print(f"{stratum}: {count:,} records")

# Close connection
conn.close()

print("\nTest database created successfully!") 