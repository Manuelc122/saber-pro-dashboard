from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.data_processing import query_db
from pathlib import Path

# Initialize the Dash app
app = Dash(__name__, 
    external_stylesheets=[
        'https://codepen.io/chriddyp/pen/bWLwgP.css',
        'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap'
    ]
)

# Add this near the top after app initialization
server = app.server  # This is needed for production deployment

# Add port configuration
port = int(os.environ.get('PORT', 8051))
host = '0.0.0.0'

# Added database existence check for dashboard
_db_path = Path(__file__).parent.parent / 'data' / 'processed' / 'saber_pro.db'
_db_warning = None if _db_path.exists() else html.Div(
    "Base de datos no encontrada. Por favor, ejecute create_database.py primero para crear y poblar la base de datos.",
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

# Updated dashboard layout with dataset overview tab
app.layout = html.Div([
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
    # Query for education costs
    query = """
    SELECT 
        ESTU_VALORMATRICULAUNIVERSIDAD as cost_range,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage
    FROM saber_pro
    WHERE ESTU_VALORMATRICULAUNIVERSIDAD IS NOT NULL
    GROUP BY ESTU_VALORMATRICULAUNIVERSIDAD
    ORDER BY 
        CASE ESTU_VALORMATRICULAUNIVERSIDAD
            WHEN 'No pagó matrícula' THEN 1
            WHEN 'Menos de 500 mil' THEN 2
            WHEN 'Entre 500 mil y menos de 1 millón' THEN 3
            WHEN 'Entre 1 millón y menos de 2.5 millones' THEN 4
            WHEN 'Entre 2.5 millones y menos de 4 millones' THEN 5
            WHEN 'Entre 4 millones y menos de 5.5 millones' THEN 6
            WHEN 'Entre 5.5 millones y menos de 7 millones' THEN 7
            WHEN 'Más de 7 millones' THEN 8
            ELSE 9
        END
    """
    costs_df = query_db(query)

    # Query for payment methods
    payment_query = """
    WITH payment_methods AS (
        SELECT 
            'Beca' as method,
            COUNT(CASE WHEN ESTU_PAGOMATRICULABECA = 'Si' THEN 1 END) as count,
            ROUND(AVG(CASE WHEN ESTU_PAGOMATRICULABECA = 'Si' THEN 
                (mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0 
            END), 1) as avg_score
        FROM saber_pro
        WHERE ESTU_PAGOMATRICULABECA IS NOT NULL
        
        UNION ALL
        
        SELECT 
            'Crédito' as method,
            COUNT(CASE WHEN ESTU_PAGOMATRICULACREDITO = 'Si' THEN 1 END) as count,
            ROUND(AVG(CASE WHEN ESTU_PAGOMATRICULACREDITO = 'Si' THEN 
                (mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0 
            END), 1) as avg_score
        FROM saber_pro
        WHERE ESTU_PAGOMATRICULACREDITO IS NOT NULL
        
        UNION ALL
        
        SELECT 
            'Padres' as method,
            COUNT(CASE WHEN ESTU_PAGOMATRICULAPADRES = 'Si' THEN 1 END) as count,
            ROUND(AVG(CASE WHEN ESTU_PAGOMATRICULAPADRES = 'Si' THEN 
                (mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0 
            END), 1) as avg_score
        FROM saber_pro
        WHERE ESTU_PAGOMATRICULAPADRES IS NOT NULL
        
        UNION ALL
        
        SELECT 
            'Recursos Propios' as method,
            COUNT(CASE WHEN ESTU_PAGOMATRICULAPROPIO = 'Si' THEN 1 END) as count,
            ROUND(AVG(CASE WHEN ESTU_PAGOMATRICULAPROPIO = 'Si' THEN 
                (mod_razona_cuantitat_punt + mod_lectura_critica_punt + mod_ingles_punt + mod_competen_ciudada_punt)/4.0 
            END), 1) as avg_score
        FROM saber_pro
        WHERE ESTU_PAGOMATRICULAPROPIO IS NOT NULL
    )
    SELECT * FROM payment_methods
    ORDER BY count DESC
    """
    payment_df = query_db(payment_query)
    
    # Create the costs distribution graph
    costs_fig = go.Figure()
    
    # Add bars for student counts
    costs_fig.add_trace(go.Bar(
        x=costs_df['cost_range'],
        y=costs_df['count'],
        name='Cantidad de Estudiantes',
        marker_color='#1976D2'
    ))

    # Update layout
    costs_fig.update_layout(
        title={
            'text': 'Distribución de Costos de Matrícula',
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
        xaxis_title='Rango de Costos',
        yaxis_title='Cantidad de Estudiantes',
        template='plotly_white',
        showlegend=False,
        xaxis={'categoryorder': 'array', 'categoryarray': costs_df['cost_range'].tolist()},
        hoverlabel={'bgcolor': 'white'},
        hovermode='x unified'
    )

    # Add percentage labels on top of bars
    costs_fig.update_traces(
        text=[f"{p:.1f}%" for p in costs_df['percentage']],
        textposition='outside',
        hovertemplate="<br>".join([
            "<b>%{x}</b>",
            "Cantidad: %{y:,.0f}",
            "Porcentaje: %{text}"
        ])
    )

    # Create payment methods graph
    payment_fig = go.Figure()
    
    # Add bars for payment methods
    payment_fig.add_trace(go.Bar(
        x=payment_df['method'],
        y=payment_df['count'],
        text=[f"{count:,.0f}<br>({score:.1f})" for count, score in zip(payment_df['count'], payment_df['avg_score'])],
        textposition='auto',
        marker_color='#1976D2',
        hovertemplate="<b>%{x}</b><br>" +
                     "Cantidad: %{y:,.0f}<br>" +
                     "Puntaje: %{customdata:.1f}<br>" +
                     "<extra></extra>",
        customdata=payment_df['avg_score']
    ))

    # Update layout for payment methods graph
    payment_fig.update_layout(
        title={
            'text': 'Distribución de Métodos de Pago',
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
        xaxis_title='Método de Pago',
        yaxis_title='Cantidad de Estudiantes',
        template='plotly_white',
        showlegend=False,
        hoverlabel={'bgcolor': 'white'},
        hovermode='x unified',
        margin=dict(t=80, r=20, l=20, b=20),
        height=500
    )

    return html.Div([
        # Costs Distribution Table
        html.Div([
            html.H5("Distribución de Costos", style=TABLE_TITLE_STYLE),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Rango de Costos", style={
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
                        html.Td(row['cost_range'], style={
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
                    ]) for _, row in costs_df.iterrows()
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
        
        # Costs Distribution Graph
        dcc.Graph(
            figure=costs_fig,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            },
            style={
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'padding': '15px',
                'marginBottom': '20px'
            }
        ),
        
        # Payment Methods Table
        html.Div([
            html.H5("Métodos de Pago", style=TABLE_TITLE_STYLE),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Método", style={
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
                        html.Td(row['method'], style={
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
                        html.Td(f"{row['avg_score']:.1f}", style={
                            'padding': '10px',
                            'backgroundColor': 'white',
                            'textAlign': 'right',
                            'borderBottom': '1px solid #e0e0e0'
                        })
                    ]) for _, row in payment_df.iterrows()
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
        
        # Payment Methods Graph
        dcc.Graph(
            figure=payment_fig,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            },
            style={
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'padding': '15px',
                'marginBottom': '20px'
            }
        )
    ], style={
        'backgroundColor': '#f8f9fa',
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

if __name__ == '__main__':
    app.run_server(debug=True, host=host, port=port) 