from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os
import sqlite3
from functools import lru_cache
import gc
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from pathlib import Path

# Constants for optimization
CHUNK_SIZE = 5000  # Reduced from 10000 for better memory management
QUERY_TIMEOUT = 30  # seconds
MAX_ROWS = 100000  # Maximum number of rows to return
CACHE_SIZE = 32

def get_db_path():
    if os.environ.get('RENDER'):
        return Path('/opt/render/project/src/data/processed/saber_pro.db')
    
    # For local development, construct path relative to the project root
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    return project_root / 'data' / 'processed' / 'saber_pro.db'

class DatabaseConnection:
    def __init__(self):
        self.db_path = get_db_path()
        if not self.db_path.exists():
            print(f"Database not found at: {self.db_path}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Absolute path to database: {self.db_path.absolute()}")
            raise FileNotFoundError(f"Database file not found at {self.db_path}")
        
    def __enter__(self):
        self.conn = sqlite3.connect(str(self.db_path), timeout=QUERY_TIMEOUT)
        self._optimize_connection()
        return self.conn
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        gc.collect()
        
    def _optimize_connection(self):
        self.conn.execute('PRAGMA cache_size = -2000')  # 2MB cache
        self.conn.execute('PRAGMA temp_store = MEMORY')
        self.conn.execute('PRAGMA journal_mode = WAL')
        self.conn.execute('PRAGMA synchronous = NORMAL')
        self.conn.execute('PRAGMA mmap_size = 30000000000')  # 30GB memory map
        self.conn.row_factory = sqlite3.Row

def read_query_in_chunks(query, conn, params=None):
    total_rows = 0
    start_time = time.time()
    
    try:
        for chunk in pd.read_sql_query(query, conn, params=params, chunksize=CHUNK_SIZE):
            total_rows += len(chunk)
            if total_rows > MAX_ROWS:
                print(f"Query exceeded maximum row limit of {MAX_ROWS}")
                break
            if time.time() - start_time > QUERY_TIMEOUT:
                print(f"Query timeout after {QUERY_TIMEOUT} seconds")
                break
            yield chunk
            gc.collect()  # Clean up after each chunk
    except Exception as e:
        print(f"Error during chunked reading: {str(e)}")
        yield pd.DataFrame()

@lru_cache(maxsize=CACHE_SIZE)
def cached_query(query_str, params_str=None):
    try:
        with DatabaseConnection() as conn:
            chunks = []
            total_size = 0
            
            for chunk in read_query_in_chunks(query_str, conn, params_str):
                chunks.append(chunk)
                total_size += chunk.memory_usage(deep=True).sum()
                
                # Break if memory usage exceeds 500MB
                if total_size > 500 * 1024 * 1024:  # 500MB in bytes
                    print("Query result exceeded memory limit")
                    break
            
            result = pd.concat(chunks) if chunks else pd.DataFrame()
            print(f"Query successful. Returned {len(result)} rows. Memory usage: {total_size/1024/1024:.2f}MB")
            return result
            
    except Exception as e:
        print(f"Database error: {str(e)}")
        return pd.DataFrame()

def query_db(query, params=None):
    """
    Execute a database query with optimizations for memory and performance.
    
    Args:
        query (str): SQL query to execute
        params (dict, optional): Query parameters
        
    Returns:
        pd.DataFrame: Query results
    """
    # Convert params to string for caching
    params_str = str(params) if params else None
    
    try:
        return cached_query(query, params_str)
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        print(f"Query: {query}")
        if params:
            print(f"Parameters: {params}")
        return pd.DataFrame()

# Add after imports, before app initialization
# Style Constants
COLORS = {
    'primary': '#1976D2',      # Updated to match the brighter blue
    'secondary': '#34495e',    # Lighter blue for subtitles
    'accent1': '#2E86C1',      # Blue for primary data series
    'accent2': '#E91E63',      # Pink for secondary data series
    'accent3': '#4CAF50',      # Green for tertiary data series
    'background': '#f8f9fa',   # Light gray for backgrounds
    'grid': 'rgba(189, 195, 199, 0.2)',  # Light gray for grids
    'text': '#2c3e50',         # Dark blue for text
    'white': '#ffffff'         # White
}

INSTITUTION_COLORS = {
    'OFICIAL': COLORS['accent1'],
    'NO OFICIAL': COLORS['accent2'],
    'REGIMEN ESPECIAL': COLORS['accent3']
}

GENDER_COLORS = {
    'M': COLORS['accent1'],
    'F': COLORS['accent2']
}

FONTS = {
    'primary': 'Roboto, sans-serif'
}

STYLES = {
    'title': {
        'textAlign': 'center',
        'color': COLORS['primary'],
        'marginBottom': '20px',
        'fontSize': '22px',
        'fontFamily': FONTS['primary'],
        'fontWeight': 'bold'
    },
    'subtitle': {
        'textAlign': 'center',
        'color': COLORS['secondary'],
        'marginBottom': '15px',
        'fontSize': '18px',
        'fontFamily': FONTS['primary']
    },
    'card': {
        'backgroundColor': COLORS['white'],
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'padding': '20px',
        'marginBottom': '20px'
    },
    'table_header': {
        'backgroundColor': COLORS['primary'],
        'color': COLORS['white'],
        'padding': '12px',
        'fontFamily': FONTS['primary'],
        'fontWeight': 'bold'
    },
    'table_cell': {
        'padding': '10px',
        'backgroundColor': COLORS['white'],
        'borderBottom': '1px solid #e0e0e0',
        'fontFamily': FONTS['primary']
    },
    'graph': {
        'height': 700,
        'font_family': FONTS['primary'],
        'title_size': 22,
        'axis_title_size': 14,
        'margin': dict(l=60, r=60, t=100, b=150)
    }
}

# Initialize the Dash app
app = Dash(__name__, 
    external_stylesheets=[
        'https://codepen.io/chriddyp/pen/bWLwgP.css',
        'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap'
    ],
    serve_locally=False  # Change this to False to fix the CSS warning
)

# Add this near the top after app initialization
server = app.server  # This is needed for production deployment

# Add port configuration
port = int(os.environ.get('PORT', 8051))
host = '0.0.0.0'

# Add memory configuration for production
if os.environ.get('RENDER'):
    # Reduce memory usage in production
    gc.collect()  # Force garbage collection
    
    # Configure SQLite to use less memory
    def optimize_sqlite_connection(conn):
        conn.execute('PRAGMA cache_size = -2000')  # Set cache size to 2MB
        conn.execute('PRAGMA temp_store = 2')  # Store temp tables in memory
        conn.execute('PRAGMA journal_mode = WAL')  # Use Write-Ahead Logging
        
    # Modify query_db function to use optimized connection
    def query_db(query, params=None):
        try:
            if os.environ.get('RENDER'):
                db_path = Path('/opt/render/project/src/data/processed/saber_pro.db')
            else:
                db_path = Path(__file__).parent.parent / 'data' / 'processed' / 'saber_pro.db'
            
            if not db_path.exists():
                print(f"Database not found at: {db_path}")
                return pd.DataFrame()
                
            conn = sqlite3.connect(db_path)
            optimize_sqlite_connection(conn)  # Apply optimization
            
            try:
                if params:
                    result = pd.read_sql_query(query, conn, params=params)
                else:
                    result = pd.read_sql_query(query, conn)
                    
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
                gc.collect()  # Force garbage collection after query
                
        except Exception as e:
            print(f"Database error: {str(e)}")
            print(f"Using database path: {db_path}")
            return pd.DataFrame()

# Updated database path configuration
if os.environ.get('RENDER'):
    # Production path on Render
    _db_path = Path('/opt/render/project/src/data/processed/saber_pro.db')
else:
    # Development path
    _db_path = Path(__file__).parent.parent / 'data' / 'processed' / 'saber_pro.db'

_db_warning = None if _db_path.exists() else html.Div(
    f"Base de datos no encontrada en {_db_path}. Por favor, ejecute create_database.py primero para crear y poblar la base de datos.",
    style={
        'color': 'white',
        'backgroundColor': '#f44336',
        'padding': '10px',
        'textAlign': 'center',
        'fontFamily': 'Roboto, sans-serif',
        'marginBottom': '20px'
    }
)

