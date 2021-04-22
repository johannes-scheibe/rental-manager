"""
Setup file for building binaries
"""
from setuptools import setup, find_packages

setup(name='rental_manager',
    version='1.0',
    packages=find_packages(include=['rental_manager', 'rental_manager.*']),
    classifiers=[
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    ]
    ,
    python_requires='>=3.6',
    )