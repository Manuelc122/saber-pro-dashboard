# Saber Pro Dashboard

Dashboard interactivo para el análisis de resultados de las pruebas Saber Pro 2018-2022.

## Descripción

Este dashboard proporciona visualizaciones y análisis detallados de los resultados de las pruebas Saber Pro, incluyendo:
- Análisis demográfico
- Educación de los padres
- Costos educativos
- Características del hogar
- Características del estudiante

## Requisitos

- Python 3.11
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución Local

```bash
python src/dashboard/app.py
```

## Deployment

El dashboard está configurado para ser desplegado en Render.com utilizando Gunicorn como servidor WSGI. 