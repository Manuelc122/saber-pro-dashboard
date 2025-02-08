# 📊 Saber Pro Analysis Dashboard

## 🎯 Overview
An advanced analytics dashboard that provides deep insights into Colombia's national standardized test (Saber Pro) results from 2018-2021. This project demonstrates my expertise in data analysis, visualization, and full-stack development, showcasing the ability to transform complex educational data into actionable insights.

## 🌟 Key Features

### 📈 Basic Analysis
- **Performance Trends**: Interactive time-series analysis of test scores with year-over-year comparisons
- **Gender Distribution**: Detailed analysis of gender-based performance patterns
- **Socioeconomic Impact**: Visual correlation between socioeconomic factors and academic performance

### 📊 Advanced Analysis
- **Statistical Distributions**: Comprehensive statistical analysis of score distributions
- **Correlation Studies**: Multi-factor correlation analysis between different variables
- **Technology Impact**: Analysis of how technology access affects student performance

### 🔍 Deep Insights
- **Performance Gap Analysis**: Sophisticated analysis of educational gaps across different demographics
- **Educational Background Impact**: Interactive heatmaps showing parental education influence
- **Socioeconomic Patterns**: Advanced visualization of socioeconomic impacts on academic performance

## 💻 Technical Highlights

### 🛠 Technology Stack
- **Frontend**: Dash 2.14.2, HTML/CSS with modern UI/UX principles
- **Backend**: Python 3.9.7, Flask 3.0.0
- **Data Processing**: Pandas 2.1.4, NumPy 1.26.3
- **Visualization**: Plotly 5.18.0
- **Database**: SQLite3 with optimized queries
- **Deployment**: Production-grade setup with Gunicorn

### 🏗 Architecture Features
- **Modular Design**: Clean, maintainable code structure
- **Responsive UI**: Mobile-friendly dashboard layout
- **Optimized Performance**: Efficient data processing and caching
- **Production-Ready**: Enterprise-level deployment configuration

## 📱 User Interface
The dashboard features a modern, intuitive interface with:
- Animated transitions and interactive elements
- Responsive design for all device sizes
- Clear data visualization with insightful tooltips
- User-friendly controls and filters

## 🔧 Technical Implementation

### Data Processing
- Efficient ETL pipeline for data preparation
- Advanced SQL queries for complex analytics
- Optimized database schema for performance

### Visualization
- Interactive Plotly graphs with custom styling
- Dynamic updates and real-time filtering
- Comprehensive tooltips and annotations

### Code Quality
- PEP 8 compliant Python code
- Comprehensive error handling
- Detailed code documentation

## 🚀 Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Manuelc122/saber-pro-dashboard.git
   cd saber-pro-dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the test database:
   ```bash
   python create_test_db.py
   ```

5. Run the development server:
   ```bash
   python src/dashboard/app.py
   ```

## 📁 Project Structure
```
saber-pro-dashboard/
├── src/                      # Source code
│   ├── dashboard/           # Dashboard components
│   │   └── app.py          # Main application
│   └── data_processing/    # Data processing modules
├── data/                    # Data directory
│   └── processed/          # Processed data files
├── notebooks/              # Analysis notebooks
├── sql/                    # SQL queries
├── requirements.txt        # Dependencies
├── render.yaml             # Deployment config
└── README.md              # Documentation
```

## 🌐 Deployment
The dashboard is deployed using Render's cloud platform, demonstrating:
- CI/CD pipeline implementation
- Production-grade server configuration
- Environment variable management
- Performance optimization

## 💡 Skills Demonstrated
- **Data Analysis**: Advanced statistical analysis and pattern recognition
- **Data Visualization**: Complex data representation through interactive visualizations
- **Full-Stack Development**: End-to-end application development
- **Cloud Deployment**: Production-level application deployment
- **Database Design**: Efficient database schema and query optimization
- **UI/UX Design**: Modern, user-friendly interface design

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📫 Contact
Manuel Castillo - manueldavidc@hotmail.com

Portfolio: [Your Portfolio URL]
LinkedIn: [Your LinkedIn URL]
Project Link: https://github.com/Manuelc122/saber-pro-dashboard

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details. 