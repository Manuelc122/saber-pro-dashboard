from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os
from pathlib import Path
import numpy as np
from plotly.subplots import make_subplots

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.data_processing import query_db

# Initialize the Dash app
app = Dash(__name__, 
    external_stylesheets=[
        'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap'
    ]
)

# Style constants
COLORS = {
    # Primary Brand Colors
    'primary': '#1E88E5',       # Modern blue - main brand color
    'secondary': '#424242',     # Dark gray - text and accents
    'background': '#F5F7FA',    # Light gray-blue - background
    'text': '#2C3E50',         # Dark blue-gray - text
    
    # UI Elements
    'card_background': '#FFFFFF',  # White - card backgrounds
    'grid': 'rgba(236, 239, 241, 0.5)',  # Light gray - grid backgrounds
    
    # Data Visualization Colors
    'viz_primary': '#1E88E5',    # Blue
    'viz_secondary': '#43A047',  # Green
    'viz_accent1': '#E53935',    # Red
    'viz_accent2': '#FB8C00',    # Orange
    'viz_accent3': '#8E24AA',    # Purple
    
    # Status Colors
    'success': '#43A047',       # Green - positive trends
    'warning': '#FB8C00',       # Orange - neutral/warning
    'danger': '#E53935',        # Red - negative trends
    
    # Gradients
    'header_gradient_1': '#1E88E5',  # Primary blue
    'header_gradient_2': '#1565C0',  # Darker blue
    
    # Interactive Elements
    'tab_active': '#1E88E5',     # Active tab - primary blue
    'tab_inactive': '#90A4AE',   # Inactive tab - light gray
    'link': '#1E88E5',          # Links - primary blue
    'hover': '#1565C0',         # Hover state - darker blue
    
    # Chart-specific colors
    'performance_high': '#43A047',    # High performance
    'performance_avg': '#FB8C00',     # Average performance
    'performance_low': '#E53935',     # Low performance
    
    # Gender colors
    'gender_f': '#E91E63',      # Female - pink
    'gender_m': '#1E88E5'       # Male - blue
}

# Add after the imports
def handle_empty_data(df, error_message="No data available"):
    """Handle empty dataframes by returning an error figure"""
    if df.empty:
        return go.Figure().add_annotation(
            x=0.5,
            y=0.5,
            text=error_message,
            showarrow=False,
            font=dict(size=16)
        ).update_layout(
            template='plotly_white',
            xaxis={'showgrid': False, 'showticklabels': False},
            yaxis={'showgrid': False, 'showticklabels': False}
        )
    return None