# Custom CSS for better styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Análisis de Resultados Saber Pro</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                margin: 0;
                background-color: #f0f2f5;
            }
            .main-title {
                text-align: center;
                padding: 30px 0;
                background-color: #1976D2;
                margin-bottom: 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .main-title h1 {
                color: white;
                font-size: 36px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin: 0;
                font-family: 'Roboto', sans-serif';
            }
            .header-title {
                text-align: center;
                color: #2c3e50;
                padding: 40px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .header-title h1 {
                font-size: 36px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin: 0;
                font-family: 'Roboto', sans-serif';
                color: #1976D2;
            }
            .header-subtitle {
                color: #666;
                font-size: 20px;
                margin-top: 15px;
                font-weight: 400;
            }
            .card {
                background-color: white;
                padding: 20px;
                margin: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="main-title">
            <h1>Análisis de Desempeño - Pruebas Saber Pro</h1>
            <div style="color: white; font-size: 24px; margin-top: 10px;">Cobertura Nacional 2018-2022</div>
        </div>
        <div class="header-title">
            <div class="header-subtitle" style="display: flex; flex-direction: column; gap: 10px;">
                <div>Resultados anonimizados de las pruebas Saber Pro desde el año 2018 al año 2022</div>
                <div style="font-size: 16px; color: #666;">
                    <strong>Fuente:</strong> Instituto Colombiano para la Evaluación de la Educación (ICFES)
                </div>
                <div style="font-size: 14px; color: #888;">
                    Datos Abiertos Colombia | Cobertura: Nacional | Última actualización: 23 de agosto de 2023
                </div>
            </div>
        </div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Add these style dictionaries at the top of the file after the imports
SECTION_TITLE_STYLE = {
    'textAlign': 'center',
    'color': '#2c3e50',
    'marginBottom': '30px',
    'fontFamily': 'Roboto, sans-serif',
    'fontSize': '28px',
    'fontWeight': 'bold',
    'textTransform': 'uppercase',
    'letterSpacing': '1px',
    'padding': '20px 0'
}

TABLE_TITLE_STYLE = {
    'color': '#2c3e50',
    'marginBottom': '20px',
    'textAlign': 'center',
    'fontFamily': 'Roboto, sans-serif',
    'fontSize': '22px',
    'fontWeight': 'bold',
    'padding': '10px 0'
}

GRAPH_TITLE_STYLE = {
    'text': None,  # Will be set for each graph
    'y': 0.95,
    'x': 0.5,
    'xanchor': 'center',
    'yanchor': 'top',
    'font': {
        'family': 'Roboto, sans-serif',
        'size': 22,
        'color': '#2c3e50'
    }
}

# Add after style definitions and before callbacks
def create_base_graph_layout(title, xaxis_title, yaxis_title, df, show_legend=False):
    """Create a base layout for graphs with consistent styling"""
    return dict(
        title=dict(
            text=title,
            font=dict(
                size=STYLES['graph']['title_size'],
                color=COLORS['primary'],
                family=STYLES['graph']['font_family']
            ),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(
                text=xaxis_title,
                font=dict(
                    size=STYLES['graph']['axis_title_size'],
                    color=COLORS['primary'],
                    family=STYLES['graph']['font_family']
                )
            ),
            showgrid=True,
            gridcolor=COLORS['grid'],
            showline=True,
            linewidth=2,
            linecolor=COLORS['primary'],
            tickangle=45
        ),
        yaxis=dict(
            title=dict(
                text=yaxis_title,
                font=dict(
                    size=STYLES['graph']['axis_title_size'],
                    color=COLORS['primary'],
                    family=STYLES['graph']['font_family']
                )
            ),
            showgrid=True,
            gridcolor=COLORS['grid'],
            showline=True,
            linewidth=2,
            linecolor=COLORS['primary'],
            range=[min(df['score']) - 2, max(df['score']) + 2] if 'score' in df.columns else None
        ),
        plot_bgcolor=COLORS['white'],
        paper_bgcolor=COLORS['white'],
        showlegend=show_legend,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor=COLORS['primary'],
            borderwidth=1
        ),
        margin=dict(l=60, r=60, t=100, b=150),  # Increased bottom margin for source annotation
        height=STYLES['graph']['height'],
        annotations=[
            dict(
                text='Fuente: Base de Datos Saber Pro',
                xref='paper',
                yref='paper',
                x=1,
                y=-0.4,
                showarrow=False,
                font=dict(
                    size=12,
                    color=COLORS['secondary'],
                    family=STYLES['graph']['font_family']
                ),
                align='right'
            )
        ],
        hovermode='x unified'
    )

# Updated dashboard layout with dataset overview tab
app.layout = html.Div([
    html.H1("Análisis Saber Pro", style=STYLES['title']),
    _db_warning,
    dcc.Tabs([
        dcc.Tab(label="Análisis Descriptivo", children=[
            html.Div([
                # Dataset Overview Section
                html.Div([
                    html.H4("Análisis de Resultados Saber Pro", style=SECTION_TITLE_STYLE),
                    html.Div([
                        html.Div([
                            html.H5("Descripción General", style={
                                'color': 'white',
                                'backgroundColor': '#1976D2',
                                'padding': '12px',
                                'marginBottom': '15px',
                                'borderRadius': '8px 8px 0 0',
                                'fontWeight': 'bold'
                            }),
                            html.P([
                                "El Saber Pro es el examen de Estado de la calidad de la educación superior en Colombia, ",
                                "una prueba estandarizada que evalúa las competencias de los estudiantes que están próximos ",
                                "a graduarse de programas de pregrado."
                            ], style={
                                'textAlign': 'justify',
                                'marginBottom': '15px',
                                'padding': '0 15px',
                                'color': '#2c3e50',
                                'lineHeight': '1.6'
                            }),
                        ], style={
                            'backgroundColor': 'white',
                            'borderRadius': '8px',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                            'marginBottom': '20px'
                        }),
                        
                        html.Div([
                            html.H5("Contenido del Dataset", style={
                                'color': 'white',
                                'backgroundColor': '#1976D2',
                                'padding': '12px',
                                'marginBottom': '15px',
                                'borderRadius': '8px 8px 0 0',
                                'fontWeight': 'bold'
                            }),
                            html.P([
                                "Este dashboard analiza datos del período 2018-2022, incluyendo:"
                            ], style={
                                'padding': '0 15px',
                                'marginBottom': '10px',
                                'color': '#2c3e50'
                            }),
                            html.Ul([
                                html.Li("Resultados en módulos genéricos (Razonamiento Cuantitativo, Lectura Crítica, Inglés y Competencias Ciudadanas)"),
                                html.Li("Información socioeconómica detallada de los estudiantes"),
                                html.Li("Características de las instituciones educativas"),
                                html.Li("Datos demográficos y contextuales")
                            ], style={
                                'paddingRight': '15px',
                                'paddingLeft': '35px',
                                'marginBottom': '15px',
                                'color': '#2c3e50',
                                'lineHeight': '1.6'
                            })
                        ], style={
                            'backgroundColor': 'white',
                            'borderRadius': '8px',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                            'marginBottom': '20px'
                        }),
                        
                        html.Div([
                            html.H5("Estructura del Dashboard", style={
                                'color': 'white',
                                'backgroundColor': '#1976D2',
                                'padding': '12px',
                                'marginBottom': '15px',
                                'borderRadius': '8px 8px 0 0',
                                'fontWeight': 'bold'
                            }),
                            html.P([
                                "El dashboard está organizado en las siguientes secciones:"
                            ], style={
                                'padding': '0 15px',
                                'marginBottom': '10px',
                                'color': '#2c3e50'
                            }),
                            html.Ul([
                                html.Li("Resumen Demográfico: Estadísticas generales y distribución por estrato socioeconómico"),
                                html.Li("Antecedentes Educativos: Nivel educativo de los padres y costos de matrícula"),
                                html.Li("Características del Hogar: Análisis de recursos y activos familiares"),
                                html.Li("Características del Estudiante: Información sobre horas de trabajo y otros factores"),
                                html.Li("Métodos de Pago: Análisis de las formas de financiación educativa")
                            ], style={
                                'paddingRight': '15px',
                                'paddingLeft': '35px',
                                'marginBottom': '15px',
                                'color': '#2c3e50',
                                'lineHeight': '1.6'
                            })
                        ], style={
                            'backgroundColor': 'white',
                            'borderRadius': '8px',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                            'marginBottom': '20px'
                        }),
                        
                        html.Div([
                            html.H5("Objetivo del Análisis", style={
                                'color': 'white',
                                'backgroundColor': '#1976D2',
                                'padding': '12px',
                                'marginBottom': '15px',
                                'borderRadius': '8px 8px 0 0',
                                'fontWeight': 'bold'
                            }),
                            html.P([
                                "Este análisis busca proporcionar insights sobre los factores que influyen en el desempeño académico, ",
                                "las características socioeconómicas de los estudiantes y las tendencias en la educación superior colombiana. ",
                                "Los datos presentados permiten identificar patrones, desigualdades y áreas de oportunidad en el sistema educativo."
                            ], style={
                                'textAlign': 'justify',
                                'marginBottom': '15px',
                                'padding': '0 15px',
                                'color': '#2c3e50',
                                'lineHeight': '1.6'
                            })
                        ], style={
                            'backgroundColor': 'white',
                            'borderRadius': '8px',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                            'marginBottom': '20px'
                        })
                    ], style={
                        'backgroundColor': '#f8f9fa',
                        'padding': '20px',
                        'borderRadius': '10px'
                    })
                ], className='card'),

                # Main Demographics Summary
                html.Div([
                    html.H4("Resumen Demográfico", style=SECTION_TITLE_STYLE),
                    html.Div(id='demographic-summary')
                ], className='card'),

                # Educational Background
                html.Div([
                    html.H4("Educación de los Padres", style=SECTION_TITLE_STYLE),
                    html.Div(id='parents-education-summary')
                ], className='card'),

                # Educational Costs
                html.Div([
                    html.H4("Costos Educativos", style=SECTION_TITLE_STYLE),
                    html.Div(id='education-costs-summary')
                ], className='card'),

                # Household Assets
                html.Div([
                    html.H4("Características del Hogar", style=SECTION_TITLE_STYLE),
                    html.Div(id='household-assets-summary')
                ], className='card'),

                # Student Characteristics
                html.Div([
                    html.H4("Características del Estudiante", style=SECTION_TITLE_STYLE),
                    html.Div(id='student-characteristics-summary')
                ], className='card')
            ])
        ]),
        dcc.Tab(label="Análisis de Relaciones", children=[
            html.Div([
                # Time Performance Section
                html.Div([
                    html.H4("Desempeño a lo Largo del Tiempo", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
                    html.Div([
                        html.Label("Seleccionar Módulo:", style={'marginRight': '10px', 'color': '#2c3e50'}),
                        dcc.Dropdown(
                            id='performance-metric',
                            options=[
                                {'label': 'Promedio General', 'value': 'avg_score'},
                                {'label': 'Razonamiento Cuantitativo', 'value': 'math_score'},
                                {'label': 'Lectura Crítica', 'value': 'reading_score'},
                                {'label': 'Inglés', 'value': 'english_score'},
                                {'label': 'Competencias Ciudadanas', 'value': 'citizenship_score'}
                            ],
                            value='avg_score',
                            style={'width': '300px'},
                            clearable=False
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginBottom': '20px'}),
                    dcc.Graph(id='performance-graph'),
                ], className='card'),
                
                # Socioeconomic Analysis Section
                html.Div([
                    html.H4("Desempeño por Estrato Socioeconómico y Género", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
                    html.Div([
                        html.Label("Seleccionar Módulo:", style={'marginRight': '10px', 'color': '#2c3e50'}),
                        dcc.Dropdown(
                            id='strata-performance-metric',
                            options=[
                                {'label': 'Promedio General', 'value': 'avg_score'},
                                {'label': 'Razonamiento Cuantitativo', 'value': 'math_score'},
                                {'label': 'Lectura Crítica', 'value': 'reading_score'},
                                {'label': 'Inglés', 'value': 'english_score'},
                                {'label': 'Competencias Ciudadanas', 'value': 'citizenship_score'}
                            ],
                            value='avg_score',
                            style={'width': '300px'},
                            clearable=False
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginBottom': '20px'}),
                    dcc.Graph(id='strata-performance-graph'),
                ], className='card'),
                
                # Parents Education Analysis Section
                html.Div([
                    html.H4("Desempeño por Nivel Educativo de los Padres", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
                    html.Div([
                        html.Label("Seleccionar Módulo:", style={'marginRight': '10px', 'color': '#2c3e50'}),
                        dcc.Dropdown(
                            id='parents-education-metric',
                            options=[
                                {'label': 'Promedio General', 'value': 'avg_score'},
                                {'label': 'Razonamiento Cuantitativo', 'value': 'math_score'},
                                {'label': 'Lectura Crítica', 'value': 'reading_score'},
                                {'label': 'Inglés', 'value': 'english_score'},
                                {'label': 'Competencias Ciudadanas', 'value': 'citizenship_score'}
                            ],
                            value='avg_score',
                            style={'width': '300px'},
                            clearable=False
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginBottom': '20px'}),
                    dcc.Graph(id='mother-education-graph', style={'marginBottom': '20px'}),
                    dcc.Graph(id='father-education-graph'),
                ], className='card'),

                # Tuition Costs Analysis Section
                html.Div([
                    html.H4("Relación entre Costos de Matrícula y Desempeño", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
                    html.Div([
                        html.Label("Seleccionar Módulo:", style={'marginRight': '10px', 'color': '#2c3e50'}),
                        dcc.Dropdown(
                            id='tuition-performance-metric',
                            options=[
                                {'label': 'Promedio General', 'value': 'avg_score'},
                                {'label': 'Razonamiento Cuantitativo', 'value': 'math_score'},
                                {'label': 'Lectura Crítica', 'value': 'reading_score'},
                                {'label': 'Inglés', 'value': 'english_score'},
                                {'label': 'Competencias Ciudadanas', 'value': 'citizenship_score'}
                            ],
                            value='avg_score',
                            style={'width': '300px'},
                            clearable=False
                        ),
                        html.Label("Tipo de Institución:", style={'marginLeft': '20px', 'marginRight': '10px', 'color': '#2c3e50'}),
                        dcc.Dropdown(
                            id='institution-type',
                            options=[
                                {'label': 'Todas', 'value': 'all'},
                                {'label': 'Oficial', 'value': 'OFICIAL'},
                                {'label': 'No Oficial', 'value': 'NO OFICIAL'},
                                {'label': 'Régimen Especial', 'value': 'REGIMEN ESPECIAL'}
                            ],
                            value='all',
                            style={'width': '200px'},
                            clearable=False
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginBottom': '20px'}),
                    dcc.Graph(id='tuition-performance-graph'),
                ], className='card')
            ])
        ])
    ])
])

# Callback for Performance Over Time tab
@app.callback(
    Output('performance-graph', 'figure'),
    [Input('performance-metric', 'value')]
)
def update_performance_graph(metric):
    query = """
    WITH year_data AS (
        SELECT 
            CAST(SUBSTR(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(periodo, '.5', ''),
                            ',5', ''
                        ),
                        ',', ''
                    ),
                    ' ', ''
                ), 1, 4
            ) AS INTEGER) as year,
            mod_razona_cuantitat_punt,
            mod_lectura_critica_punt,
            mod_ingles_punt,
            mod_competen_ciudada_punt
        FROM saber_pro
        WHERE periodo IS NOT NULL
    )
    SELECT 
        year,
        ROUND(AVG(mod_razona_cuantitat_punt),2) as math_score,
        ROUND(AVG(mod_lectura_critica_punt),2) as reading_score,
        ROUND(AVG(mod_ingles_punt),2) as english_score,
        ROUND(AVG(mod_competen_ciudada_punt),2) as citizenship_score,
        ROUND(AVG((mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0),2) as avg_score
    FROM year_data
    WHERE year BETWEEN 2018 AND 2022
    GROUP BY year
    ORDER BY year ASC
    """
    df = query_db(query)
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos disponibles para el análisis temporal",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color='#2c3e50')
        )
        return fig

    # Spanish translations for metric names
    metric_translations = {
        'math_score': 'Razonamiento Cuantitativo',
        'reading_score': 'Lectura Crítica',
        'english_score': 'Inglés',
        'citizenship_score': 'Competencias Ciudadanas',
        'avg_score': 'Promedio General'
    }

    # Calculate total change
    start_value = df[metric].iloc[0]
    end_value = df[metric].iloc[-1]
    change = end_value - start_value
    change_pct = (change / start_value) * 100
    
    # Create figure
    fig = go.Figure()
    
    # Add main trace for performance graph
    fig.add_trace(
        go.Scatter(
            x=df['year'],
            y=df[metric],
            mode='lines+markers+text',
            name='Puntaje',
            text=[f'{score:.1f}' for score in df[metric]],
            textposition='top center',
            textfont=dict(size=14, color='#1976D2', family='Roboto, sans-serif'),
            line=dict(color='#1976D2', width=3),
            marker=dict(
                size=12,
                color='#1976D2',
                line=dict(color='white', width=2)
            ),
            hovertemplate="<b>Año: %{x}</b><br>" +
                         "Puntaje: %{y:.1f}<br>" +
                         "<extra></extra>"
        )
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'Relación entre Año y {metric_translations[metric]} (2018-2022)',
            font=dict(size=22, color='#2c3e50', family='Roboto, sans-serif'),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(
                text='Año',
                font=dict(size=14, color='#2c3e50', family='Roboto, sans-serif')
            ),
            showgrid=True,
            gridcolor='rgba(189, 195, 199, 0.4)',
            showline=True,
            linewidth=2,
            linecolor='#2c3e50',
            tickmode='array',
            tickvals=df['year'].unique(),
            ticktext=[str(year) for year in df['year'].unique()],
            tickfont=dict(family='Roboto, sans-serif', size=12)
        ),
        yaxis=dict(
            title=dict(
                text='Puntaje Promedio',
                font=dict(size=14, color='#2c3e50', family='Roboto, sans-serif')
            ),
            showgrid=True,
            gridcolor='rgba(189, 195, 199, 0.4)',
            showline=True,
            linewidth=2,
            linecolor='#2c3e50',
            range=[min(df[metric]) - 5, max(df[metric]) + 5],
            tickfont=dict(family='Roboto, sans-serif', size=12)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        margin=dict(l=60, r=60, t=100, b=60),
        annotations=[
            dict(
                text=f'Cambio Total: {change:+.1f} puntos ({change_pct:+.1f}%)',
                xref='paper',
                yref='paper',
                x=0.01,
                y=1.05,
                showarrow=False,
                font=dict(size=14, color='#2c3e50', family='Roboto, sans-serif'),
                align='left'
            ),
            dict(
                text='Fuente: Base de Datos Saber Pro',
                xref='paper',
                yref='paper',
                x=1,
                y=-0.15,
                showarrow=False,
                font=dict(size=12, color='#7f8c8d', family='Roboto, sans-serif'),
                align='right'
            )
        ],
        hovermode='x unified'
    )
    
    # Add a subtle grid pattern
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(189, 195, 199, 0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(189, 195, 199, 0.2)')
    
    return fig

# Add custom CSS
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

# Add callbacks for dataset overview
@app.callback(
    Output('demographic-summary', 'children'),
    Input('demographic-summary', 'id')
)
def update_demographic_summary(_):
    # Query for general demographics
    query = """
    SELECT 
        COUNT(*) as total_students,
        ROUND(AVG((mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0), 2) as avg_overall_score,
        SUM(CASE WHEN estu_genero = 'F' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as female_percentage,
        AVG(CASE WHEN fami_estratovivienda != 'Sin estrato' THEN CAST(REPLACE(fami_estratovivienda, 'Estrato ', '') AS INTEGER) ELSE NULL END) as avg_estrato
    FROM saber_pro
    """
    overall_stats = query_db(query).iloc[0]
    
    # Query for estrato distribution
    estrato_query = """
    SELECT 
        fami_estratovivienda as estrato,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage
    FROM saber_pro
    WHERE fami_estratovivienda IS NOT NULL
    GROUP BY fami_estratovivienda
    ORDER BY 
        CASE 
            WHEN fami_estratovivienda = 'Sin estrato' THEN 7
            ELSE CAST(REPLACE(fami_estratovivienda, 'Estrato ', '') AS INTEGER)
        END
    """
    estrato_df = query_db(estrato_query)
    
    # Create the estrato distribution graph
    estrato_fig = go.Figure()
    
    # Add bars for student count with improved styling
    estrato_fig.add_trace(go.Bar(
        x=estrato_df['estrato'],
        y=estrato_df['count'],
        name='Cantidad de Estudiantes',
        text=[f'{count:,.0f}<br>({pct:.1f}%)' for count, pct in zip(estrato_df['count'], estrato_df['percentage'])],
        textposition='auto',
        hovertemplate="<b>%{x}</b><br>" +
                     "Estudiantes: %{y:,.0f}<br>" +
                     "Porcentaje: %{text}<br>" +
                     "<extra></extra>",
        marker_color='#1976D2'
    ))
    
    # Update layout with enhanced styling
    estrato_fig.update_layout(
        title={
            'text': 'Distribución de Estudiantes por Estrato',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'family': 'Roboto, sans-serif',
                'size': 22,
                'color': '#2c3e50'
            }
        },
        xaxis=dict(
            title=dict(
                text='Estrato Socioeconómico',
                font=dict(size=14, color='#2c3e50')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(189, 195, 199, 0.2)',
            showline=True,
            linewidth=2,
            linecolor='#2c3e50'
        ),
        yaxis=dict(
            title=dict(
                text='Cantidad de Estudiantes',
                font=dict(size=14, color='#2c3e50')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(189, 195, 199, 0.2)',
            showline=True,
            linewidth=2,
            linecolor='#2c3e50',
            tickformat=',d'
        ),
        showlegend=False,
        template='plotly_white',
        margin=dict(l=60, r=60, t=80, b=60),
        height=500,
        annotations=[
            dict(
                text='Fuente: Base de Datos Saber Pro',
                xref='paper',
                yref='paper',
                x=1,
                y=-0.15,
                showarrow=False,
                font=dict(size=10, color='#7f8c8d'),
                align='right'
            )
        ]
    )
    
    # Add a subtle grid pattern
    estrato_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(189, 195, 199, 0.2)')
    estrato_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(189, 195, 199, 0.2)')
    
    return html.Div([
        # General Statistics
        html.Div([
            html.H5("Estadísticas Generales", style=TABLE_TITLE_STYLE),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Indicador", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'left',
                            'fontWeight': 'bold',
                            'width': '70%'
                        }),
                        html.Th("Valor", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'right',
                            'fontWeight': 'bold',
                            'width': '30%'
                        })
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td("Total de Estudiantes", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{int(overall_stats['total_students']):,}", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        })
                    ]),
                    html.Tr([
                        html.Td("Puntaje Promedio General", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{overall_stats['avg_overall_score']:.1f}", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        })
                    ]),
                    html.Tr([
                        html.Td("Porcentaje de Mujeres", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{overall_stats['female_percentage']:.1f}%", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        })
                    ]),
                    html.Tr([
                        html.Td("Estrato Promedio", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{overall_stats['avg_estrato']:.1f}", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        })
                    ])
                ])
            ], style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'overflow': 'hidden',
                'marginBottom': '20px'
            })
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '20px',
            'borderRadius': '10px',
            'marginBottom': '20px'
        }),
        
        # Estrato Distribution
        html.Div([
            html.H5("Distribución por Estrato", style=TABLE_TITLE_STYLE),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Estrato", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'left',
                            'fontWeight': 'bold'
                        }),
                        html.Th("Cantidad", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'right',
                            'fontWeight': 'bold'
                        }),
                        html.Th("Porcentaje", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'right',
                            'fontWeight': 'bold'
                        })
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(row['estrato'], style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{int(row['count']):,}", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{row['percentage']:.1f}%", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        })
                    ]) for _, row in estrato_df.iterrows()
                ])
            ], style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'overflow': 'hidden',
                'marginBottom': '20px'
            }),
            
            # Add the specialized graph
            dcc.Graph(
                figure=estrato_fig,
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                },
                style={
                    'backgroundColor': 'white',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'padding': '15px'
                }
            )
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '20px',
            'borderRadius': '10px',
            'marginBottom': '20px'
        })
    ])

