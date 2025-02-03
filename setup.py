from setuptools import setup, find_packages

setup(
    name="saber_pro",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "dash",
        "plotly",
        "pandas",
        "numpy",
        "gunicorn"
    ],
) 