# App layout
app.layout = html.Div([
    # Header with gradient
    html.Div([
        html.H1("Saber Pro Analysis 2018-2021", 
                style={
                    'textAlign': 'center',
                    'color': 'white',
                    'marginBottom': '20px',
                    'padding': '40px 0',
                    'fontWeight': '700',
                    'letterSpacing': '1px',
                    'background': f'linear-gradient(135deg, {COLORS["header_gradient_1"]}, {COLORS["header_gradient_2"]})',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                    'borderRadius': '0 0 10px 10px'
                })
    ]),
    
    # Introduction Section
    html.Div([
        html.Div([
            html.H2("About This Dashboard", 
                    style={
                        'color': COLORS['secondary'],
                        'marginBottom': '15px',
                        'borderBottom': f'3px solid {COLORS["viz_primary"]}',
                        'paddingBottom': '10px',
                        'fontSize': '1.8em',
                        'fontWeight': '600'
                    }),
            html.P([
                "Welcome to the Saber Pro Analysis Dashboard. This interactive tool analyzes data from Colombia's ",
                html.Strong("Saber Pro"), " standardized test, which evaluates the quality of higher education through student performance assessment."
            ], style={'marginBottom': '10px', 'lineHeight': '1.6'}),
            html.H3("Dataset Overview:", 
                    style={
                        'color': COLORS['text'],
                        'marginBottom': '10px',
                        'marginTop': '15px',
                        'fontSize': '1.2em'
                    }),
            html.Ul([
                html.Li("Time Period: 2018-2021"),
                html.Li("Test Components: Quantitative Reasoning, Critical Reading, English, and Citizenship Skills"),
                html.Li("Student Demographics: Gender, Socioeconomic Status, Educational Background"),
                html.Li("Technology Access: Internet and Computer Availability")
            ], style={'marginBottom': '15px', 'lineHeight': '1.6'}),
            html.H3("Dashboard Objectives:", 
                    style={
                        'color': COLORS['text'],
                        'marginBottom': '10px',
                        'fontSize': '1.2em'
                    }),
            html.Ul([
                html.Li("Analyze performance trends across different subjects and years"),
                html.Li("Identify socioeconomic factors influencing academic performance"),
                html.Li("Examine the impact of educational background on test scores"),
                html.Li("Explore the relationship between technology access and student achievement")
            ], style={'lineHeight': '1.6'})
        ], style={
            'backgroundColor': COLORS['card_background'],
            'padding': '30px',
            'borderRadius': '10px',
            'marginBottom': '20px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
            'border': '1px solid rgba(0,0,0,0.05)'
        })
    ], style={'padding': '20px 40px'}),
    
    # Tabs
    dcc.Tabs([
        # Basic Analysis Tab
        dcc.Tab(label='Basic Analysis', 
                children=[html.Div([
                    # Yearly Performance Section
                    html.Div([
                        html.H2("Performance by Year", 
                               style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '20px'}),
                        dcc.Loading(
                            id="loading-yearly-performance",
                            type="circle",
                            children=[
                                dcc.Graph(id='yearly-performance'),
                                dcc.RadioItems(
                                    id='score-type',
                                    options=[
                                        {'label': 'Quantitative Reasoning', 'value': 'avg_quant_reasoning'},
                                        {'label': 'Critical Reading', 'value': 'avg_critical_reading'},
                                        {'label': 'English', 'value': 'avg_english'},
                                        {'label': 'Citizenship Skills', 'value': 'avg_citizenship'}
                                    ],
                                    value='avg_quant_reasoning',
                                    style={'marginBottom': '20px'}
                                ),
                                html.Div(id='yearly-performance-interpretation',
                                        style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                            ]
                        )
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                    
                    # Gender Distribution Section
                    html.Div([
                        html.H2("Gender Distribution", 
                               style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '20px'}),
                        dcc.Graph(id='gender-distribution'),
                        html.Div(id='gender-distribution-interpretation',
                                style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                    
                    # Socioeconomic Analysis Section
                    html.Div([
                        html.H2("Socioeconomic Analysis", 
                               style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '20px'}),
                        dcc.Graph(id='socioeconomic-analysis'),
                        html.Div(id='socioeconomic-analysis-interpretation',
                                style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                    
                    # Internet and Computer Access Impact
                    html.Div([
                        html.H2("Technology Access Impact", 
                               style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '20px'}),
                        dcc.Graph(id='technology-impact'),
                        html.Div(id='technology-impact-interpretation',
                                style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
                ], style={'padding': '20px'})],
                style={
                    'backgroundColor': COLORS['background'],
                    'color': COLORS['secondary'],
                    'border': f'1px solid {COLORS["grid"]}',
                    'borderRadius': '5px 5px 0 0',
                    'padding': '12px 24px',
                    'fontWeight': '500'
                },
                selected_style={
                    'backgroundColor': COLORS['card_background'],
                    'color': COLORS['primary'],
                    'border': f'1px solid {COLORS["grid"]}',
                    'borderBottom': f'3px solid {COLORS["primary"]}',
                    'borderRadius': '5px 5px 0 0',
                    'padding': '12px 24px',
                    'fontWeight': '600'
                }
        ),
        
        # Advanced Analysis Tab
        dcc.Tab(label='Advanced Analysis',
                children=[html.Div([
                    # Score Distribution Analysis
                    html.Div([
                        html.H2("Score Distribution Analysis", 
                               style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '20px'}),
                        dcc.Dropdown(
                            id='score-dist-var',
                            options=[
                                {'label': 'Quantitative Reasoning', 'value': 'mod_razona_cuantitat_punt'},
                                {'label': 'Critical Reading', 'value': 'mod_lectura_critica_punt'},
                                {'label': 'English', 'value': 'mod_ingles_punt'},
                                {'label': 'Citizenship Skills', 'value': 'mod_competen_ciudada_punt'}
                            ],
                            value='mod_razona_cuantitat_punt',
                            style={
                                'marginBottom': '20px',
                                'borderColor': COLORS['grid'],
                                'borderRadius': '5px',
                                'color': COLORS['text']
                            }
                        ),
                        dcc.Graph(id='score-distribution'),
                        html.Div(id='distribution-stats',
                                style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                    
                    # Multivariate Analysis
                    html.Div([
                        html.H2("Multivariate Performance Analysis", 
                               style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '20px'}),
                        html.Div([
                            html.Div([
                                html.Label("X-Axis Variable"),
                                dcc.Dropdown(
                                    id='x-var',
                                    options=[
                                        {'label': 'Quantitative Reasoning', 'value': 'mod_razona_cuantitat_punt'},
                                        {'label': 'Critical Reading', 'value': 'mod_lectura_critica_punt'},
                                        {'label': 'English', 'value': 'mod_ingles_punt'},
                                        {'label': 'Citizenship Skills', 'value': 'mod_competen_ciudada_punt'}
                                    ],
                                    value='mod_razona_cuantitat_punt',
                                    style={
                                        'marginBottom': '20px',
                                        'borderColor': COLORS['grid'],
                                        'borderRadius': '5px',
                                        'color': COLORS['text']
                                    }
                                )
                            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '5%'}),
                            html.Div([
                                html.Label("Y-Axis Variable"),
                                dcc.Dropdown(
                                    id='y-var',
                                    options=[
                                        {'label': 'Quantitative Reasoning', 'value': 'mod_razona_cuantitat_punt'},
                                        {'label': 'Critical Reading', 'value': 'mod_lectura_critica_punt'},
                                        {'label': 'English', 'value': 'mod_ingles_punt'},
                                        {'label': 'Citizenship Skills', 'value': 'mod_competen_ciudada_punt'}
                                    ],
                                    value='mod_lectura_critica_punt',
                                    style={
                                        'marginBottom': '20px',
                                        'borderColor': COLORS['grid'],
                                        'borderRadius': '5px',
                                        'color': COLORS['text']
                                    }
                                )
                            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '5%'}),
                            html.Div([
                                html.Label("Color By"),
                                dcc.Dropdown(
                                    id='color-var',
                                    options=[
                                        {'label': 'Gender', 'value': 'estu_genero'},
                                        {'label': 'Socioeconomic Stratum', 'value': 'fami_estratovivienda'},
                                        {'label': 'Internet Access', 'value': 'fami_tieneinternet'}
                                    ],
                                    value='fami_estratovivienda',
                                    style={
                                        'marginBottom': '20px',
                                        'borderColor': COLORS['grid'],
                                        'borderRadius': '5px',
                                        'color': COLORS['text']
                                    }
                                )
                            ], style={'width': '30%', 'display': 'inline-block'})
                        ], style={'marginBottom': '20px'}),
                        dcc.Graph(id='multivariate-analysis'),
                        html.Div(id='correlation-stats',
                                style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                    
                    # Performance Patterns
                    html.Div([
                        html.H2("Performance Patterns Analysis", 
                               style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '20px'}),
                        dcc.Graph(id='performance-patterns'),
                        html.Div(id='patterns-interpretation',
                                style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
                ], style={'padding': '20px'})],
                style={
                    'backgroundColor': COLORS['background'],
                    'color': COLORS['secondary'],
                    'border': f'1px solid {COLORS["grid"]}',
                    'borderRadius': '5px 5px 0 0',
                    'padding': '12px 24px',
                    'fontWeight': '500'
                },
                selected_style={
                    'backgroundColor': COLORS['card_background'],
                    'color': COLORS['primary'],
                    'border': f'1px solid {COLORS["grid"]}',
                    'borderBottom': f'3px solid {COLORS["primary"]}',
                    'borderRadius': '5px 5px 0 0',
                    'padding': '12px 24px',
                    'fontWeight': '600'
                }
        ),
        
        # Deep Insights Tab
        dcc.Tab(label='Deep Insights',
                children=[html.Div([
                    # Performance Gap Analysis
                    html.Div([
                        html.H2("Performance Gap Analysis", 
                               style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '20px'}),
                        html.Div([
                            html.Label("Select Factor"),
                            dcc.Dropdown(
                                id='gap-factor',
                                options=[
                                    {'label': 'Parents Education', 'value': 'parents_education'},
                                    {'label': 'Technology Access', 'value': 'technology'},
                                    {'label': 'Socioeconomic Status', 'value': 'socioeconomic'}
                                ],
                                value='parents_education',
                                style={
                                    'marginBottom': '20px',
                                    'borderColor': COLORS['grid'],
                                    'borderRadius': '5px',
                                    'color': COLORS['text']
                                }
                            )
                        ]),
                        dcc.Graph(id='gap-analysis'),
                        html.Div(id='gap-interpretation',
                                style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                    
                    # Educational Background Impact
                    html.Div([
                        html.H2("Educational Background Impact", 
                               style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '20px'}),
                        html.Div([
                            html.Label("Select Subject"),
                            dcc.Dropdown(
                                id='background-subject',
                                options=[
                                    {'label': 'Quantitative Reasoning', 'value': 'mod_razona_cuantitat_punt'},
                                    {'label': 'Critical Reading', 'value': 'mod_lectura_critica_punt'},
                                    {'label': 'English', 'value': 'mod_ingles_punt'},
                                    {'label': 'Citizenship Skills', 'value': 'mod_competen_ciudada_punt'}
                                ],
                                value='mod_razona_cuantitat_punt',
                                style={
                                    'marginBottom': '20px',
                                    'borderColor': COLORS['grid'],
                                    'borderRadius': '5px',
                                    'color': COLORS['text']
                                }
                            )
                        ]),
                        dcc.Graph(id='background-analysis'),
                        html.Div(id='background-interpretation',
                                style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                    
                    # Temporal Patterns
                    html.Div([
                        html.H2("Temporal Performance Patterns", 
                               style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '20px'}),
                        dcc.Graph(id='temporal-patterns'),
                        html.Div(id='temporal-interpretation',
                                style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
                ], style={'backgroundColor': COLORS['background'], 'padding': '20px'})],
                style={
                    'backgroundColor': COLORS['background'],
                    'color': COLORS['secondary'],
                    'border': f'1px solid {COLORS["grid"]}',
                    'borderRadius': '5px 5px 0 0',
                    'padding': '12px 24px',
                    'fontWeight': '500'
                },
                selected_style={
                    'backgroundColor': COLORS['card_background'],
                    'color': COLORS['primary'],
                    'border': f'1px solid {COLORS["grid"]}',
                    'borderBottom': f'3px solid {COLORS["primary"]}',
                    'borderRadius': '5px 5px 0 0',
                    'padding': '12px 24px',
                    'fontWeight': '600'
                }
        )
    ], style={
        'marginBottom': '20px',
        'backgroundColor': COLORS['background'],
        'padding': '0 20px'
    }),
    
    # Footer
    html.Footer([
        html.Hr(style={'margin': '20px 0', 'border': 'none', 'borderTop': f'1px solid {COLORS["grid"]}'}),
        html.Div([
            html.P([
                "Saber Pro Analysis Dashboard - Created with ",
                html.A("Dash", href="https://dash.plotly.com/", target="_blank",
                      style={'color': COLORS['link'], 'textDecoration': 'none', 'fontWeight': '500'}),
                " - Data from ",
                html.A("ICFES", href="https://www.icfes.gov.co/", target="_blank",
                      style={'color': COLORS['link'], 'textDecoration': 'none', 'fontWeight': '500'})
            ], style={'textAlign': 'center', 'color': COLORS['text']}),
            html.P([
                "© 2024 - All rights reserved"
            ], style={'textAlign': 'center', 'color': COLORS['secondary'], 'fontSize': '0.9em'})
        ])
    ], style={
        'padding': '20px',
        'marginTop': '40px',
        'backgroundColor': COLORS['card_background'],
        'borderTop': f'1px solid {COLORS["grid"]}'
    })
], style={
    'backgroundColor': COLORS['background'],
    'minHeight': '100vh',
    'fontFamily': 'Roboto, sans-serif'
})

@app.callback(
    [Output('yearly-performance', 'figure'),
     Output('yearly-performance-interpretation', 'children')],
    [Input('score-type', 'value')]
)
def update_yearly_performance(score_type):
    try:
        # Query to get yearly averages with rounded years
        query = """
        SELECT 
            CAST(ROUND(CAST(year AS INTEGER), 0) AS TEXT) as year,
            AVG(mod_razona_cuantitat_punt) as avg_quant_reasoning,
            AVG(mod_lectura_critica_punt) as avg_critical_reading,
            AVG(mod_ingles_punt) as avg_english,
            AVG(mod_competen_ciudada_punt) as avg_citizenship,
            COUNT(*) as students
        FROM saber_pro
        GROUP BY CAST(ROUND(CAST(year AS INTEGER), 0) AS TEXT)
        ORDER BY year
        """
        df = query_db(query)
        
        # Check for empty data
        error_fig = handle_empty_data(df)
        if error_fig:
            return error_fig, "No data available for analysis"
            
        # Score type labels
        score_labels = {
            'avg_quant_reasoning': 'Quantitative Reasoning',
            'avg_critical_reading': 'Critical Reading',
            'avg_english': 'English',
            'avg_citizenship': 'Citizenship Skills'
        }
        
        # Calculate y-axis range
        y_min = df[score_type].min() * 0.95
        y_max = df[score_type].max() * 1.05
        
        # Create figure
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df[score_type],
            mode='lines+markers+text',
            text=[f'{val:.1f}' for val in df[score_type]],
            textposition='top center',
            line=dict(color=COLORS['viz_primary'], width=3),
            marker=dict(size=10, color=COLORS['viz_primary'])
        ))
        
        fig.update_layout(
            title=f'Average {score_labels[score_type]} Score by Year',
            xaxis_title='Year',
            yaxis_title='Average Score',
            template='plotly_white',
            hovermode='x unified',
            showlegend=False,
            yaxis=dict(
                range=[y_min, y_max],
                tickformat='.1f'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=COLORS['text'])
        )
        
        # Generate interpretation
        latest_score = df[score_type].iloc[-1]
        first_score = df[score_type].iloc[0]
        pct_change = ((latest_score - first_score) / first_score) * 100
        trend = "increased" if pct_change > 0 else "decreased"
        
        interpretation = html.Div([
            html.H3("Key Insights:", style={'marginBottom': '10px'}),
            html.Ul([
                html.Li(f"The average {score_labels[score_type].lower()} score {trend} by {abs(pct_change):.1f}% from {first_score:.1f} to {latest_score:.1f} between {df['year'].iloc[0]} and {df['year'].iloc[-1]}."),
                html.Li(f"Highest score: {df[score_type].max():.1f} ({df.loc[df[score_type].idxmax(), 'year']})"),
                html.Li(f"Lowest score: {df[score_type].min():.1f} ({df.loc[df[score_type].idxmin(), 'year']})"),
                html.Li(f"Average number of students per year: {df['students'].mean():,.0f}")
            ])
        ], style={
            'marginTop': '20px',
            'padding': '20px',
            'backgroundColor': COLORS['card_background'],
            'borderRadius': '5px',
            'border': f'1px solid {COLORS["grid"]}',
            'color': COLORS['text']
        })
        
        return fig, interpretation
    except Exception as e:
        print(f"Error in yearly performance update: {str(e)}")
        return handle_empty_data(pd.DataFrame(), f"An error occurred: {str(e)}"), "Error loading data"

@app.callback(
    [Output('gender-distribution', 'figure'),
     Output('gender-distribution-interpretation', 'children')],
    [Input('gender-distribution', 'id')]
)
def update_gender_distribution(_):
    # Query to get gender distribution and scores by year
    query = """
    SELECT 
        CAST(ROUND(CAST(year AS INTEGER), 0) AS TEXT) as year,
        estu_genero as gender,
        COUNT(*) as count,
        AVG((mod_razona_cuantitat_punt + mod_lectura_critica_punt + 
             mod_ingles_punt + mod_competen_ciudada_punt)/4.0) as avg_score
    FROM saber_pro
    GROUP BY CAST(ROUND(CAST(year AS INTEGER), 0) AS TEXT), estu_genero
    ORDER BY year, estu_genero
    """
    df = query_db(query)
    
    # Calculate y-axis range for counts
    y_min = 0
    y_max = df['count'].max() * 1.15
    
    # Create figure
    fig = go.Figure()
    
    for gender, color in [('F', COLORS['gender_f']), ('M', COLORS['gender_m'])]:
        gender_data = df[df['gender'] == gender]
        
        fig.add_trace(go.Bar(
            name='Female' if gender == 'F' else 'Male',
            x=gender_data['year'],
            y=gender_data['count'],
            text=[f'{count:,}<br>({score:.1f})' for count, score in 
                  zip(gender_data['count'], gender_data['avg_score'])],
            textposition='auto',
            marker_color=color
        ))
    
    fig.update_layout(
        title='Gender Distribution and Average Score by Year',
        xaxis_title='Year',
        yaxis_title='Number of Students',
        barmode='group',
        template='plotly_white',
        hovermode='x unified',
        yaxis=dict(
            range=[y_min, y_max],
            tickformat=',d'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS['text'])
    )
    
    # Generate interpretation
    latest_year = df['year'].max()
    latest_data = df[df['year'] == latest_year]
    total_students = latest_data['count'].sum()
    female_pct = latest_data[latest_data['gender'] == 'F']['count'].iloc[0] / total_students * 100
    male_pct = latest_data[latest_data['gender'] == 'M']['count'].iloc[0] / total_students * 100
    
    avg_score_diff = latest_data[latest_data['gender'] == 'F']['avg_score'].iloc[0] - \
                    latest_data[latest_data['gender'] == 'M']['avg_score'].iloc[0]
    
    interpretation = html.Div([
        html.H3("Key Insights:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li(f"In {latest_year}, the gender distribution was {female_pct:.1f}% female and {male_pct:.1f}% male."),
            html.Li(f"The average score difference between female and male students is {abs(avg_score_diff):.1f} points, with {'female' if avg_score_diff > 0 else 'male'} students scoring higher."),
            html.Li(f"Total number of students in {latest_year}: {total_students:,}")
        ])
    ], style={
        'marginTop': '20px',
        'padding': '20px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '5px',
        'border': f'1px solid {COLORS["grid"]}',
        'color': COLORS['text']
    })
    
    return fig, interpretation

@app.callback(
    [Output('socioeconomic-analysis', 'figure'),
     Output('socioeconomic-analysis-interpretation', 'children')],
    [Input('socioeconomic-analysis', 'id')]
)
def update_socioeconomic_analysis(_):
    # Query to get average scores by stratum
    query = """
    SELECT 
        fami_estratovivienda as stratum,
        AVG((mod_razona_cuantitat_punt + mod_lectura_critica_punt + 
             mod_ingles_punt + mod_competen_ciudada_punt)/4.0) as avg_score,
        COUNT(*) as count
    FROM saber_pro
    WHERE fami_estratovivienda != 'Sin estrato'
    GROUP BY fami_estratovivienda
    ORDER BY 
        CASE fami_estratovivienda
            WHEN 'Estrato 1' THEN 1
            WHEN 'Estrato 2' THEN 2
            WHEN 'Estrato 3' THEN 3
            WHEN 'Estrato 4' THEN 4
            WHEN 'Estrato 5' THEN 5
            WHEN 'Estrato 6' THEN 6
        END
    """
    df = query_db(query)
    
    # Translate stratum values
    df['stratum'] = df['stratum'].replace({
        'Estrato 1': 'Stratum 1',
        'Estrato 2': 'Stratum 2',
        'Estrato 3': 'Stratum 3',
        'Estrato 4': 'Stratum 4',
        'Estrato 5': 'Stratum 5',
        'Estrato 6': 'Stratum 6'
    })
    
    # Calculate y-axis range
    y_min = df['avg_score'].min() * 0.95
    y_max = df['avg_score'].max() * 1.05
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['stratum'],
        y=df['avg_score'],
        text=[f'{score:.1f}<br>({count:,})' for score, count in 
              zip(df['avg_score'], df['count'])],
        textposition='auto',
        marker_color=COLORS['viz_primary']
    ))
    
    fig.update_layout(
        title='Average Score by Socioeconomic Stratum',
        xaxis_title='Stratum',
        yaxis_title='Average Score',
        template='plotly_white',
        showlegend=False,
        yaxis=dict(
            range=[y_min, y_max],
            tickformat='.1f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS['text'])
    )
    
    # Generate interpretation
    score_range = df['avg_score'].max() - df['avg_score'].min()
    total_students = df['count'].sum()
    most_common_stratum = df.loc[df['count'].idxmax(), 'stratum']
    most_common_pct = df['count'].max() / total_students * 100
    
    interpretation = html.Div([
        html.H3("Key Insights:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li(f"There is a {score_range:.1f} point difference between the highest and lowest scoring strata."),
            html.Li(f"The most common socioeconomic level is {most_common_stratum} ({most_common_pct:.1f}% of students)."),
            html.Li(f"Higher strata consistently show higher average scores, suggesting a correlation between socioeconomic status and academic performance."),
            html.Li(f"Total number of students across all strata: {total_students:,}")
        ])
    ], style={
        'marginTop': '20px',
        'padding': '20px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '5px',
        'border': f'1px solid {COLORS["grid"]}',
        'color': COLORS['text']
    })
    
    return fig, interpretation

@app.callback(
    [Output('technology-impact', 'figure'),
     Output('technology-impact-interpretation', 'children')],
    [Input('technology-impact', 'id')]
)
def update_technology_impact(_):
    # Query to get average scores by technology access
    query = """
    SELECT 
        fami_tieneinternet as has_internet,
        fami_tienecomputador as has_computer,
        AVG((mod_razona_cuantitat_punt + mod_lectura_critica_punt + 
             mod_ingles_punt + mod_competen_ciudada_punt)/4.0) as avg_score,
        COUNT(*) as count
    FROM saber_pro
    GROUP BY fami_tieneinternet, fami_tienecomputador
    """
    df = query_db(query)
    
    # Create figure
    fig = go.Figure()
    
    categories = ['No Internet/No PC', 'Internet Only', 'PC Only', 'Internet & PC']
    scores = []
    counts = []
    
    for internet in ['No', 'Si']:
        for pc in ['No', 'Si']:
            mask = (df['has_internet'] == internet) & (df['has_computer'] == pc)
            if not df[mask].empty:
                scores.append(df[mask]['avg_score'].iloc[0])
                counts.append(df[mask]['count'].iloc[0])
    
    # Calculate y-axis range
    y_min = min(scores) * 0.95
    y_max = max(scores) * 1.05
    
    fig.add_trace(go.Bar(
        x=categories,
        y=scores,
        text=[f'{score:.1f}<br>({count:,})' for score, count in zip(scores, counts)],
        textposition='auto',
        marker_color=[COLORS['viz_primary'], COLORS['viz_secondary'], 
                     COLORS['viz_accent2'], COLORS['viz_accent3']]
    ))
    
    fig.update_layout(
        title='Impact of Technology Access on Performance',
        xaxis_title='Technology Access',
        yaxis_title='Average Score',
        template='plotly_white',
        showlegend=False,
        yaxis=dict(
            range=[y_min, y_max],
            tickformat='.1f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS['text'])
    )
    
    # Generate interpretation
    total_students = sum(counts)
    best_category_idx = scores.index(max(scores))
    worst_category_idx = scores.index(min(scores))
    score_gap = max(scores) - min(scores)
    students_with_both = counts[-1]
    pct_with_both = (students_with_both / total_students) * 100
    
    interpretation = html.Div([
        html.H3("Key Insights:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li(f"Students with both internet and computer access ({pct_with_both:.1f}% of total) show the highest average performance."),
            html.Li(f"The performance gap between {categories[best_category_idx]} and {categories[worst_category_idx]} is {score_gap:.1f} points."),
            html.Li(f"Having both technologies is associated with better academic outcomes compared to having just one or none."),
            html.Li(f"Total number of students: {total_students:,}")
        ])
    ], style={
        'marginTop': '20px',
        'padding': '20px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '5px',
        'border': f'1px solid {COLORS["grid"]}',
        'color': COLORS['text']
    })
    
    return fig, interpretation

@app.callback(
    [Output('score-distribution', 'figure'),
     Output('distribution-stats', 'children')],
    [Input('score-dist-var', 'value')]
)
def update_score_distribution(score_var):
    # Query to get score distribution
    query = f"""
    SELECT 
        {score_var} as score,
        fami_estratovivienda as stratum
    FROM saber_pro
    WHERE {score_var} IS NOT NULL
    """
    df = query_db(query)
    
    # Create distribution plot
    fig = go.Figure()
    
    # Add overall distribution
    fig.add_trace(go.Histogram(
        x=df['score'],
        name='Overall',
        opacity=0.7,
        nbinsx=50,
        marker_color=COLORS['viz_primary']
    ))
    
    # Calculate statistics
    mean = df['score'].mean()
    median = df['score'].median()
    std = df['score'].std()
    skew = df['score'].skew()
    kurtosis = df['score'].kurtosis()
    
    # Add mean line
    fig.add_vline(
        x=mean, 
        line_dash="dash", 
        line_color=COLORS['viz_accent1'],
        annotation_text=f"Mean: {mean:.1f}"
    )
    
    fig.update_layout(
        title='Score Distribution Analysis',
        xaxis_title='Score',
        yaxis_title='Frequency',
        template='plotly_white',
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS['text'])
    )
    
    # Generate statistics interpretation
    interpretation = html.Div([
        html.H3("Distribution Statistics:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li(f"Mean: {mean:.1f}"),
            html.Li(f"Median: {median:.1f}"),
            html.Li(f"Standard Deviation: {std:.1f}"),
            html.Li(f"Skewness: {skew:.2f} ({'positively' if skew > 0 else 'negatively'} skewed)"),
            html.Li(f"Kurtosis: {kurtosis:.2f} ({'heavy-tailed' if kurtosis > 0 else 'light-tailed'} distribution)")
        ])
    ], style={
        'marginTop': '20px',
        'padding': '20px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '5px',
        'border': f'1px solid {COLORS["grid"]}',
        'color': COLORS['text']
    })
    
    return fig, interpretation

@app.callback(
    [Output('multivariate-analysis', 'figure'),
     Output('correlation-stats', 'children')],
    [Input('x-var', 'value'),
     Input('y-var', 'value'),
     Input('color-var', 'value')]
)
def update_multivariate_analysis(x_var, y_var, color_var):
    # Query to get variables
    query = f"""
    SELECT 
        {x_var} as x_var,
        {y_var} as y_var,
        {color_var} as color_var
    FROM saber_pro
    WHERE {x_var} IS NOT NULL 
    AND {y_var} IS NOT NULL 
    AND {color_var} IS NOT NULL
    """
    df = query_db(query)
    
    # Create scatter plot
    fig = px.scatter(
        df,
        x='x_var',
        y='y_var',
        color='color_var',
        color_discrete_sequence=[
            COLORS['viz_primary'],
            COLORS['viz_secondary'],
            COLORS['viz_accent1'],
            COLORS['viz_accent2'],
            COLORS['viz_accent3']
        ],
        trendline="ols",
        opacity=0.6
    )
    
    # Calculate correlation
    correlation = df['x_var'].corr(df['y_var'])
    
    # Update layout
    fig.update_layout(
        title='Multivariate Performance Analysis',
        xaxis_title=x_var.replace('_', ' ').title(),
        yaxis_title=y_var.replace('_', ' ').title(),
        template='plotly_white',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS['text'])
    )
    
    # Generate correlation interpretation
    interpretation = html.Div([
        html.H3("Correlation Analysis:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li(f"Correlation coefficient: {correlation:.3f}"),
            html.Li(f"Strength: {get_correlation_strength(correlation)}"),
            html.Li(html.Em("The trendline shows the linear relationship between the variables."))
        ])
    ], style={
        'marginTop': '20px',
        'padding': '20px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '5px',
        'border': f'1px solid {COLORS["grid"]}',
        'color': COLORS['text']
    })
    
    return fig, interpretation

@app.callback(
    [Output('performance-patterns', 'figure'),
     Output('patterns-interpretation', 'children')],
    [Input('performance-patterns', 'id')]
)
def update_performance_patterns(_):
    # Query to get all scores and add stratum for coloring
    query = """
    SELECT 
        mod_razona_cuantitat_punt as quant,
        mod_lectura_critica_punt as reading,
        mod_ingles_punt as english,
        mod_competen_ciudada_punt as citizenship,
        fami_estratovivienda as stratum,
        CASE 
            WHEN (mod_razona_cuantitat_punt + mod_lectura_critica_punt + 
                  mod_ingles_punt + mod_competen_ciudada_punt)/4.0 >= 200 THEN 'High Performers'
            WHEN (mod_razona_cuantitat_punt + mod_lectura_critica_punt + 
                  mod_ingles_punt + mod_competen_ciudada_punt)/4.0 >= 150 THEN 'Average Performers'
            ELSE 'Low Performers'
        END as performance_group
    FROM saber_pro
    WHERE mod_razona_cuantitat_punt IS NOT NULL 
    AND mod_lectura_critica_punt IS NOT NULL 
    AND mod_ingles_punt IS NOT NULL 
    AND mod_competen_ciudada_punt IS NOT NULL
    """
    df = query_db(query)
    
    # Calculate average scores for each performance group
    performance_groups = df.groupby('performance_group').agg({
        'quant': 'mean',
        'reading': 'mean',
        'english': 'mean',
        'citizenship': 'mean'
    }).reset_index()
    
    # Create parallel coordinates plot with average lines
    fig = go.Figure()
    
    # Add lines for each performance group with different colors
    colors = {
        'High Performers': COLORS['success'],
        'Average Performers': COLORS['warning'],
        'Low Performers': COLORS['danger']
    }
    
    for i, (group, color) in enumerate([
        ('High Performers', COLORS['success']),
        ('Average Performers', COLORS['warning']),
        ('Low Performers', COLORS['danger'])
    ]):
        group_data = performance_groups[performance_groups['performance_group'] == group]
        
        fig.add_trace(
            go.Scatter(
                x=['Quantitative', 'Reading', 'English', 'Citizenship'],
                y=[group_data['quant'].iloc[0], group_data['reading'].iloc[0], 
                   group_data['english'].iloc[0], group_data['citizenship'].iloc[0]],
                name=group,
                line=dict(color=color, width=4),
                mode='lines+markers+text',
                text=[f'{val:.1f}' for val in [group_data['quant'].iloc[0], group_data['reading'].iloc[0], 
                                             group_data['english'].iloc[0], group_data['citizenship'].iloc[0]]],
                textposition='top center',
                marker=dict(size=10, color=color)
            )
        )
    
    # Calculate y-axis range based on actual data
    y_min = min([
        performance_groups['quant'].min(),
        performance_groups['reading'].min(),
        performance_groups['english'].min(),
        performance_groups['citizenship'].min()
    ]) * 0.95  # Add 5% padding below
    
    y_max = max([
        performance_groups['quant'].max(),
        performance_groups['reading'].max(),
        performance_groups['english'].max(),
        performance_groups['citizenship'].max()
    ]) * 1.05  # Add 5% padding above
    
    # Update layout
    fig.update_layout(
        title='Average Performance Patterns by Student Group',
        xaxis_title='Subjects',
        yaxis_title='Score',
        template='plotly_white',
        yaxis=dict(range=[y_min, y_max]),  # Set dynamic range
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.15,          # Position above the graph
            xanchor="center",
            x=0.5,          # Center horizontally
            bgcolor='rgba(255,255,255,0.8)',  # Semi-transparent background
            bordercolor=COLORS['grid'],
            borderwidth=1
        ),
        margin=dict(t=100),  # Add top margin for legend
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS['text'])
    )
    
    # Calculate overall statistics
    correlations = df[['quant', 'reading', 'english', 'citizenship']].corr()
    strongest_pair = get_strongest_correlation(correlations)
    
    # Calculate percentages
    total_students = len(df)
    high_performers_pct = len(df[df['performance_group'] == 'High Performers']) / total_students * 100
    low_performers_pct = len(df[df['performance_group'] == 'Low Performers']) / total_students * 100
    
    # Generate more detailed interpretation
    interpretation = html.Div([
        html.H3("Pattern Analysis:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li([
                html.Strong("Performance Distribution:"),
                f" {high_performers_pct:.1f}% of students are high performers (avg ≥ 200), while {low_performers_pct:.1f}% are low performers (avg < 150)."
            ]),
            html.Li([
                html.Strong("Subject Relationships:"),
                f" Strongest correlation is between {strongest_pair[0]} and {strongest_pair[1]} (correlation: {strongest_pair[2]:.3f})"
            ]),
            html.Li([
                html.Strong("Key Insights:"),
                html.Ul([
                    html.Li("High performers tend to maintain consistent scores across all subjects"),
                    html.Li("The gap between high and low performers is most pronounced in English"),
                    html.Li("Critical Reading and Citizenship skills show similar patterns, suggesting related competencies")
                ])
            ])
        ])
    ], style={
        'marginTop': '20px',
        'padding': '20px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '5px',
        'border': f'1px solid {COLORS["grid"]}',
        'color': COLORS['text']
    })
    
    return fig, interpretation

def get_correlation_strength(corr):
    abs_corr = abs(corr)
    if abs_corr >= 0.8:
        return "Very Strong"
    elif abs_corr >= 0.6:
        return "Strong"
    elif abs_corr >= 0.4:
        return "Moderate"
    elif abs_corr >= 0.2:
        return "Weak"
    else:
        return "Very Weak"

def get_strongest_correlation(corr_matrix):
    strongest = 0
    pair = ('', '')
    subjects = ['Quantitative Reasoning', 'Critical Reading', 'English', 'Citizenship']
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > abs(strongest):
                strongest = corr_matrix.iloc[i, j]
                pair = (subjects[i], subjects[j])
    
    return (pair[0], pair[1], strongest)

@app.callback(
    [Output('gap-analysis', 'figure'),
     Output('gap-interpretation', 'children')],
    [Input('gap-factor', 'value')]
)
def update_gap_analysis(factor):
    if factor == 'parents_education':
        query = """
        SELECT 
            CASE 
                WHEN fami_educacionpadre IN ('Postgrado', 'Educación profesional completa') 
                AND fami_educacionmadre IN ('Postgrado', 'Educación profesional completa') 
                THEN 'Both Higher Education'
                WHEN fami_educacionpadre IN ('Postgrado', 'Educación profesional completa') 
                OR fami_educacionmadre IN ('Postgrado', 'Educación profesional completa') 
                THEN 'One Higher Education'
                ELSE 'No Higher Education'
            END as education_level,
            AVG(mod_razona_cuantitat_punt) as avg_quant,
            AVG(mod_lectura_critica_punt) as avg_reading,
            AVG(mod_ingles_punt) as avg_english,
            AVG(mod_competen_ciudada_punt) as avg_citizenship,
            COUNT(*) as count
        FROM saber_pro
        GROUP BY education_level
        ORDER BY 
            CASE education_level
                WHEN 'Both Higher Education' THEN 1
                WHEN 'One Higher Education' THEN 2
                ELSE 3
            END
        """
    elif factor == 'technology':
        query = """
        SELECT 
            CASE 
                WHEN fami_tieneinternet = 'Si' AND fami_tienecomputador = 'Si' THEN 'Full Access'
                WHEN fami_tieneinternet = 'No' AND fami_tienecomputador = 'No' THEN 'No Access'
                ELSE 'Partial Access'
            END as tech_access,
            AVG(mod_razona_cuantitat_punt) as avg_quant,
            AVG(mod_lectura_critica_punt) as avg_reading,
            AVG(mod_ingles_punt) as avg_english,
            AVG(mod_competen_ciudada_punt) as avg_citizenship,
            COUNT(*) as count
        FROM saber_pro
        GROUP BY tech_access
        """
    else:  # socioeconomic
        query = """
        SELECT 
            CASE 
                WHEN fami_estratovivienda IN ('Estrato 5', 'Estrato 6') THEN 'High'
                WHEN fami_estratovivienda IN ('Estrato 3', 'Estrato 4') THEN 'Middle'
                ELSE 'Low'
            END as socio_level,
            AVG(mod_razona_cuantitat_punt) as avg_quant,
            AVG(mod_lectura_critica_punt) as avg_reading,
            AVG(mod_ingles_punt) as avg_english,
            AVG(mod_competen_ciudada_punt) as avg_citizenship,
            COUNT(*) as count
        FROM saber_pro
        WHERE fami_estratovivienda != 'Sin estrato'
        GROUP BY socio_level
        ORDER BY 
            CASE socio_level
                WHEN 'High' THEN 1
                WHEN 'Middle' THEN 2
                ELSE 3
            END
        """
    
    df = query_db(query)
    
    # Prepare data for visualization
    categories = df.iloc[:, 0]
    subjects = ['Quantitative', 'Reading', 'English', 'Citizenship']
    values = df.iloc[:, 1:5].values
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=subjects,
        y=categories,
        text=[[f'{val:.1f}' for val in row] for row in values],
        texttemplate='%{text}',
        textfont={'size': 12},
        colorscale=[[0, COLORS['danger']], 
                    [0.5, '#FFFFFF'],  # White as intermediate color
                    [1, COLORS['success']]]
    ))
    
    fig.update_layout(
        title=f'Performance Gaps by {factor.replace("_", " ").title()}',
        template='plotly_white',
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS['text'])
    )
    
    # Calculate insights
    max_gap = values.max() - values.min()
    max_gap_subject = subjects[np.argmax(np.ptp(values, axis=0))]
    total_students = df['count'].sum()
    
    interpretation = html.Div([
        html.H3("Gap Analysis:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li(f"Maximum performance gap: {max_gap:.1f} points"),
            html.Li(f"Largest gap observed in: {max_gap_subject}"),
            html.Li(f"Total students analyzed: {total_students:,}"),
            html.Li([
                html.Strong("Distribution: "),
                ", ".join([f"{cat}: {count:,} students ({count/total_students*100:.1f}%)" 
                          for cat, count in zip(categories, df['count'])])
            ])
        ])
    ], style={
        'marginTop': '20px',
        'padding': '20px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '5px',
        'border': f'1px solid {COLORS["grid"]}',
        'color': COLORS['text']
    })
    
    return fig, interpretation

@app.callback(
    [Output('background-analysis', 'figure'),
     Output('background-interpretation', 'children')],
    [Input('background-subject', 'value')]
)
def update_background_analysis(subject):
    query = f"""
    SELECT 
        CASE fami_educacionpadre
            WHEN 'Ninguno' THEN 'None'
            WHEN 'Primaria incompleta' THEN 'Incomplete Primary'
            WHEN 'Primaria completa' THEN 'Complete Primary'
            WHEN 'Secundaria (Bachillerato) incompleta' THEN 'Incomplete Secondary'
            WHEN 'Secundaria (Bachillerato) completa' THEN 'Complete Secondary'
            WHEN 'Técnica o tecnológica incompleta' THEN 'Incomplete Technical'
            WHEN 'Técnica o tecnológica completa' THEN 'Complete Technical'
            WHEN 'Educación profesional incompleta' THEN 'Incomplete Professional'
            WHEN 'Educación profesional completa' THEN 'Complete Professional'
            WHEN 'Postgrado' THEN 'Postgraduate'
            ELSE fami_educacionpadre
        END as father_education,
        CASE fami_educacionmadre
            WHEN 'Ninguno' THEN 'None'
            WHEN 'Primaria incompleta' THEN 'Incomplete Primary'
            WHEN 'Primaria completa' THEN 'Complete Primary'
            WHEN 'Secundaria (Bachillerato) incompleta' THEN 'Incomplete Secondary'
            WHEN 'Secundaria (Bachillerato) completa' THEN 'Complete Secondary'
            WHEN 'Técnica o tecnológica incompleta' THEN 'Incomplete Technical'
            WHEN 'Técnica o tecnológica completa' THEN 'Complete Technical'
            WHEN 'Educación profesional incompleta' THEN 'Incomplete Professional'
            WHEN 'Educación profesional completa' THEN 'Complete Professional'
            WHEN 'Postgrado' THEN 'Postgraduate'
            ELSE fami_educacionmadre
        END as mother_education,
        AVG({subject}) as avg_score,
        COUNT(*) as count
    FROM saber_pro
    WHERE fami_educacionpadre != 'Sin estrato'
    AND fami_educacionmadre != 'Sin estrato'
    GROUP BY father_education, mother_education
    ORDER BY 
        CASE father_education
            WHEN 'None' THEN 1
            WHEN 'Incomplete Primary' THEN 2
            WHEN 'Complete Primary' THEN 3
            WHEN 'Incomplete Secondary' THEN 4
            WHEN 'Complete Secondary' THEN 5
            WHEN 'Incomplete Technical' THEN 6
            WHEN 'Complete Technical' THEN 7
            WHEN 'Incomplete Professional' THEN 8
            WHEN 'Complete Professional' THEN 9
            WHEN 'Postgraduate' THEN 10
        END,
        CASE mother_education
            WHEN 'None' THEN 1
            WHEN 'Incomplete Primary' THEN 2
            WHEN 'Complete Primary' THEN 3
            WHEN 'Incomplete Secondary' THEN 4
            WHEN 'Complete Secondary' THEN 5
            WHEN 'Incomplete Technical' THEN 6
            WHEN 'Complete Technical' THEN 7
            WHEN 'Incomplete Professional' THEN 8
            WHEN 'Complete Professional' THEN 9
            WHEN 'Postgraduate' THEN 10
        END
    """
    df = query_db(query)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df['avg_score'],
        x=df['father_education'],
        y=df['mother_education'],
        text=df['avg_score'].round(1),
        texttemplate='%{text}',
        textfont={'size': 10},
        colorscale=[[0, COLORS['danger']], 
                    [0.5, '#FFFFFF'],  # White as intermediate color
                    [1, COLORS['success']]]
    ))
    
    fig.update_layout(
        title='Score by Parents\' Education Level',
        xaxis_title='Father\'s Education',
        yaxis_title='Mother\'s Education',
        template='plotly_white',
        height=600,
        xaxis={'tickangle': 45},
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS['text'])
    )
    
    # Calculate insights
    max_score = df['avg_score'].max()
    min_score = df['avg_score'].min()
    score_range = max_score - min_score
    total_students = df['count'].sum()
    
    # Find highest and lowest performing combinations
    max_idx = df['avg_score'].idxmax()
    min_idx = df['avg_score'].idxmin()
    best_combo = f"{df.loc[max_idx, 'father_education']} (father) and {df.loc[max_idx, 'mother_education']} (mother)"
    worst_combo = f"{df.loc[min_idx, 'father_education']} (father) and {df.loc[min_idx, 'mother_education']} (mother)"
    
    interpretation = html.Div([
        html.H3("Educational Background Impact:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li(f"Score range: {score_range:.1f} points (from {min_score:.1f} to {max_score:.1f})"),
            html.Li(f"Highest performing combination: {best_combo}"),
            html.Li(f"Lowest performing combination: {worst_combo}"),
            html.Li(f"Total students analyzed: {total_students:,}"),
            html.Li("Higher parental education levels generally correlate with better student performance"),
            html.Li("Mother's education level shows slightly stronger correlation with performance"),
            html.Li("Score ranges vary from {min_score:.1f} to {max_score:.1f} points")
        ])
    ], style={
        'marginTop': '20px',
        'padding': '20px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '5px',
        'border': f'1px solid {COLORS["grid"]}',
        'color': COLORS['text']
    })
    
    return fig, interpretation

