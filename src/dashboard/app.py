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

# Initialize the Dash app with server configuration
app = Dash(__name__, 
    external_stylesheets=[
        'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap',
        'https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap',
        'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css'
    ],
    suppress_callback_exceptions=True
)

# Configure server for production
server = app.server

# Style constants with enhanced color palette
COLORS = {
    'primary': '#2962FF',      # Vibrant blue
    'secondary': '#00C853',    # Emerald green
    'accent1': '#FF6D00',      # Deep orange
    'accent2': '#6200EA',      # Deep purple
    'accent3': '#FFD600',      # Bright yellow
    'background': '#F5F7FA',   # Light gray-blue
    'card_bg': '#FFFFFF',      # Pure white
    'text': '#1A237E',         # Deep indigo
    'text_light': '#5C6BC0',   # Light indigo
    'grid': '#E8EAF6',         # Light indigo grid
    'success': '#00C853',      # Success green
    'warning': '#FF6D00',      # Warning orange
    'error': '#D50000',        # Error red
    'border': '#C5CAE9',       # Border indigo
    'gradient_start': '#1A237E',  # Deep indigo
    'gradient_end': '#3949AB'     # Light indigo
}

# App layout with enhanced styling
app.layout = html.Div([
    # Header with animated gradient background
    html.Div([
        html.H1("Saber Pro Analysis Dashboard", 
                className='animate__animated animate__fadeIn',
                style={
                    'textAlign': 'center', 
                    'color': 'white', 
                    'marginBottom': '20px',
                    'fontFamily': 'Poppins, sans-serif', 
                    'fontWeight': '600', 
                    'fontSize': '3rem',
                    'textShadow': '2px 2px 4px rgba(0,0,0,0.3)',
                    'letterSpacing': '1px',
                    'padding': '50px 0'
                }),
        html.H2("2018-2021 Performance Analysis",
                className='animate__animated animate__fadeIn animate__delay-1s',
                style={
                    'textAlign': 'center',
                    'color': 'rgba(255,255,255,0.9)',
                    'fontFamily': 'Poppins, sans-serif',
                    'fontWeight': '400',
                    'fontSize': '1.5rem',
                    'marginTop': '-10px'
                })
    ], style={
        'background': f'linear-gradient(135deg, {COLORS["gradient_start"]}, {COLORS["gradient_end"]})',
        'marginBottom': '40px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
        'borderRadius': '0 0 20px 20px',
        'animation': 'gradient 15s ease infinite',
    }),
    
    # Introduction Section with enhanced styling
    html.Div([
        html.Div([
            html.H2("About This Dashboard", 
                   className='animate__animated animate__fadeIn',
                   style={'color': COLORS['text'], 
                         'marginBottom': '25px', 
                         'fontSize': '2.2rem',
                         'fontWeight': '600',
                         'fontFamily': 'Poppins, sans-serif',
                         'borderBottom': f'3px solid {COLORS["accent1"]}',
                         'paddingBottom': '15px'}),
            html.P([
                "Welcome to the Saber Pro Analysis Dashboard, a comprehensive tool designed to analyze and visualize the performance trends in Colombia's national standardized test for higher education.",
                html.Br(), html.Br(),
                html.Strong("Objective: ", style={'color': COLORS['primary'], 'fontSize': '1.2rem'}),
                "To provide educational stakeholders with deep insights into student performance patterns, socioeconomic impacts, and educational gaps across different demographics.",
                html.Br(), html.Br(),
                html.Strong("Dataset: ", style={'color': COLORS['primary'], 'fontSize': '1.2rem'}),
                "This analysis is based on Saber Pro test results from 2018 to 2021, covering multiple competency areas including Quantitative Reasoning, Critical Reading, English, and Citizenship Skills.",
                html.Br(), html.Br(),
                html.Strong("Key Features:", style={'color': COLORS['primary'], 'fontSize': '1.2rem'}),
                html.Ul([
                    html.Li("Basic Analysis: Overview of performance trends, gender distribution, and socioeconomic factors",
                           style={'marginBottom': '12px', 'fontSize': '1.1rem'}),
                    html.Li("Advanced Analysis: Detailed statistical analysis of score distributions and correlations",
                           style={'marginBottom': '12px', 'fontSize': '1.1rem'}),
                    html.Li("Deep Insights: Comprehensive analysis of performance gaps and educational background impact",
                           style={'marginBottom': '12px', 'fontSize': '1.1rem'})
                ], style={'paddingLeft': '25px'})
            ], style={'fontSize': '1.1rem', 
                     'lineHeight': '1.8', 
                     'color': COLORS['text'],
                     'textAlign': 'justify'})
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '35px',
            'borderRadius': '20px',
            'boxShadow': '0 8px 16px rgba(0,0,0,0.1)',
            'marginBottom': '40px',
            'border': f'1px solid {COLORS["border"]}',
            'transition': 'transform 0.3s ease-in-out',
            ':hover': {
                'transform': 'translateY(-5px)'
            }
        })
    ], style={'padding': '0 40px'}),
    
    # Tabs with enhanced styling
    dcc.Tabs([
        dcc.Tab(
            label='Basic Analysis',
            className='custom-tab',
            style={
                'backgroundColor': COLORS['background'],
                'color': COLORS['text_light'],
                'fontFamily': 'Poppins, sans-serif',
                'fontWeight': '600',
                'padding': '16px 32px',
                'borderRadius': '15px 15px 0 0',
                'border': f'1px solid {COLORS["border"]}',
                'borderBottom': 'none',
                'transition': 'all 0.3s ease-in-out'
            },
            selected_style={
                'backgroundColor': COLORS['card_bg'],
                'color': COLORS['primary'],
                'fontFamily': 'Poppins, sans-serif',
                'fontWeight': '600',
                'padding': '16px 32px',
                'borderRadius': '15px 15px 0 0',
                'border': f'1px solid {COLORS["border"]}',
                'borderBottom': 'none',
                'boxShadow': '0 -4px 8px rgba(0,0,0,0.1)'
            },
            children=[
                html.Div([
                    # Content sections with enhanced styling
                    html.Div([
                        html.H2("Performance by Year", 
                               className='animate__animated animate__fadeIn',
                               style={'textAlign': 'center', 
                                     'color': COLORS['text'], 
                                     'marginBottom': '30px',
                                     'fontSize': '2rem',
                                     'fontWeight': '600',
                                     'fontFamily': 'Poppins, sans-serif',
                                     'borderBottom': f'3px solid {COLORS["accent1"]}',
                                     'paddingBottom': '15px'}),
                        dcc.Graph(id='yearly-performance',
                                 style={'boxShadow': '0 4px 8px rgba(0,0,0,0.05)',
                                       'borderRadius': '10px',
                                       'backgroundColor': 'white',
                                       'padding': '15px'}),
                        html.Div([
                            dcc.RadioItems(
                                id='score-type',
                                options=[
                                    {'label': 'Quantitative Reasoning', 'value': 'avg_quant_reasoning'},
                                    {'label': 'Critical Reading', 'value': 'avg_critical_reading'},
                                    {'label': 'English', 'value': 'avg_english'},
                                    {'label': 'Citizenship Skills', 'value': 'avg_citizenship'}
                                ],
                                value='avg_quant_reasoning',
                                className='custom-radio',
                                style={'marginBottom': '25px',
                                      'padding': '20px',
                                      'backgroundColor': COLORS['background'],
                                      'borderRadius': '15px',
                                      'border': f'1px solid {COLORS["border"]}',
                                      'display': 'flex',
                                      'justifyContent': 'center',
                                      'gap': '20px'},
                                labelStyle={'display': 'inline-block', 
                                          'margin': '0 15px',
                                          'padding': '10px 20px',
                                          'cursor': 'pointer',
                                          'color': COLORS['text'],
                                          'borderRadius': '8px',
                                          'transition': 'all 0.3s ease',
                                          ':hover': {
                                              'backgroundColor': COLORS['primary'],
                                              'color': 'white'
                                          }}
                            )
                        ], style={'marginTop': '30px'}),
                        html.Div(id='yearly-performance-interpretation',
                                style={'marginTop': '30px', 
                                      'padding': '25px', 
                                      'backgroundColor': COLORS['background'], 
                                      'borderRadius': '15px',
                                      'border': f'1px solid {COLORS["border"]}',
                                      'boxShadow': '0 4px 8px rgba(0,0,0,0.05)'})
                    ], style={
                        'backgroundColor': COLORS['card_bg'],
                        'padding': '35px',
                        'borderRadius': '20px',
                        'marginBottom': '30px',
                        'boxShadow': '0 8px 16px rgba(0,0,0,0.1)',
                        'border': f'1px solid {COLORS["border"]}',
                        'transition': 'transform 0.3s ease-in-out',
                        ':hover': {
                            'transform': 'translateY(-5px)'
                        }
                    })
                ], style={'padding': '35px'})
            ]
        ),
        dcc.Tab(
            label='Advanced Analysis',
            style={
                'backgroundColor': COLORS['background'],
                'color': COLORS['text'],
                'fontWeight': '600',
                'padding': '15px 25px',
                'borderRadius': '15px 15px 0 0',
                'border': f'1px solid {COLORS["border"]}',
                'borderBottom': 'none'
            },
            selected_style={
                'backgroundColor': COLORS['card_bg'],
                'color': COLORS['primary'],
                'fontWeight': '600',
                'padding': '15px 25px',
                'borderRadius': '15px 15px 0 0',
                'border': f'1px solid {COLORS["border"]}',
                'borderBottom': 'none',
                'boxShadow': '0 -2px 4px rgba(0,0,0,0.1)'
            },
            children=[
                html.Div([
                    # Gender Distribution Section
                    html.Div([
                        html.H2("Gender Distribution", 
                               style={'textAlign': 'center', 
                                     'color': COLORS['primary'], 
                                     'marginBottom': '25px',
                                     'fontSize': '1.8rem',
                                     'fontWeight': '600',
                                     'borderBottom': f'3px solid {COLORS["accent1"]}',
                                     'paddingBottom': '10px'}),
                        dcc.Graph(id='gender-distribution'),
                        html.Div(id='gender-distribution-interpretation',
                                style={'marginTop': '25px', 
                                      'padding': '25px', 
                                      'backgroundColor': COLORS['background'], 
                                      'borderRadius': '10px',
                                      'border': f'1px solid {COLORS["border"]}',
                                      'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'})
                    ], style={
                        'backgroundColor': COLORS['card_bg'],
                        'padding': '30px',
                        'borderRadius': '15px',
                        'marginBottom': '30px',
                        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                        'border': f'1px solid {COLORS["border"]}'
                    }),
                    
                    # Socioeconomic Analysis Section
                    html.Div([
                        html.H2("Socioeconomic Analysis", 
                               style={'textAlign': 'center', 
                                     'color': COLORS['primary'], 
                                     'marginBottom': '25px',
                                     'fontSize': '1.8rem',
                                     'fontWeight': '600',
                                     'borderBottom': f'3px solid {COLORS["accent1"]}',
                                     'paddingBottom': '10px'}),
                        dcc.Graph(id='socioeconomic-analysis'),
                        html.Div(id='socioeconomic-analysis-interpretation',
                                style={'marginTop': '25px', 
                                      'padding': '25px', 
                                      'backgroundColor': COLORS['background'], 
                                      'borderRadius': '10px',
                                      'border': f'1px solid {COLORS["border"]}',
                                      'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'})
                    ], style={
                        'backgroundColor': COLORS['card_bg'],
                        'padding': '30px',
                        'borderRadius': '15px',
                        'marginBottom': '30px',
                        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                        'border': f'1px solid {COLORS["border"]}'
                    }),
                    
                    # Technology Access Impact Section
                    html.Div([
                        html.H2("Technology Access Impact", 
                               style={'textAlign': 'center', 
                                     'color': COLORS['primary'], 
                                     'marginBottom': '25px',
                                     'fontSize': '1.8rem',
                                     'fontWeight': '600',
                                     'borderBottom': f'3px solid {COLORS["accent1"]}',
                                     'paddingBottom': '10px'}),
                        dcc.Graph(id='technology-impact'),
                        html.Div(id='technology-impact-interpretation',
                                style={'marginTop': '25px', 
                                      'padding': '25px', 
                                      'backgroundColor': COLORS['background'], 
                                      'borderRadius': '10px',
                                      'border': f'1px solid {COLORS["border"]}',
                                      'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'})
                    ], style={
                        'backgroundColor': COLORS['card_bg'],
                        'padding': '30px',
                        'borderRadius': '15px',
                        'marginBottom': '30px',
                        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                        'border': f'1px solid {COLORS["border"]}'
                    })
                ], style={'padding': '30px'})
            ]
        ),
        dcc.Tab(
            label='Deep Insights',
            style={'backgroundColor': COLORS['background'],
                   'color': COLORS['text'],
                   'fontWeight': '600',
                   'padding': '15px'},
            selected_style={'backgroundColor': 'white',
                           'borderTop': f'3px solid {COLORS["primary"]}',
                           'color': COLORS['primary'],
                           'fontWeight': '600',
                           'padding': '15px'},
            children=[
                html.Div([
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
                                style={'marginBottom': '20px'}
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
                                style={'marginBottom': '20px'}
                            )
                        ]),
                        dcc.Graph(id='background-analysis'),
                        html.Div(id='background-interpretation',
                                style={'marginTop': '20px', 'padding': '15px', 'backgroundColor': COLORS['grid'], 'borderRadius': '5px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'})
                ], style={'padding': '20px'})
            ]
        )
    ]),
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
    # Query to get yearly averages with rounded years
    query = """
    SELECT 
        CAST(SUBSTR(periodo, 1, 4) AS INTEGER) as year,
        AVG(mod_razona_cuantitat_punt) as avg_quant_reasoning,
        AVG(mod_lectura_critica_punt) as avg_critical_reading,
        AVG(mod_ingles_punt) as avg_english,
        AVG(mod_competen_ciudada_punt) as avg_citizenship,
        COUNT(*) as students
    FROM saber_pro
    GROUP BY CAST(SUBSTR(periodo, 1, 4) AS INTEGER)
    ORDER BY year
    """
    df = query_db(query)
    
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
    
    # Create figure with enhanced styling
    fig = go.Figure()
    
    # Add area fill for trend
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df[score_type],
        fill='tozeroy',
        fillcolor=f'rgba{tuple(int(COLORS["primary"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False
    ))
    
    # Add main line with enhanced styling
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df[score_type],
        mode='lines+markers+text',
        text=[f'{val:.1f}' for val in df[score_type]],
        textposition='top center',
        line=dict(
            color=COLORS['primary'],
            width=4,
            shape='spline',
            smoothing=0.3
        ),
        marker=dict(
            size=12,
            color=COLORS['primary'],
            line=dict(
                color='white',
                width=2
            ),
            symbol='circle'
        ),
        hovertemplate='<b>Year:</b> %{x}<br>' +
                      '<b>Score:</b> %{y:.1f}<br>' +
                      '<b>Students:</b> %{customdata:,}<extra></extra>',
        customdata=df['students']
    ))
    
    # Update layout with enhanced styling
    fig.update_layout(
        title=dict(
            text=f'Average {score_labels[score_type]} Score by Year',
            font=dict(
                size=24,
                color=COLORS['text'],
                family='Poppins, sans-serif'
            ),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(
                text='Year',
                font=dict(
                    size=14,
                    color=COLORS['text'],
                    family='Poppins, sans-serif'
                )
            ),
            showgrid=True,
            gridcolor=COLORS['grid'],
            gridwidth=1,
            zeroline=False,
            showline=True,
            linecolor=COLORS['border'],
            linewidth=2,
            dtick=1,  # Show every year
            tickformat='d'  # Format as whole numbers
        ),
        yaxis=dict(
            title=dict(
                text='Average Score',
                font=dict(
                    size=14,
                    color=COLORS['text'],
                    family='Poppins, sans-serif'
                )
            ),
            range=[y_min, y_max],
            showgrid=True,
            gridcolor=COLORS['grid'],
            gridwidth=1,
            zeroline=False,
            showline=True,
            linecolor=COLORS['border'],
            linewidth=2
        ),
        template='plotly_white',
        hovermode='x unified',
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=100, b=50, l=50, r=50),
        shapes=[
            # Add horizontal line for average
            dict(
                type='line',
                x0=df['year'].iloc[0],
                x1=df['year'].iloc[-1],
                y0=df[score_type].mean(),
                y1=df[score_type].mean(),
                line=dict(
                    color=COLORS['accent1'],
                    width=2,
                    dash='dash'
                )
            )
        ],
        annotations=[
            # Add average line label
            dict(
                x=df['year'].iloc[-1],
                y=df[score_type].mean(),
                xref='x',
                yref='y',
                text=f'Average: {df[score_type].mean():.1f}',
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=COLORS['accent1'],
                ax=50,
                ay=-30,
                font=dict(
                    size=12,
                    color=COLORS['text_light']
                )
            )
        ]
    )
    
    # Generate interpretation with enhanced styling
    latest_score = df[score_type].iloc[-1]
    first_score = df[score_type].iloc[0]
    pct_change = ((latest_score - first_score) / first_score) * 100
    trend = "increased" if pct_change > 0 else "decreased"
    
    interpretation = html.Div([
        html.H3("Key Insights:", 
                className='animate__animated animate__fadeIn',
                style={'marginBottom': '20px', 
                       'color': COLORS['text'],
                       'fontSize': '1.4rem',
                       'fontWeight': '600',
                       'fontFamily': 'Poppins, sans-serif',
                       'borderBottom': f'2px solid {COLORS["accent1"]}',
                       'paddingBottom': '10px'}),
        html.Ul([
            html.Li(
                [html.Strong("Score Trend: "), 
                 f"The average {score_labels[score_type].lower()} score {trend} by {abs(pct_change):.1f}% from {first_score:.1f} to {latest_score:.1f} between {df['year'].iloc[0]} and {df['year'].iloc[-1]}."],
                className='animate__animated animate__fadeIn animate__delay-1s',
                style={'marginBottom': '12px', 'lineHeight': '1.6'}
            ),
            html.Li(
                [html.Strong("Highest Performance: "), 
                 f"{df[score_type].max():.1f} points ({df.loc[df[score_type].idxmax(), 'year']})"],
                className='animate__animated animate__fadeIn animate__delay-2s',
                style={'marginBottom': '12px', 'lineHeight': '1.6'}
            ),
            html.Li(
                [html.Strong("Lowest Performance: "), 
                 f"{df[score_type].min():.1f} points ({df.loc[df[score_type].idxmin(), 'year']})"],
                className='animate__animated animate__fadeIn animate__delay-3s',
                style={'marginBottom': '12px', 'lineHeight': '1.6'}
            ),
            html.Li(
                [html.Strong("Student Participation: "), 
                 f"Average of {df['students'].mean():,.0f} students per period"],
                className='animate__animated animate__fadeIn animate__delay-4s',
                style={'marginBottom': '12px', 'lineHeight': '1.6'}
            )
        ], style={
            'listStyleType': 'none',
            'padding': '0',
            'fontSize': '1.1rem',
            'color': COLORS['text'],
            'fontFamily': 'Poppins, sans-serif'
        })
    ])
    
    return fig, interpretation