@app.callback(
    Output('parents-education-summary', 'children'),
    Input('parents-education-summary', 'id')
)
def update_parents_education_summary(_):
    # Query for parents' education
    query = """
    WITH education_order AS (
        SELECT education_level, 
        CASE education_level
            WHEN 'Postgrado' THEN 1
            WHEN 'Educación profesional completa' THEN 2
            WHEN 'Educación profesional incompleta' THEN 3
            WHEN 'Técnica o tecnológica completa' THEN 4
            WHEN 'Técnica o tecnológica incompleta' THEN 5
            WHEN 'Secundaria (Bachillerato) completa' THEN 6
            WHEN 'Secundaria (Bachillerato) incompleta' THEN 7
            WHEN 'Primaria completa' THEN 8
            WHEN 'Primaria incompleta' THEN 9
            WHEN 'Ninguno' THEN 10
            WHEN 'No Aplica' THEN 11
            WHEN 'No sabe' THEN 12
        END as order_num
        FROM (
            SELECT DISTINCT fami_educacionpadre as education_level FROM saber_pro WHERE fami_educacionpadre IS NOT NULL
            UNION
            SELECT DISTINCT fami_educacionmadre FROM saber_pro WHERE fami_educacionmadre IS NOT NULL
        )
    )
    SELECT 
        parent,
        education_level,
        count,
        percentage,
        order_num
    FROM (
        SELECT 
            'Padre' as parent,
            eo.education_level,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage,
            eo.order_num
        FROM saber_pro s
        JOIN education_order eo ON s.fami_educacionpadre = eo.education_level
        WHERE fami_educacionpadre IS NOT NULL
        GROUP BY eo.education_level, eo.order_num
        
        UNION ALL
        
        SELECT 
            'Madre' as parent,
            eo.education_level,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage,
            eo.order_num
        FROM saber_pro s
        JOIN education_order eo ON s.fami_educacionmadre = eo.education_level
        WHERE fami_educacionmadre IS NOT NULL
        GROUP BY eo.education_level, eo.order_num
    ) subquery
    ORDER BY order_num, parent
    """
    education_df = query_db(query)
    
    # Create the parents' education graph
    parents_fig = go.Figure()
    
    # Sort the data by order_num to ensure hierarchical display
    father_data = education_df[education_df['parent'] == 'Padre'].sort_values('order_num')
    mother_data = education_df[education_df['parent'] == 'Madre'].sort_values('order_num')
    
    # Add bars for father's education
    parents_fig.add_trace(go.Bar(
        name='Padre',
        x=father_data['education_level'],
        y=father_data['percentage'],
        text=[f"{pct:.1f}%" for pct in father_data['percentage']],
        textposition='auto',
        marker_color='#1976D2',
        hovertemplate="<b>%{x}</b><br>" +
                     "Porcentaje: %{text}<br>" +
                     "<extra></extra>"
    ))
    
    # Add bars for mother's education
    parents_fig.add_trace(go.Bar(
        name='Madre',
        x=mother_data['education_level'],
        y=mother_data['percentage'],
        text=[f"{pct:.1f}%" for pct in mother_data['percentage']],
        textposition='auto',
        marker_color='#9C27B0',  # Keep mother's education in purple for contrast
        hovertemplate="<b>%{x}</b><br>" +
                     "Porcentaje: %{text}<br>" +
                     "<extra></extra>"
    ))
    
    # Get the ordered categories
    ordered_categories = education_df.sort_values('order_num')['education_level'].unique()
    
    # Update layout with hierarchical ordering
    parents_fig.update_layout(
        title={
            'text': 'Distribución del Nivel Educativo de los Padres',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'family': 'Roboto, sans-serif',
                'size': 22,
                'color': '#2c3e50'
            }
        },
        xaxis=dict(
            title='Nivel Educativo',
            titlefont=dict(size=14, color='#2c3e50'),
            tickangle=45,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(189, 195, 199, 0.2)',
            categoryorder='array',
            categoryarray=ordered_categories
        ),
        yaxis=dict(
            title='Porcentaje',
            titlefont=dict(size=14, color='#2c3e50'),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(189, 195, 199, 0.2)',
            tickformat='.1f',
            ticksuffix='%',
            range=[0, max(education_df['percentage']) * 1.1]
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            title='',
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#2c3e50',
            borderwidth=1
        ),
        margin=dict(l=50, r=50, t=100, b=150),
        height=700
    )
    
    return html.Div([
        html.Table([
            html.Thead(
                html.Tr([
                    html.Th("Nivel Educativo", style={
                        'padding': '12px',
                        'backgroundColor': '#1976D2',
                        'color': 'white',
                        'textAlign': 'left',
                        'fontWeight': 'bold'
                    }),
                    html.Th("Padre", style={
                        'padding': '12px',
                        'backgroundColor': '#1976D2',
                        'color': 'white',
                        'textAlign': 'right',
                        'fontWeight': 'bold'
                    }),
                    html.Th("Madre", style={
                        'padding': '12px',
                        'backgroundColor': '#1976D2',
                        'color': 'white',
                        'textAlign': 'right',
                        'fontWeight': 'bold'
                    })
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(level, style={
                        'padding': '10px',
                        'backgroundColor': 'white',
                        'borderBottom': '1px solid #e0e0e0'
                    }),
                    html.Td(
                        f"{education_df[(education_df['parent'] == 'Padre') & (education_df['education_level'] == level)]['percentage'].iloc[0]:.1f}%"
                        if len(education_df[(education_df['parent'] == 'Padre') & (education_df['education_level'] == level)]) > 0
                        else "0.0%",
                        style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        }
                    ),
                    html.Td(
                        f"{education_df[(education_df['parent'] == 'Madre') & (education_df['education_level'] == level)]['percentage'].iloc[0]:.1f}%"
                        if len(education_df[(education_df['parent'] == 'Madre') & (education_df['education_level'] == level)]) > 0
                        else "0.0%",
                        style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        }
                    )
                ]) for level in sorted(education_df['education_level'].unique())
            ])
        ], style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'backgroundColor': 'white',
            'borderRadius': '8px',
            'overflow': 'hidden',
            'marginBottom': '20px'
        }),
        
        # Add the graph
        dcc.Graph(
            figure=parents_fig,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            },
            style={
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'padding': '15px'
            }
        )
    ], style={
        'backgroundColor': '#f8f9fa',
        'padding': '20px',
        'borderRadius': '10px',
        'marginBottom': '20px'
    })

