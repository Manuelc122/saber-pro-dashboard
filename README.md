# Saber Pro Analysis Dashboard

An interactive dashboard for analyzing Colombia's Saber Pro standardized test results from 2018-2021. The dashboard provides insights into student performance, socioeconomic factors, and educational trends.

## Features

- **Basic Analysis**
  - Yearly Performance Trends
  - Gender Distribution Analysis
  - Socioeconomic Impact Analysis
  - Technology Access Impact

- **Advanced Analysis**
  - Score Distribution Analysis
  - Multivariate Performance Analysis
  - Performance Patterns

- **Deep Insights**
  - Performance Gap Analysis
  - Educational Background Impact
  - Temporal Performance Patterns

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/saber-pro-dashboard.git
cd saber-pro-dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv .myenv
source .myenv/bin/activate  # On Windows: .myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python create_test_db.py
```

5. Run the dashboard:
```bash
python src/dashboard/app.py
```

The dashboard will be available at `http://localhost:8051`

## Data Description

The dashboard uses a sample of 10,000 records from the Saber Pro test results (2018-2021), including:
- Test scores in four components
- Student demographics
- Socioeconomic information
- Technology access data

## Project Structure

```
saber-pro-dashboard/
├── src/
│   ├── dashboard/
│   │   └── app.py
│   └── data_processing/
│       └── __init__.py
├── data/
│   └── saber_pro.db
├── requirements.txt
├── create_test_db.py
└── README.md
```

## Technologies Used

- Python 3.8+
- Dash
- Plotly
- Pandas
- SQLite

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Your Name

## Acknowledgments

- Data provided by ICFES (Instituto Colombiano para la Evaluación de la Educación) 