@app.callback(
    [Output('gender-distribution', 'figure'),
     Output('gender-distribution-interpretation', 'children')],
    [Input('gender-distribution', 'id')]
)
def update_gender_distribution(_):
    # Query to get gender distribution and scores by year with rounded years
    query = """
    SELECT 
        CAST(SUBSTR(periodo, 1, 4) AS INTEGER) as year,
        estu_genero as gender,
        COUNT(*) as student_count,
        AVG((mod_razona_cuantitat_punt + mod_lectura_critica_punt + 
             mod_ingles_punt + mod_competen_ciudada_punt)/4.0) as avg_score
    FROM saber_pro
    GROUP BY CAST(SUBSTR(periodo, 1, 4) AS INTEGER), estu_genero
    ORDER BY year, estu_genero
    """
    df = query_db(query)
    
    # Calculate y-axis range for counts
    y_min = 0
    y_max = df['student_count'].max() * 1.15
    
    # Create figure
    fig = go.Figure()
    
    for gender, color in [('F', '#E91E63'), ('M', '#1976D2')]:
        gender_data = df[df['gender'] == gender]
        
        fig.add_trace(go.Bar(
            name='Female' if gender == 'F' else 'Male',
            x=gender_data['year'],
            y=gender_data['student_count'],
            text=[f'{count:,}<br>({score:.1f})' for count, score in 
                  zip(gender_data['student_count'], gender_data['avg_score'])],
            textposition='auto',
            marker_color=color
        ))
    
    fig.update_layout(
        title=dict(
            text='Gender Distribution and Average Score by Year',
            font=dict(size=24, color=COLORS['primary'], family='Roboto'),
            x=0.5,
            y=0.95
        ),
        xaxis_title=dict(text='Year', font=dict(size=14, color=COLORS['text'])),
        yaxis_title=dict(text='Number of Students', font=dict(size=14, color=COLORS['text'])),
        barmode='group',
        template='plotly_white',
        hovermode='x unified',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor='white',
        font=dict(family='Roboto', color=COLORS['text']),
        yaxis=dict(
            range=[y_min, y_max],
            tickformat=',d',
            gridcolor=COLORS['grid'],
            zerolinecolor=COLORS['border']
        ),
        xaxis=dict(
            gridcolor=COLORS['grid'],
            zerolinecolor=COLORS['border'],
            dtick=1,  # Show every year
            tickformat='d'  # Format as whole numbers
        ),
        margin=dict(t=100, b=50, l=50, r=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Generate interpretation with enhanced styling
    latest_year = df['year'].max()
    latest_data = df[df['year'] == latest_year]
    total_students = latest_data['student_count'].sum()
    female_pct = latest_data[latest_data['gender'] == 'F']['student_count'].iloc[0] / total_students * 100
    male_pct = latest_data[latest_data['gender'] == 'M']['student_count'].iloc[0] / total_students * 100
    
    avg_score_diff = latest_data[latest_data['gender'] == 'F']['avg_score'].iloc[0] - \
                    latest_data[latest_data['gender'] == 'M']['avg_score'].iloc[0]
    
    interpretation = html.Div([
        html.H3("Key Insights:", 
                style={'marginBottom': '20px', 
                       'color': COLORS['primary'],
                       'fontSize': '1.4rem',
                       'fontWeight': '600',
                       'borderBottom': f'2px solid {COLORS["accent1"]}',
                       'paddingBottom': '10px'}),
        html.Ul([
            html.Li(
                [html.Strong("Current Distribution: "), 
                 f"In {latest_year}, the gender distribution was {female_pct:.1f}% female and {male_pct:.1f}% male."],
                style={'marginBottom': '12px', 'lineHeight': '1.6'}
            ),
            html.Li(
                [html.Strong("Performance Gap: "), 
                 f"The average score difference between female and male students is {abs(avg_score_diff):.1f} points, with {'female' if avg_score_diff > 0 else 'male'} students scoring higher."],
                style={'marginBottom': '12px', 'lineHeight': '1.6'}
            ),
            html.Li(
                [html.Strong("Total Participation: "), 
                 f"In {latest_year}, {total_students:,} students participated in the assessment."],
                style={'marginBottom': '12px', 'lineHeight': '1.6'}
            )
        ], style={
            'listStyleType': 'none',
            'padding': '0',
            'fontSize': '1.1rem',
            'color': COLORS['text']
        })
    ])
    
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
        COUNT(*) as student_count
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
              zip(df['avg_score'], df['student_count'])],
        textposition='auto',
        marker_color=COLORS['primary']
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
        )
    )
    
    # Generate interpretation
    score_range = df['avg_score'].max() - df['avg_score'].min()
    total_students = df['student_count'].sum()
    most_common_stratum = df.loc[df['student_count'].idxmax(), 'stratum']
    most_common_pct = df['student_count'].max() / total_students * 100
    
    interpretation = html.Div([
        html.H3("Key Insights:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li(f"There is a {score_range:.1f} point difference between the highest and lowest scoring strata."),
            html.Li(f"The most common socioeconomic level is {most_common_stratum} ({most_common_pct:.1f}% of students)."),
            html.Li(f"Higher strata consistently show higher average scores, suggesting a correlation between socioeconomic status and academic performance."),
            html.Li(f"Total number of students across all strata: {total_students:,}")
        ])
    ])
    
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
        COUNT(*) as student_count
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
                counts.append(df[mask]['student_count'].iloc[0])
    
    # Calculate y-axis range
    y_min = min(scores) * 0.95
    y_max = max(scores) * 1.05
    
    fig.add_trace(go.Bar(
        x=categories,
        y=scores,
        text=[f'{score:.1f}<br>({count:,})' for score, count in zip(scores, counts)],
        textposition='auto',
        marker_color=COLORS['primary']
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
        )
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
    ])
    
    return fig, interpretation

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
            COUNT(*) as student_count
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
            COUNT(*) as student_count
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
            COUNT(*) as student_count
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
        colorscale='RdYlBu',
        reversescale=True
    ))
    
    fig.update_layout(
        title=f'Performance Gaps by {factor.replace("_", " ").title()}',
        template='plotly_white',
        height=400
    )
    
    # Calculate insights
    max_gap = values.max() - values.min()
    max_gap_subject = subjects[np.argmax(np.ptp(values, axis=0))]
    total_students = df['student_count'].sum()
    
    interpretation = html.Div([
        html.H3("Gap Analysis:", style={'marginBottom': '10px'}),
        html.Ul([
            html.Li(f"Maximum performance gap: {max_gap:.1f} points"),
            html.Li(f"Largest gap observed in: {max_gap_subject}"),
            html.Li(f"Total students analyzed: {total_students:,}"),
            html.Li([
                html.Strong("Distribution: "),
                ", ".join([f"{cat}: {count:,} students ({count/total_students*100:.1f}%)" 
                          for cat, count in zip(categories, df['student_count'])])
            ])
        ])
    ])
    
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
        COUNT(*) as student_count
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
        colorscale='RdYlBu'
    ))
    
    fig.update_layout(
        title='Score by Parents\' Education Level',
        xaxis_title='Father\'s Education',
        yaxis_title='Mother\'s Education',
        template='plotly_white',
        height=600,
        xaxis={'tickangle': 45}
    )
    
    # Calculate insights
    max_score = df['avg_score'].max()
    min_score = df['avg_score'].min()
    score_range = max_score - min_score
    total_students = df['student_count'].sum()
    
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
            html.Li("Mother's education level shows slightly stronger correlation with performance")
        ])
    ])
    
    return fig, interpretation

if __name__ == '__main__':
    # Development server
    app.run_server(debug=False, host='0.0.0.0', port=8051) 