@app.callback(
    Output('education-costs-summary', 'children'),
    Input('education-costs-summary', 'id')
)
def update_education_costs_summary(_):
    # Query for education costs distribution
    query = """
    SELECT 
        estu_valormatriculauniversidad as tuition_range,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage,
        ROUND(AVG((mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0), 1) as avg_score,
        CASE estu_valormatriculauniversidad
            WHEN 'Menos de 500 mil' THEN 1
            WHEN 'Entre 500 mil y menos de 1 millón' THEN 2
            WHEN 'Entre 1 millón y menos de 2.5 millones' THEN 3
            WHEN 'Entre 2.5 millones y menos de 4 millones' THEN 4
            WHEN 'Entre 4 millones y menos de 5.5 millones' THEN 5
            WHEN 'Entre 5.5 millones y menos de 7 millones' THEN 6
            WHEN 'Más de 7 millones' THEN 7
            ELSE 8
        END as order_num
    FROM saber_pro
    WHERE estu_valormatriculauniversidad IS NOT NULL
    GROUP BY estu_valormatriculauniversidad
    ORDER BY order_num
    """
    
    costs_df = query_db(query)
    
    if costs_df.empty:
        return html.Div("No hay datos disponibles para el análisis de costos de matrícula")
    
    # Create bar chart
    costs_fig = go.Figure()
    
    costs_fig.add_trace(go.Bar(
        x=costs_df['tuition_range'],
        y=costs_df['percentage'],
        text=[f"{p}%" for p in costs_df['percentage']],
        textposition='auto',
        marker_color=COLORS['primary'],  # Updated to use primary color
        hovertemplate="<b>%{x}</b><br>" +
                     "Porcentaje: %{text}<br>" +
                     "Estudiantes: %{customdata:,.0f}<br>" +
                     "Puntaje promedio: %{customdata2:.1f}<br>" +
                     "<extra></extra>",
        customdata=costs_df[['count', 'avg_score']].values
    ))
    
    # Update layout using the standardized styles
    costs_fig.update_layout(
        title=dict(
            text='Distribución de Costos de Matrícula',
            font=dict(
                size=STYLES['graph']['title_size'],
                color='#2c3e50',  # Updated to match other titles
                family=FONTS['primary']
            ),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(
                text='Rango de Costos',
                font=dict(
                    size=STYLES['graph']['axis_title_size'],
                    color='#2c3e50',  # Updated to match other axis titles
                    family=FONTS['primary']
                )
            ),
            tickangle=45,
            showgrid=True,
            gridcolor=COLORS['grid'],
            showline=True,
            linewidth=2,
            linecolor=COLORS['primary']
        ),
        yaxis=dict(
            title=dict(
                text='Porcentaje de Estudiantes',
                font=dict(
                    size=STYLES['graph']['axis_title_size'],
                    color='#2c3e50',  # Updated to match other axis titles
                    family=FONTS['primary']
                )
            ),
            ticksuffix='%',
            showgrid=True,
            gridcolor=COLORS['grid'],
            showline=True,
            linewidth=2,
            linecolor=COLORS['primary']
        ),
        plot_bgcolor=COLORS['white'],
        paper_bgcolor=COLORS['white'],
        showlegend=False,
        margin=STYLES['graph']['margin'],
        height=STYLES['graph']['height'],
        annotations=[
            dict(
                text='Fuente: Base de Datos Saber Pro',
                xref='paper',
                yref='paper',
                x=1,
                y=-0.4,
                showarrow=False,
                font=dict(
                    size=12,
                    color=COLORS['secondary'],
                    family=FONTS['primary']
                ),
                align='right'
            )
        ],
        hovermode='x unified'
    )
    
    # Create summary table with standardized styles
    return html.Div([
        # Table Section
        html.Div([
            html.Table([
                # Header
                html.Thead([
                    html.Tr([
                        html.Th('Rango de Costos', style={
                            **STYLES['table_header'],
                            'backgroundColor': COLORS['primary']  # Updated to use primary color
                        }),
                        html.Th('Estudiantes', style={
                            **STYLES['table_header'],
                            'backgroundColor': COLORS['primary'],  # Updated to use primary color
                            'textAlign': 'right'
                        }),
                        html.Th('Porcentaje', style={
                            **STYLES['table_header'],
                            'backgroundColor': COLORS['primary'],  # Updated to use primary color
                            'textAlign': 'right'
                        }),
                        html.Th('Puntaje Promedio', style={
                            **STYLES['table_header'],
                            'backgroundColor': COLORS['primary'],  # Updated to use primary color
                            'textAlign': 'right'
                        })
                    ])
                ]),
                # Body
                html.Tbody([
                    html.Tr([
                        html.Td(row['tuition_range'], style=STYLES['table_cell']),
                        html.Td(f"{int(row['count']):,}", style={**STYLES['table_cell'], 'textAlign': 'right'}),
                        html.Td(f"{row['percentage']:.1f}%", style={**STYLES['table_cell'], 'textAlign': 'right'}),
                        html.Td(f"{row['avg_score']:.1f}", style={**STYLES['table_cell'], 'textAlign': 'right'})
                    ]) for _, row in costs_df.iterrows()
                ])
            ], style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'backgroundColor': COLORS['white'],
                'borderRadius': '8px',
                'overflow': 'hidden',
                'marginBottom': '20px'
            })
        ]),
        
        # Graph Section
        dcc.Graph(
            figure=costs_fig,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            },
            style=STYLES['card']
        )
    ], style={
        'backgroundColor': COLORS['background'],
        'padding': '20px',
        'borderRadius': '10px',
        'marginBottom': '20px'
    })

