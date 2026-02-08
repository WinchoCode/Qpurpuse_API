from setuptools import setup, find_packages

setup(
    name="qpurpose-api",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "flask",
        "flask-restful",
        "flask-sqlalchemy",
        "flask-jwt-extended",
        "flask-cors",
        "python-dotenv",
        "werkzeug",
    ],
)