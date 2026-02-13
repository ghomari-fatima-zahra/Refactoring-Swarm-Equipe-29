from setuptools import setup, find_packages

setup(
    name="refactoring-swarm",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'google-generativeai>=0.8.3',
        'python-dotenv>=1.0.1',
        'pytest>=8.3.0',
        'httpx>=0.27.2',
    ],
)