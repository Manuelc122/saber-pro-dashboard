from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
from pathlib import Path
import os
from plotly.subplots import make_subplots

# Initialize the Dash app
app = Dash(__name__, 
    external_stylesheets=[
        'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap'
    ]
)

# Expose the server variable for Gunicorn
server = app.server

# Determine the correct database path
if os.environ.get('RENDER'):
    # Production path on Render
    DB_PATH = Path('/opt/render/project/src/data/processed/saber_pro.db').resolve()
else:
    # Development path - relative to this file
    DB_PATH = Path(__file__).parent.parent / 'data' / 'processed' / 'saber_pro.db'

print(f"Using database path: {DB_PATH}")

def query_db(query, params=None):
    """Execute a query and return results as a DataFrame."""
    try:
        if not DB_PATH.exists():
            print(f"Database not found at: {DB_PATH}")
            return pd.DataFrame()
            
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"Database error: {str(e)}")
        return pd.DataFrame()

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
    
    # Gender Colors
    'gender_f': '#ff69b4',      # Pink for female
    'gender_m': '#4169e1'       # Blue for male
}

def handle_empty_data(df, error_message="No data available"):
    """Create an empty figure with an error message."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=error_message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            template='plotly_white',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig

@app.callback(
    [Output('yearly-performance', 'figure'),
     Output('yearly-performance-interpretation', 'children')],
    [Input('score-type', 'value')]
)
def update_yearly_performance(score_type):
    try:
        # Query to get yearly averages
        query = """
        SELECT 
            periodo,
            AVG(mod_razona_cuantitat_punt) as avg_quant_reasoning,
            AVG(mod_lectura_critica_punt) as avg_critical_reading,
            AVG(mod_ingles_punt) as avg_english,
            AVG(mod_competen_ciudada_punt) as avg_citizenship,
            COUNT(*) as students
        FROM saber_pro
        GROUP BY periodo
        ORDER BY periodo
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
            x=df['periodo'],
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
        
        interpretation = f"""
        From {df['periodo'].iloc[0]} to {df['periodo'].iloc[-1]}, the average {score_labels[score_type]} score has 
        {trend} by {abs(pct_change):.1f}%. The latest average score is {latest_score:.1f}.
        """
        
        return fig, interpretation
    except Exception as e:
        print(f"Error in yearly performance: {str(e)}")
        return handle_empty_data(pd.DataFrame(), "Error generating yearly performance"), "Error in analysis"