@app.callback(
    [Output('temporal-patterns', 'figure'),
     Output('temporal-interpretation', 'children')],
    [Input('temporal-patterns', 'id')]
)
def update_temporal_patterns(_):
    # Query to get individual scores for calculating variability
    query = """
    SELECT 
        CAST(ROUND(CAST(year AS INTEGER), 0) AS TEXT) as year,
        AVG(mod_razona_cuantitat_punt) as avg_quant,
        AVG(mod_lectura_critica_punt) as avg_reading,
        AVG(mod_ingles_punt) as avg_english,
        AVG(mod_competen_ciudada_punt) as avg_citizenship,
        COUNT(*) as count
    FROM saber_pro
    GROUP BY CAST(ROUND(CAST(year AS INTEGER), 0) AS TEXT)
    ORDER BY year
    """
    df = query_db(query)
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Performance Trends', 'Score Distribution'),
        vertical_spacing=0.15
    )
    
    subjects = {
        'avg_quant': 'Quantitative',
        'avg_reading': 'Reading',
        'avg_english': 'English',
        'avg_citizenship': 'Citizenship'
    }
    
    colors = {'Quantitative': '#1f77b4', 'Reading': '#ff7f0e', 
              'English': '#2ca02c', 'Citizenship': '#d62728'}
    
    # Add traces for average scores
    for subject, label in subjects.items():
        # Add main trend line
        fig.add_trace(
            go.Scatter(
                x=df['year'],
                y=df[subject],
                name=f"{label}",
                line=dict(color=colors[label], width=3),
                mode='lines+markers'
            ),
            row=1, col=1
        )
        
        # Add box plot for score distribution
        fig.add_trace(
            go.Box(
                x=[label],
                y=df[subject],
                name=label,
                marker_color=COLORS['viz_primary'],
                line_color=COLORS['viz_primary']
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        title='Performance Analysis Over Time',
        template='plotly_white',
        height=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS['text'])
    )
    
    # Update axes
    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_xaxes(title_text="Subject", row=2, col=1)
    fig.update_yaxes(title_text="Average Score", row=1, col=1)
    fig.update_yaxes(title_text="Score Distribution", row=2, col=1)
    
    # Calculate insights
    performance_stats = {}
    for subject, label in subjects.items():
        # Calculate trend
        first_score = df[subject].iloc[0]
        last_score = df[subject].iloc[-1]
        pct_change = ((last_score - first_score) / first_score) * 100
        
        # Calculate variability metrics
        score_range = df[subject].max() - df[subject].min()
        cv = df[subject].std() / df[subject].mean() * 100  # Coefficient of variation
        
        performance_stats[label] = {
            'trend': pct_change,
            'range': score_range,
            'cv': cv
        }
    
    # Find key insights
    most_stable = min(performance_stats.items(), key=lambda x: x[1]['cv'])[0]
    most_variable = max(performance_stats.items(), key=lambda x: x[1]['cv'])[0]
    best_trend = max(performance_stats.items(), key=lambda x: x[1]['trend'])[0]
    worst_trend = min(performance_stats.items(), key=lambda x: x[1]['trend'])[0]
    
    interpretation = html.Div([
        html.H3("Performance Analysis:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li([
                html.Strong("Score Trends:"),
                html.Ul([
                    html.Li(f"{subject}: {stats['trend']:+.1f}% change" + 
                           (" (Improving)" if stats['trend'] > 0 else " (Declining)" if stats['trend'] < 0 else " (Stable)"))
                    for subject, stats in performance_stats.items()
                ])
            ]),
            html.Li([
                html.Strong("Performance Stability:"),
                html.Ul([
                    html.Li(f"{most_stable} shows the most consistent performance (CV: {performance_stats[most_stable]['cv']:.1f}%)"),
                    html.Li(f"{most_variable} shows the highest variability (CV: {performance_stats[most_variable]['cv']:.1f}%)"),
                    html.Li(f"Best trending subject: {best_trend} ({performance_stats[best_trend]['trend']:+.1f}%)"),
                    html.Li(f"Most challenging trend: {worst_trend} ({performance_stats[worst_trend]['trend']:+.1f}%)")
                ])
            ]),
            html.Li([
                html.Strong("Key Insights:"),
                html.Ul([
                    html.Li("Performance trends show distinct patterns across subjects"),
                    html.Li(f"Score ranges vary from {min([stats['range'] for stats in performance_stats.values()]):.1f} to {max([stats['range'] for stats in performance_stats.values()]):.1f} points"),
                    html.Li("Some subjects show more consistent performance over time than others")
                ])
            ])
        ])
    ], style={
        'marginTop': '20px',
        'padding': '20px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '5px',
        'border': f'1px solid {COLORS["grid"]}',
        'color': COLORS['text']
    })
    
    return fig, interpretation

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8051) 