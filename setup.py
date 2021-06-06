"""
Setup file for building binaries
"""
from setuptools import setup, find_packages

setup(name='RentalManager',
    version='1.0',
    packages=find_packages(include=['RentalManager', 'RentalManager.*']),
    classifiers=[
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    ]
    )
