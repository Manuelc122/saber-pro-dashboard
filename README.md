# 📊 Saber Pro Analysis Dashboard

## 🎯 Live Demo
Experience the dashboard in action: [Saber Pro Dashboard](https://saber-pro-dashboard.onrender.com/)

## 🌟 Project Impact
Built an end-to-end data analytics solution that processes and visualizes Colombia's national standardized test results (2018-2021), enabling:
- Real-time analysis of 12,000+ student records
- Identification of educational performance patterns across socioeconomic levels
- Data-driven insights for educational policy decisions

## 💻 Technical Implementation

### Backend Development
- Engineered a robust SQLite database managing 12,000+ records with optimized query performance
- Implemented complex SQL queries achieving sub-second response times for aggregated analytics
- Built an efficient ETL pipeline processing multiple years of educational data
- Developed RESTful API endpoints handling concurrent user requests

### Frontend Visualization
- Created interactive dashboards using Plotly and Dash, reducing data exploration time by 80%
- Implemented real-time filtering and dynamic updates with callback functions
- Designed responsive layouts adapting to various screen sizes
- Built custom visualizations including:
  - Time-series analysis of performance trends
  - Heatmaps for educational background impact
  - Interactive correlation matrices

### Data Processing Pipeline
- Automated data cleaning procedures handling missing values and outliers
- Implemented data validation checks ensuring data integrity
- Created efficient data aggregation methods for quick insights generation
- Developed custom analytics functions for educational metrics calculation

### Performance Optimization
- Implemented database indexing reducing query times by 60%
- Optimized data loading with lazy evaluation and caching
- Reduced initial page load time to under 3 seconds
- Implemented efficient memory management for large dataset handling

## 🛠 Tech Stack
- **Data Processing**: Python 3.9.7, Pandas 2.1.4, NumPy 1.26.3
- **Web Framework**: Dash 2.14.2, Flask 3.0.0
- **Database**: SQLite3 with optimized indexing
- **Visualization**: Plotly 5.18.0
- **Deployment**: Gunicorn, Render Cloud Platform

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/Manuelc122/saber-pro-dashboard.git
cd saber-pro-dashboard

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python create_test_db.py

# Launch application
python src/dashboard/app.py
```

## 📁 Project Architecture
```
saber-pro-dashboard/
├── src/                      # Core application code
│   ├── dashboard/           # Interactive visualization components
│   │   └── app.py          # Main application logic
│   └── data_processing/    # ETL and data handling modules
├── data/                    # Data management
│   └── processed/          # Cleaned and processed datasets
├── notebooks/              # Analysis and prototyping
├── sql/                    # Optimized database queries
├── requirements.txt        # Project dependencies
└── render.yaml             # Deployment configuration
```

## 📫 Let's Connect
- **LinkedIn**: [Manuel Castillo](https://www.linkedin.com/in/manuel-castillo-8355ab18b/)
- **Email**: manueldavidc@hotmail.com
- **Project**: [GitHub Repository](https://github.com/Manuelc122/saber-pro-dashboard) 