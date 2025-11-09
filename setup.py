"""
Setup script for Crono Ders Takip Sistemi
For creating executable with PyInstaller
"""

from setuptools import setup, find_packages
import os

# Read version from src/__init__.py
version = "1.0.0"

setup(
    name="crono-ders-takip",
    version=version,
    description="Crono Ders Takip Sistemi - Professional Study Tracking System",
    author="Chaster",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "customtkinter>=5.2.0",
        "matplotlib>=3.7.0",
    ],
    python_requires=">=3.8",
)