# Add new callback for household assets
@app.callback(
    Output('household-assets-summary', 'children'),
    Input('household-assets-summary', 'id')
)
def update_household_assets_summary(_):
    # Query for household assets
    query = """
    WITH asset_counts AS (
        SELECT 
            'Internet' as asset,
            SUM(CASE WHEN FAMI_TIENEINTERNET = 'Si' THEN 1 ELSE 0 END) as has_asset,
            SUM(CASE WHEN FAMI_TIENEINTERNET = 'No' THEN 1 ELSE 0 END) as no_asset,
            COUNT(*) as total
        FROM saber_pro
        WHERE FAMI_TIENEINTERNET IS NOT NULL
        UNION ALL
        SELECT 
            'Computador' as asset,
            SUM(CASE WHEN FAMI_TIENECOMPUTADOR = 'Si' THEN 1 ELSE 0 END) as has_asset,
            SUM(CASE WHEN FAMI_TIENECOMPUTADOR = 'No' THEN 1 ELSE 0 END) as no_asset,
            COUNT(*) as total
        FROM saber_pro
        WHERE FAMI_TIENECOMPUTADOR IS NOT NULL
        UNION ALL
        SELECT 
            'Lavadora' as asset,
            SUM(CASE WHEN FAMI_TIENELAVADORA = 'Si' THEN 1 ELSE 0 END) as has_asset,
            SUM(CASE WHEN FAMI_TIENELAVADORA = 'No' THEN 1 ELSE 0 END) as no_asset,
            COUNT(*) as total
        FROM saber_pro
        WHERE FAMI_TIENELAVADORA IS NOT NULL
        UNION ALL
        SELECT 
            'Automóvil' as asset,
            SUM(CASE WHEN FAMI_TIENEAUTOMOVIL = 'Si' THEN 1 ELSE 0 END) as has_asset,
            SUM(CASE WHEN FAMI_TIENEAUTOMOVIL = 'No' THEN 1 ELSE 0 END) as no_asset,
            COUNT(*) as total
        FROM saber_pro
        WHERE FAMI_TIENEAUTOMOVIL IS NOT NULL
    )
    SELECT 
        asset as Recurso,
        has_asset as Tienen,
        no_asset as No_Tienen,
        ROUND(has_asset * 100.0 / total, 1) as percentage_tienen,
        ROUND(no_asset * 100.0 / total, 1) as percentage_no_tienen
    FROM asset_counts
    ORDER BY percentage_tienen DESC
    """
    
    assets_df = query_db(query)
    
    # Create the assets distribution graph
    assets_fig = go.Figure()
    
    # Add bars for those who have the assets
    assets_fig.add_trace(go.Bar(
        name='Tienen',
        x=assets_df['Recurso'],
        y=assets_df['Tienen'],
        text=[f"{count:,.0f}<br>({pct:.1f}%)" for count, pct in zip(assets_df['Tienen'], assets_df['percentage_tienen'])],
        textposition='auto',
        marker_color='#1976D2'
    ))
    
    # Add bars for those who don't have the assets
    assets_fig.add_trace(go.Bar(
        name='No Tienen',
        x=assets_df['Recurso'],
        y=assets_df['No_Tienen'],
        text=[f"{count:,.0f}<br>({pct:.1f}%)" for count, pct in zip(assets_df['No_Tienen'], assets_df['percentage_no_tienen'])],
        textposition='auto',
        marker_color='#E57373'  # Changed to a contrasting red color
    ))

    # Update layout
    assets_fig.update_layout(
        title={
            'text': 'Distribución de Recursos del Hogar',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'family': 'Roboto, sans-serif',
                'size': 22,
                'color': '#2c3e50'
            }
        },
        xaxis_title='Recurso',
        yaxis_title='Cantidad de Estudiantes',
        template='plotly_white',
        barmode='group',
        height=700,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.98,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#2c3e50',
            borderwidth=1
        ),
        hoverlabel={'bgcolor': 'white'},
        hovermode='x unified',
        margin=dict(t=80, r=20, l=20, b=20)  # Adjusted margins
    )

    return html.Div([
        html.Div([
            html.H5("Recursos del Hogar", style=TABLE_TITLE_STYLE),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Recurso", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'left',
                            'fontWeight': 'bold'
                        }),
                        html.Th("Tienen", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'right',
                            'fontWeight': 'bold'
                        }),
                        html.Th("No Tienen", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'right',
                            'fontWeight': 'bold'
                        }),
                        html.Th("% Tienen", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'right',
                            'fontWeight': 'bold'
                        })
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(row['Recurso'], style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{int(row['Tienen']):,}", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{int(row['No_Tienen']):,}", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{row['percentage_tienen']:.1f}%", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        })
                    ]) for _, row in assets_df.iterrows()
                ])
            ], style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'overflow': 'hidden',
                'marginBottom': '20px'
            }),
        ]),
        
        # Add the graph
        dcc.Graph(
            figure=assets_fig,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            },
            style={
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'padding': '15px'
            }
        )
    ], style={
        'backgroundColor': '#f8f9fa',
        'padding': '20px',
        'borderRadius': '10px',
        'marginBottom': '20px'
    })

