from setuptools import setup, find_packages

setup(
    name="rec_chart_ocr",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.4.0",
        "pytesseract>=0.3.10",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "mss>=9.0.1",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.0",
    ],
    python_requires=">=3.8",
) 