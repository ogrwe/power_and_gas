from setuptools import setup, find_packages

setup(
    name="dremio",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "python-dotenv"
    ],
    author="Otto Geupel",
    author_email="otto.geupel@example.com",
    description="Dremio client for RWE. Used to connect dremio direct to IDE for easier development",
    keywords="dremio, client, data",
    python_requires='>=3.7',
)