@app.callback(
    Output('student-characteristics-summary', 'children'),
    Input('student-characteristics-summary', 'id')
)
def update_student_characteristics_summary(_):
    # Query for work hours
    work_query = """
    SELECT 
        ESTU_HORASSEMANATRABAJA as work_hours,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage,
        ROUND(AVG((mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0), 1) as avg_score
    FROM saber_pro
    WHERE ESTU_HORASSEMANATRABAJA IS NOT NULL
    GROUP BY ESTU_HORASSEMANATRABAJA
    ORDER BY 
        CASE ESTU_HORASSEMANATRABAJA
            WHEN '0' THEN 1
            WHEN 'No trabaja' THEN 1
            WHEN 'Menos de 10 horas' THEN 2
            WHEN 'Entre 11 y 20 horas' THEN 3
            WHEN 'Entre 21 y 30 horas' THEN 4
            WHEN 'Más de 30 horas' THEN 5
            ELSE 6
        END,
        CASE 
            WHEN ESTU_HORASSEMANATRABAJA = '0' THEN 1
            WHEN ESTU_HORASSEMANATRABAJA = 'No trabaja' THEN 2
            ELSE 3
        END
    """
    
    work_data = query_db(work_query)
    
    # Create work hours graph
    work_fig = go.Figure()
    
    # Add bars for work hours
    work_fig.add_trace(go.Bar(
        x=work_data['work_hours'],
        y=work_data['count'],
        text=[f"{count:,.0f}<br>({pct:.1f}%)" for count, pct in zip(work_data['count'], work_data['percentage'])],
        textposition='auto',
        marker_color='#1976D2',
        hovertemplate="<b>%{x}</b><br>" +
                     "Cantidad: %{y:,.0f}<br>" +
                     "Porcentaje: %{text}<br>" +
                     "Puntaje: %{customdata:.1f}<br>" +
                     "<extra></extra>",
        customdata=work_data['avg_score']
    ))

    # Update layout for work hours
    work_fig.update_layout(
        title={
            'text': 'Distribución de Horas de Trabajo Semanal',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'family': 'Roboto, sans-serif',
                'size': 22,
                'color': '#2c3e50'
            }
        },
        xaxis_title='Horas de Trabajo',
        yaxis_title='Cantidad de Estudiantes',
        template='plotly_white',
        showlegend=False,
        height=500
    )

    return html.Div([
        # Work Hours Table
        html.Div([
            html.H5("Horas de Trabajo Semanal", style=TABLE_TITLE_STYLE),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Horas", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'left',
                            'fontWeight': 'bold'
                        }),
                        html.Th("Cantidad", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'right',
                            'fontWeight': 'bold'
                        }),
                        html.Th("Porcentaje", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'right',
                            'fontWeight': 'bold'
                        }),
                        html.Th("Puntaje Promedio", style={
                            'padding': '12px',
                            'backgroundColor': '#1976D2',
                            'color': 'white',
                            'textAlign': 'right',
                            'fontWeight': 'bold'
                        })
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(row['work_hours'], style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{int(row['count']):,}", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{row['percentage']:.1f}%", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        }),
                        html.Td(f"{row['avg_score']:.1f}", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        })
                    ]) for _, row in work_data.iterrows()
                ])
            ], style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'overflow': 'hidden',
                'marginBottom': '20px'
            })
        ]),
        
        # Work Hours Graph
        dcc.Graph(
            figure=work_fig,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            },
            style={
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'padding': '15px'
            }
        )
    ], style={
        'backgroundColor': '#f8f9fa',
        'padding': '20px',
        'borderRadius': '10px',
        'marginBottom': '20px'
    })