@app.callback(
    [Output('gender-distribution', 'figure'),
     Output('gender-distribution-interpretation', 'children')],
    [Input('score-type', 'value')]
)
def update_gender_distribution(score_type):
    try:
        # Query to get gender-based averages by period
        query = """
        SELECT 
            periodo,
            estu_genero,
            AVG(mod_razona_cuantitat_punt) as avg_quant_reasoning,
            AVG(mod_lectura_critica_punt) as avg_critical_reading,
            AVG(mod_ingles_punt) as avg_english,
            AVG(mod_competen_ciudada_punt) as avg_citizenship,
            COUNT(*) as students
        FROM saber_pro
        GROUP BY periodo, estu_genero
        ORDER BY periodo, estu_genero
        """
        df = query_db(query)
        
        # Check for empty data
        error_fig = handle_empty_data(df)
        if error_fig:
            return error_fig, "No data available for gender analysis"
        
        # Score type labels
        score_labels = {
            'avg_quant_reasoning': 'Quantitative Reasoning',
            'avg_critical_reading': 'Critical Reading',
            'avg_english': 'English',
            'avg_citizenship': 'Citizenship Skills'
        }
        
        # Create figure
        fig = go.Figure()
        
        for gender in ['F', 'M']:
            gender_df = df[df['estu_genero'] == gender]
            color = COLORS['gender_f'] if gender == 'F' else COLORS['gender_m']
            gender_label = 'Female' if gender == 'F' else 'Male'
            
            fig.add_trace(go.Scatter(
                x=gender_df['periodo'],
                y=gender_df[score_type],
                name=gender_label,
                mode='lines+markers',
                line=dict(color=color, width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title=f'Gender Comparison: {score_labels[score_type]} Scores',
            xaxis_title='Year',
            yaxis_title='Average Score',
            template='plotly_white',
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=COLORS['text'])
        )
        
        # Generate interpretation
        latest_period = df['periodo'].max()
        latest_data = df[df['periodo'] == latest_period]
        female_score = latest_data[latest_data['estu_genero'] == 'F'][score_type].iloc[0]
        male_score = latest_data[latest_data['estu_genero'] == 'M'][score_type].iloc[0]
        diff = female_score - male_score
        
        interpretation = f"""
        In the most recent period ({latest_period}), female students scored {abs(diff):.1f} points 
        {'higher' if diff > 0 else 'lower'} than male students in {score_labels[score_type]}.
        """
        
        return fig, interpretation
        
    except Exception as e:
        print(f"Error in gender distribution: {str(e)}")
        return handle_empty_data(pd.DataFrame(), "Error generating gender distribution"), "Error in analysis"

@app.callback(
    [Output('temporal-patterns', 'figure'),
     Output('temporal-interpretation', 'children')],
    [Input('score-type', 'value')]
)
def update_temporal_patterns(score_type):
    try:
        # Query to get performance metrics by period
        query = """
        SELECT 
            periodo,
            AVG(mod_razona_cuantitat_punt) as avg_quant_reasoning,
            AVG(mod_lectura_critica_punt) as avg_critical_reading,
            AVG(mod_ingles_punt) as avg_english,
            AVG(mod_competen_ciudada_punt) as avg_citizenship,
            COUNT(*) as students
        FROM saber_pro
        GROUP BY periodo
        ORDER BY periodo
        """
        df = query_db(query)
        
        # Check for empty data
        error_fig = handle_empty_data(df)
        if error_fig:
            return error_fig, "No data available for temporal analysis"
        
        # Score type labels
        score_labels = {
            'avg_quant_reasoning': 'Quantitative Reasoning',
            'avg_critical_reading': 'Critical Reading',
            'avg_english': 'English',
            'avg_citizenship': 'Citizenship Skills'
        }
        
        # Create subplots
        fig = make_subplots(rows=2, cols=1,
                           subplot_titles=('Score Trend', 'Student Count'),
                           vertical_spacing=0.15)
        
        # Add score trend
        fig.add_trace(
            go.Scatter(
                x=df['periodo'],
                y=df[score_type],
                mode='lines+markers',
                name='Average Score',
                line=dict(color=COLORS['viz_primary'], width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Add student count
        fig.add_trace(
            go.Bar(
                x=df['periodo'],
                y=df['students'],
                name='Number of Students',
                marker_color=COLORS['viz_secondary']
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f'Temporal Analysis: {score_labels[score_type]}',
            template='plotly_white',
            height=800,
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=COLORS['text'])
        )
        
        # Update axes labels
        fig.update_xaxes(title_text='Period', row=2, col=1)
        fig.update_yaxes(title_text='Average Score', row=1, col=1)
        fig.update_yaxes(title_text='Number of Students', row=2, col=1)
        
        # Generate interpretation
        score_trend = df[score_type].iloc[-1] - df[score_type].iloc[0]
        student_trend = df['students'].iloc[-1] - df['students'].iloc[0]
        
        interpretation = f"""
        Over the analyzed period, {score_labels[score_type]} scores have 
        {'increased' if score_trend > 0 else 'decreased'} by {abs(score_trend):.1f} points.
        The number of test takers has {'increased' if student_trend > 0 else 'decreased'} 
        by {abs(student_trend)} students.
        """
        
        return fig, interpretation
        
    except Exception as e:
        print(f"Error in temporal patterns: {str(e)}")
        return handle_empty_data(pd.DataFrame(), "Error generating temporal patterns"), "Error in analysis"

# App Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('Saber Pro Analysis Dashboard', 
                style={'textAlign': 'center', 'color': COLORS['text'], 'marginBottom': '30px'})
    ], style={'marginBottom': '40px', 'backgroundColor': COLORS['card_background'], 'padding': '20px'}),
    
    # Main Content
    html.Div([
        # Yearly Performance Section
        html.Div([
            html.H2('Yearly Performance Analysis', 
                    style={'color': COLORS['text'], 'marginBottom': '20px'}),
            dcc.Dropdown(
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
            dcc.Graph(id='yearly-performance'),
            html.Div(id='yearly-performance-interpretation')
        ], style={'backgroundColor': COLORS['background'], 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '40px'}),
        
        # Gender Distribution Section
        html.Div([
            html.H2('Gender Distribution Analysis', 
                    style={'color': COLORS['text'], 'marginBottom': '20px'}),
            dcc.Graph(id='gender-distribution'),
            html.Div(id='gender-distribution-interpretation')
        ], style={'backgroundColor': COLORS['background'], 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '40px'}),
        
        # Temporal Patterns Section
        html.Div([
            html.H2('Temporal Performance Patterns', 
                    style={'color': COLORS['text'], 'marginBottom': '20px'}),
            dcc.Graph(id='temporal-patterns'),
            html.Div(id='temporal-interpretation')
        ], style={'backgroundColor': COLORS['background'], 'padding': '20px', 'borderRadius': '10px'})
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '0 20px'})
], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'paddingBottom': '40px'})

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
