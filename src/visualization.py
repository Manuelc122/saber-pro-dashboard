import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List

class SaberProVisualizer:
    def __init__(self, df):
        self.df = df
        
    def plot_score_distributions(self, save_path: str = None):
        """Plot distribution of all score columns"""
        score_columns = [
            'MOD_RAZONA_CUANTITAT_PUNT',
            'MOD_COMUNI_ESCRITA_PUNT',
            'MOD_LECTURA_CRITICA_PUNT',
            'MOD_INGLES_PUNT',
            'MOD_COMPETEN_CIUDADA_PUNT'
        ]
        
        fig = go.Figure()
        for col in score_columns:
            fig.add_trace(go.Histogram(
                x=self.df[col],
                name=col,
                opacity=0.7
            ))
            
        fig.update_layout(
            title='Distribution of Scores Across Different Modules',
            xaxis_title='Score',
            yaxis_title='Count',
            barmode='overlay'
        )
        
        if save_path:
            fig.write_html(save_path)
        return fig
    
    def plot_scores_by_region(self, module: str):
        """Plot average scores by department"""
        avg_scores = self.df.groupby('ESTU_DEPTO_PRESENTACION')[module].mean()
        
        fig = px.choropleth(
            avg_scores,
            locations=avg_scores.index,
            color=module,
            title=f'Average {module} Scores by Department',
            scope="south america"
        )
        return fig
    
    def plot_correlation_matrix(self):
        """Plot correlation matrix for numerical columns"""
        score_columns = [
            'MOD_RAZONA_CUANTITAT_PUNT',
            'MOD_COMUNI_ESCRITA_PUNT',
            'MOD_LECTURA_CRITICA_PUNT',
            'MOD_INGLES_PUNT',
            'MOD_COMPETEN_CIUDADA_PUNT'
        ]
        
        corr_matrix = self.df[score_columns].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            corr_matrix, 
            annot=True, 
            cmap='coolwarm', 
            center=0
        )
        plt.title('Correlation Matrix of Test Scores')
        return plt 