# Add new callback for strata performance graph
@app.callback(
    Output('strata-performance-graph', 'figure'),
    [Input('strata-performance-metric', 'value')]
)
def update_strata_performance_graph(metric):
    # Define the metric mapping
    metric_mapping = {
        'avg_score': '(mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0',
        'math_score': 'mod_razona_cuantitat_punt',
        'reading_score': 'mod_lectura_critica_punt',
        'english_score': 'mod_ingles_punt',
        'citizenship_score': 'mod_competen_ciudada_punt'
    }
    
    # Query to get average scores by strata and gender
    query = f"""
    SELECT 
        fami_estratovivienda as estrato,
        estu_genero as genero,
        ROUND(AVG({metric_mapping[metric]}), 2) as score,
        COUNT(*) as count
    FROM saber_pro
    WHERE fami_estratovivienda != 'Sin estrato'
    GROUP BY fami_estratovivienda, estu_genero
    ORDER BY 
        CAST(REPLACE(fami_estratovivienda, 'Estrato ', '') AS INTEGER),
        estu_genero
    """
    
    df = query_db(query)
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos disponibles para el análisis por estrato y género",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color='#2c3e50')
        )
        return fig

    # Spanish translations for metric names
    metric_translations = {
        'math_score': 'Razonamiento Cuantitativo',
        'reading_score': 'Lectura Crítica',
        'english_score': 'Inglés',
        'citizenship_score': 'Competencias Ciudadanas',
        'avg_score': 'Promedio General'
    }

    # Create figure
    fig = go.Figure()
    
    # Add lines for each gender
    for gender, color, name in [('M', '#1976D2', 'Hombres'), ('F', '#E91E63', 'Mujeres')]:
        gender_data = df[df['genero'] == gender]
        
        fig.add_trace(go.Scatter(
            x=gender_data['estrato'],
            y=gender_data['score'],
            name=name,
            mode='lines+markers+text',
            text=[f'{score:.1f}' for score in gender_data['score']],
            textposition='top center',
            textfont=dict(size=12, color=color, family='Roboto, sans-serif'),
            line=dict(color=color, width=3),
            marker=dict(
                size=8,
                color=color,
                line=dict(color='white', width=2)
            ),
            hovertemplate="<b>%{x}</b><br>" +
                         f"{name}<br>" +
                         "Puntaje: %{y:.1f}<br>" +
                         "Estudiantes: %{customdata:,.0f}<br>" +
                         "<extra></extra>",
            customdata=gender_data['count']
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'Relación entre Estrato Socioeconómico, Género y {metric_translations[metric]}',
            font=dict(size=22, color='#2c3e50', family='Roboto, sans-serif'),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(
                text='Estrato Socioeconómico',
                font=dict(size=14, color='#2c3e50', family='Roboto, sans-serif')
            ),
            showgrid=True,
            gridcolor='rgba(189, 195, 199, 0.4)',
            showline=True,
            linewidth=2,
            linecolor='#2c3e50'
        ),
        yaxis=dict(
            title=dict(
                text='Puntaje Promedio',
                font=dict(size=14, color='#2c3e50', family='Roboto, sans-serif')
            ),
            showgrid=True,
            gridcolor='rgba(189, 195, 199, 0.4)',
            showline=True,
            linewidth=2,
            linecolor='#2c3e50',
            range=[min(df['score']) - 2, max(df['score']) + 2]
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,  # At the top
            xanchor="center",
            x=0.5,  # Centered horizontally
            orientation="h",  # Horizontal layout
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#2c3e50',
            borderwidth=1
        ),
        margin=dict(l=60, r=60, t=100, b=60),
        height=700,  # Increased height from default (450) to 700
        annotations=[
            dict(
                text='Fuente: Base de Datos Saber Pro',
                xref='paper',
                yref='paper',
                x=1,
                y=-0.15,
                showarrow=False,
                font=dict(size=12, color='#7f8c8d', family='Roboto, sans-serif'),
                align='right'
            )
        ],
        hovermode='x unified'
    )
    
    # Add a subtle grid pattern
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(189, 195, 199, 0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(189, 195, 199, 0.2)')
    
    return fig

# Add new callbacks for parents' education graphs
@app.callback(
    [Output('mother-education-graph', 'figure'),
     Output('father-education-graph', 'figure')],
    [Input('parents-education-metric', 'value')]
)
def update_parents_education_graphs(metric):
    # Define the metric mapping
    metric_mapping = {
        'avg_score': '(mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0',
        'math_score': 'mod_razona_cuantitat_punt',
        'reading_score': 'mod_lectura_critica_punt',
        'english_score': 'mod_ingles_punt',
        'citizenship_score': 'mod_competen_ciudada_punt'
    }
    
    # Education level order
    education_order = """
    CASE education_level
        WHEN 'Postgrado' THEN 1
        WHEN 'Educación profesional completa' THEN 2
        WHEN 'Educación profesional incompleta' THEN 3
        WHEN 'Técnica o tecnológica completa' THEN 4
        WHEN 'Técnica o tecnológica incompleta' THEN 5
        WHEN 'Secundaria (Bachillerato) completa' THEN 6
        WHEN 'Secundaria (Bachillerato) incompleta' THEN 7
        WHEN 'Primaria completa' THEN 8
        WHEN 'Primaria incompleta' THEN 9
        WHEN 'Ninguno' THEN 10
        ELSE 11
    END
    """
    
    # Query for mother's education
    mother_query = f"""
    SELECT 
        fami_educacionmadre as education_level,
        ROUND(AVG({metric_mapping[metric]}), 2) as score,
        COUNT(*) as count,
        CASE fami_educacionmadre
            WHEN 'Postgrado' THEN 1
            WHEN 'Educación profesional completa' THEN 2
            WHEN 'Educación profesional incompleta' THEN 3
            WHEN 'Técnica o tecnológica completa' THEN 4
            WHEN 'Técnica o tecnológica incompleta' THEN 5
            WHEN 'Secundaria (Bachillerato) completa' THEN 6
            WHEN 'Secundaria (Bachillerato) incompleta' THEN 7
            WHEN 'Primaria completa' THEN 8
            WHEN 'Primaria incompleta' THEN 9
            WHEN 'Ninguno' THEN 10
            ELSE 11
        END as order_num
    FROM saber_pro
    WHERE fami_educacionmadre NOT IN ('No sabe', 'No Aplica')
    GROUP BY fami_educacionmadre
    ORDER BY order_num
    """
    
    # Query for father's education
    father_query = f"""
    SELECT 
        fami_educacionpadre as education_level,
        ROUND(AVG({metric_mapping[metric]}), 2) as score,
        COUNT(*) as count,
        CASE fami_educacionpadre
            WHEN 'Postgrado' THEN 1
            WHEN 'Educación profesional completa' THEN 2
            WHEN 'Educación profesional incompleta' THEN 3
            WHEN 'Técnica o tecnológica completa' THEN 4
            WHEN 'Técnica o tecnológica incompleta' THEN 5
            WHEN 'Secundaria (Bachillerato) completa' THEN 6
            WHEN 'Secundaria (Bachillerato) incompleta' THEN 7
            WHEN 'Primaria completa' THEN 8
            WHEN 'Primaria incompleta' THEN 9
            WHEN 'Ninguno' THEN 10
            ELSE 11
        END as order_num
    FROM saber_pro
    WHERE fami_educacionpadre NOT IN ('No sabe', 'No Aplica')
    GROUP BY fami_educacionpadre
    ORDER BY order_num
    """
    
    mother_df = query_db(mother_query)
    father_df = query_db(father_query)
    
    # Spanish translations for metric names
    metric_translations = {
        'math_score': 'Razonamiento Cuantitativo',
        'reading_score': 'Lectura Crítica',
        'english_score': 'Inglés',
        'citizenship_score': 'Competencias Ciudadanas',
        'avg_score': 'Promedio General'
    }
    
    def create_education_figure(df, parent_type):
        fig = go.Figure()
        
        # Add line plot
        fig.add_trace(go.Scatter(
            x=df['education_level'],
            y=df['score'],
            mode='lines+markers+text',
            text=[f'{score:.1f}' for score in df['score']],
            textposition='top center',
            textfont=dict(size=12, color='#1976D2', family='Roboto, sans-serif'),
            line=dict(color='#1976D2', width=3),
            marker=dict(
                size=8,
                color='#1976D2',
                line=dict(color='white', width=2)
            ),
            hovertemplate="<b>%{x}</b><br>" +
                         "Puntaje: %{y:.1f}<br>" +
                         "Estudiantes: %{customdata:,.0f}<br>" +
                         "<extra></extra>",
            customdata=df['count']
        ))
        
        parent_name = "Madre" if parent_type == "mother" else "Padre"
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f'Relación entre Nivel Educativo de la {parent_name} y {metric_translations[metric]}',
                font=dict(size=22, color='#2c3e50', family='Roboto, sans-serif'),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                title=dict(
                    text='Nivel Educativo',
                    font=dict(size=14, color='#2c3e50', family='Roboto, sans-serif')
                ),
                showgrid=True,
                gridcolor='rgba(189, 195, 199, 0.4)',
                showline=True,
                linewidth=2,
                linecolor='#2c3e50',
                tickangle=45
            ),
            yaxis=dict(
                title=dict(
                    text='Puntaje Promedio',
                    font=dict(size=14, color='#2c3e50', family='Roboto, sans-serif')
                ),
                showgrid=True,
                gridcolor='rgba(189, 195, 199, 0.4)',
                showline=True,
                linewidth=2,
                linecolor='#2c3e50',
                range=[min(df['score']) - 2, max(df['score']) + 2]
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False,
            margin=dict(l=60, r=60, t=100, b=150),
            height=700,
            annotations=[
                dict(
                    text='Fuente: Base de Datos Saber Pro',
                    xref='paper',
                    yref='paper',
                    x=1,
                    y=-0.4,
                    showarrow=False,
                    font=dict(size=12, color='#7f8c8d', family='Roboto, sans-serif'),
                    align='right'
                )
            ],
            hovermode='x unified'
        )
        
        # Add a subtle grid pattern
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(189, 195, 199, 0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(189, 195, 199, 0.2)')
        
        return fig
    
    return create_education_figure(mother_df, "mother"), create_education_figure(father_df, "father")

# Add new callback for tuition costs vs performance graph
@app.callback(
    Output('tuition-performance-graph', 'figure'),
    [Input('tuition-performance-metric', 'value'),
     Input('institution-type', 'value')]
)
def update_tuition_performance_graph(metric, institution_type):
    # Define the metric mapping
    metric_mapping = {
        'avg_score': '(mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0',
        'math_score': 'mod_razona_cuantitat_punt',
        'reading_score': 'mod_lectura_critica_punt',
        'english_score': 'mod_ingles_punt',
        'citizenship_score': 'mod_competen_ciudada_punt'
    }
    
    # Spanish translations for metric names
    metric_translations = {
        'math_score': 'Razonamiento Cuantitativo',
        'reading_score': 'Lectura Crítica',
        'english_score': 'Inglés',
        'citizenship_score': 'Competencias Ciudadanas',
        'avg_score': 'Promedio General'
    }
    
    # Query to get average scores by tuition cost ranges
    query = f"""
    WITH standardized_data AS (
        SELECT 
            estu_valormatriculauniversidad,
            CASE 
                WHEN inst_origen IN ('OFICIAL DEPARTAMENTAL', 'OFICIAL NACIONAL', 'OFICIAL MUNICIPAL') THEN 'OFICIAL'
                WHEN inst_origen IN ('NO OFICIAL - CORPORACIÓN', 'NO OFICIAL - FUNDACIÓN') THEN 'NO OFICIAL'
                WHEN inst_origen = 'REGIMEN ESPECIAL' THEN 'REGIMEN ESPECIAL'
                ELSE inst_origen
            END as inst_origen_std,
            {metric_mapping[metric]} as score
        FROM saber_pro
        WHERE estu_valormatriculauniversidad IS NOT NULL 
        AND estu_valormatriculauniversidad != 'No pagó matrícula'
        {" AND (inst_origen IN ('OFICIAL DEPARTAMENTAL', 'OFICIAL NACIONAL', 'OFICIAL MUNICIPAL')" + 
          " OR inst_origen IN ('NO OFICIAL - CORPORACIÓN', 'NO OFICIAL - FUNDACIÓN')" +
          " OR inst_origen = 'REGIMEN ESPECIAL')" if institution_type == 'all' else
          " AND (CASE " +
          "WHEN '" + institution_type + "' = 'OFICIAL' THEN inst_origen IN ('OFICIAL DEPARTAMENTAL', 'OFICIAL NACIONAL', 'OFICIAL MUNICIPAL') " +
          "WHEN '" + institution_type + "' = 'NO OFICIAL' THEN inst_origen IN ('NO OFICIAL - CORPORACIÓN', 'NO OFICIAL - FUNDACIÓN') " +
          "ELSE inst_origen = '" + institution_type + "' END)"}
    )
    SELECT 
        estu_valormatriculauniversidad as tuition_range,
        inst_origen_std as institution_type,
        ROUND(AVG(score), 2) as score,
        COUNT(*) as count,
        CASE estu_valormatriculauniversidad
            WHEN 'Menos de 500 mil' THEN 1
            WHEN 'Entre 500 mil y menos de 1 millón' THEN 2
            WHEN 'Entre 1 millón y menos de 2.5 millones' THEN 3
            WHEN 'Entre 2.5 millones y menos de 4 millones' THEN 4
            WHEN 'Entre 4 millones y menos de 5.5 millones' THEN 5
            WHEN 'Entre 5.5 millones y menos de 7 millones' THEN 6
            WHEN 'Más de 7 millones' THEN 7
            ELSE 8
        END as order_num
    FROM standardized_data
    GROUP BY tuition_range, inst_origen_std, order_num
    ORDER BY order_num
    """
    
    df = query_db(query)
    
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos disponibles para el análisis de costos de matrícula",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color=COLORS['primary'])
        )
        return fig

    # Create figure
    fig = go.Figure()
    
    # Names mapping for institution types
    names = {
        'OFICIAL': 'Oficial',
        'NO OFICIAL': 'No Oficial',
        'REGIMEN ESPECIAL': 'Régimen Especial'
    }
    
    if institution_type == 'all':
        # Add a line for each institution type
        for inst_type in INSTITUTION_COLORS.keys():
            inst_data = df[df['institution_type'] == inst_type]
            if not inst_data.empty:
                fig.add_trace(go.Scatter(
                    x=inst_data['tuition_range'],
                    y=inst_data['score'],
                    name=names[inst_type],
                    mode='lines+markers+text',
                    text=[f'{score:.1f}' for score in inst_data['score']],
                    textposition='top center',
                    textfont=dict(
                        size=12,
                        color=INSTITUTION_COLORS[inst_type],
                        family=FONTS['primary']
                    ),
                    line=dict(
                        color=INSTITUTION_COLORS[inst_type],
                        width=3
                    ),
                    marker=dict(
                        size=8,
                        color=INSTITUTION_COLORS[inst_type],
                        line=dict(color=COLORS['white'], width=2)
                    ),
                    hovertemplate="<b>%{x}</b><br>" +
                                 f"{names[inst_type]}<br>" +
                                 "Puntaje: %{y:.1f}<br>" +
                                 "Estudiantes: %{customdata:,.0f}<br>" +
                                 "<extra></extra>",
                    customdata=inst_data['count']
                ))
    else:
        # Add single line for selected institution type
        fig.add_trace(go.Scatter(
            x=df['tuition_range'],
            y=df['score'],
            name=names.get(institution_type, institution_type),
            mode='lines+markers+text',
            text=[f'{score:.1f}' for score in df['score']],
            textposition='top center',
            textfont=dict(
                size=12,
                color=INSTITUTION_COLORS.get(institution_type, COLORS['accent1']),
                family=FONTS['primary']
            ),
            line=dict(
                color=INSTITUTION_COLORS.get(institution_type, COLORS['accent1']),
                width=3
            ),
            marker=dict(
                size=8,
                color=INSTITUTION_COLORS.get(institution_type, COLORS['accent1']),
                line=dict(color=COLORS['white'], width=2)
            ),
            hovertemplate="<b>%{x}</b><br>" +
                         "Puntaje: %{y:.1f}<br>" +
                         "Estudiantes: %{customdata:,.0f}<br>" +
                         "<extra></extra>",
            customdata=df['count']
        ))
    
    # Update layout using the base layout function
    fig.update_layout(
        title=dict(
            text=f'Relación entre Costos de Matrícula y {metric_translations[metric]}',
            font=dict(
                size=22,
                color='#2c3e50',
                family=FONTS['primary']
            ),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(
                text='Rango de Costos de Matrícula',
                font=dict(
                    size=14,
                    color='#2c3e50',
                    family=FONTS['primary']
                )
            ),
            tickangle=45,
            showgrid=True,
            gridcolor=COLORS['grid'],
            showline=True,
            linewidth=2,
            linecolor='#2c3e50'
        ),
        yaxis=dict(
            title=dict(
                text='Puntaje Promedio',
                font=dict(
                    size=14,
                    color='#2c3e50',
                    family=FONTS['primary']
                )
            ),
            showgrid=True,
            gridcolor=COLORS['grid'],
            showline=True,
            linewidth=2,
            linecolor='#2c3e50',
            range=[min(df['score']) - 2, max(df['score']) + 2]
        ),
        plot_bgcolor=COLORS['white'],
        paper_bgcolor=COLORS['white'],
        showlegend=institution_type == 'all',
        legend=dict(
            yanchor="top",
            y=0.99,  # At the top
            xanchor="center",
            x=0.5,  # Centered horizontally
            orientation="h",  # Horizontal layout
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#2c3e50',
            borderwidth=1
        ),
        margin=dict(l=60, r=60, t=100, b=60),  # Reduced bottom margin since legend is now at top
        height=700,
        annotations=[
            dict(
                text='Fuente: Base de Datos Saber Pro',
                xref='paper',
                yref='paper',
                x=1,
                y=-0.4,
                showarrow=False,
                font=dict(
                    size=12,
                    color=COLORS['secondary'],
                    family=FONTS['primary']
                ),
                align='right'
            )
        ],
        hovermode='x unified'
    )
    
    # Add a subtle grid pattern
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(189, 195, 199, 0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(189, 195, 199, 0.2)')
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host=host, port=port) 