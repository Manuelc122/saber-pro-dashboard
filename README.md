# Saber Pro Analysis Dashboard

## Overview
A comprehensive dashboard for analyzing Colombia's Saber Pro test results from 2018-2021. This dashboard provides insights into student performance patterns, socioeconomic impacts, and educational gaps across different demographics.

## Features
- **Basic Analysis**: Performance trends, gender distribution, and socioeconomic factors
- **Advanced Analysis**: Statistical analysis of score distributions and correlations
- **Deep Insights**: Performance gaps and educational background impact analysis

## Technology Stack
- Python 3.9.7
- Dash 2.14.2
- Plotly 5.18.0
- SQLite3
- Additional dependencies in requirements.txt

## Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/saber-pro-dashboard.git
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

## Project Structure
```
saber-pro-dashboard/
├── src/
│   ├── dashboard/
│   │   └── app.py
│   └── data_processing/
│       └── __init__.py
├── data/
│   └── processed/
│       └── saber_pro.db
├── notebooks/
├── sql/
├── requirements.txt
├── render.yaml
├── README.md
└── .gitignore
```

## Deployment
### Render Deployment
1. Fork/Clone this repository
2. Connect your GitHub repository to Render
3. Create a new Web Service
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn src.dashboard.app:server`

### Environment Variables
Required environment variables in Render:
- PYTHON_VERSION: 3.9.7
- PYTHONPATH: .

## Data Sources
The dashboard uses a test database that simulates the Saber Pro test results with:
- 2,000 records per socioeconomic stratum
- Realistic correlations between variables
- Data spanning from 2018 to 2021

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
Your Name - your.email@example.com
Project Link: https://github.com/yourusername/saber-pro-dashboard 