-- Create the main table
CREATE TABLE saber_pro (
    periodo TEXT,
    estu_consecutivo TEXT PRIMARY KEY,
    estu_genero TEXT,
    estu_inst_departamento TEXT,
    inst_nombre_institucion TEXT,
    estu_prgm_academico TEXT,
    mod_razona_cuantitat_punt NUMERIC,
    mod_comuni_escrita_punt NUMERIC,
    mod_lectura_critica_punt NUMERIC,
    mod_ingles_punt NUMERIC,
    mod_competen_ciudada_punt NUMERIC,
    fami_estratovivienda TEXT
);

-- Sample analysis queries
-- Average scores by department
SELECT 
    estu_inst_departamento,
    ROUND(AVG(mod_razona_cuantitat_punt), 2) as avg_math,
    ROUND(AVG(mod_lectura_critica_punt), 2) as avg_reading,
    ROUND(AVG(mod_ingles_punt), 2) as avg_english,
    COUNT(*) as student_count
FROM saber_pro
GROUP BY estu_inst_departamento
ORDER BY avg_math DESC;

-- Performance by gender and socioeconomic status
SELECT 
    estu_genero,
    fami_estratovivienda,
    ROUND(AVG(mod_razona_cuantitat_punt), 2) as avg_math,
    ROUND(AVG(mod_lectura_critica_punt), 2) as avg_reading,
    COUNT(*) as student_count
FROM saber_pro
GROUP BY estu_genero, fami_estratovivienda
ORDER BY fami_estratovivienda, estu_genero;

-- Data quality check query
WITH data_quality AS (
    SELECT 
        COUNT(*) as total_rows,
        SUM(CASE WHEN mod_razona_cuantitat_punt > 0 AND mod_razona_cuantitat_punt < 300 THEN 1 ELSE 0 END) as valid_scores,
        SUM(CASE WHEN fami_estratovivienda LIKE 'Estrato %' THEN 1 ELSE 0 END) as valid_estrato,
        SUM(CASE WHEN inst_origen IS NOT NULL THEN 1 ELSE 0 END) as valid_institution,
        SUM(CASE WHEN fami_tieneinternet IN ('Si', 'No') THEN 1 ELSE 0 END) as valid_internet,
        SUM(CASE WHEN fami_tienecomputador IN ('Si', 'No') THEN 1 ELSE 0 END) as valid_computer,
        SUM(CASE WHEN estu_pagomatriculapropio IN ('Si', 'No') THEN 1 ELSE 0 END) as valid_self_paid,
        SUM(CASE WHEN estu_pagomatriculapadres IN ('Si', 'No') THEN 1 ELSE 0 END) as valid_parent_paid
    FROM saber_pro
);

-- Regression data query
WITH clean_scores AS (
    SELECT *
    FROM saber_pro
    WHERE mod_razona_cuantitat_punt > 0 AND mod_razona_cuantitat_punt < 300
    AND mod_lectura_critica_punt > 0 AND mod_lectura_critica_punt < 300
    AND mod_ingles_punt > 0 AND mod_ingles_punt < 300
    AND mod_competen_ciudada_punt > 0 AND mod_competen_ciudada_punt < 300
),
parent_education AS (
    SELECT 
        estu_consecutivo,
        CASE 
            WHEN fami_educacionpadre IN ('Ninguno', 'No sabe', 'No Aplica', 'Primaria incompleta', 'Primaria completa') 
                THEN 1
            WHEN fami_educacionpadre IN ('Secundaria (Bachillerato) incompleta', 'Secundaria (Bachillerato) completa')
                THEN 2
            WHEN fami_educacionpadre IN ('Técnica o tecnológica incompleta', 'Técnica o tecnológica completa')
                THEN 3
            WHEN fami_educacionpadre IN ('Educación profesional incompleta', 'Educación profesional completa', 'Postgrado')
                THEN 4
            ELSE NULL
        END as father_education,
        CASE 
            WHEN fami_educacionmadre IN ('Ninguno', 'No sabe', 'No Aplica', 'Primaria incompleta', 'Primaria completa') 
                THEN 1
            WHEN fami_educacionmadre IN ('Secundaria (Bachillerato) incompleta', 'Secundaria (Bachillerato) completa')
                THEN 2
            WHEN fami_educacionmadre IN ('Técnica o tecnológica incompleta', 'Técnica o tecnológica completa')
                THEN 3
            WHEN fami_educacionmadre IN ('Educación profesional incompleta', 'Educación profesional completa', 'Postgrado')
                THEN 4
            ELSE NULL
        END as mother_education
    FROM clean_scores
)
SELECT 
    (s.mod_razona_cuantitat_punt + s.mod_lectura_critica_punt + 
     s.mod_ingles_punt + s.mod_competen_ciudada_punt)/4.0 as avg_score,
    CAST(REPLACE(s.fami_estratovivienda, 'Estrato ', '') AS INTEGER) as estrato,
    CASE 
        WHEN s.inst_origen LIKE 'OFICIAL%' OR s.inst_origen = 'REGIMEN ESPECIAL' THEN 1
        WHEN s.inst_origen LIKE 'NO OFICIAL%' THEN 0
    END as is_public,
    CASE WHEN s.estu_genero = 'M' THEN 1 ELSE 0 END as is_male,
    CASE WHEN s.fami_tieneinternet = 'Si' THEN 1 ELSE 0 END as has_internet,
    CASE WHEN s.fami_tienecomputador = 'Si' THEN 1 ELSE 0 END as has_computer,
    CASE WHEN s.estu_pagomatriculapropio = 'Si' THEN 1 ELSE 0 END as self_paid,
    CASE WHEN s.estu_pagomatriculapadres = 'Si' THEN 1 ELSE 0 END as parent_paid,
    pe.father_education,
    pe.mother_education
FROM clean_scores s
LEFT JOIN parent_education pe ON s.estu_consecutivo = pe.estu_consecutivo
WHERE s.fami_estratovivienda LIKE 'Estrato %'
    AND s.estu_genero IN ('M', 'F')
    AND s.fami_tieneinternet IN ('Si', 'No')
    AND s.fami_tienecomputador IN ('Si', 'No')
    AND s.estu_pagomatriculapropio IN ('Si', 'No')
    AND s.estu_pagomatriculapadres IN ('Si', 'No')
    AND pe.father_education IS NOT NULL
    AND pe.mother_education IS NOT NULL; 