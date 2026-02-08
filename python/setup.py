"""
Setup script for rotational_unfolding package.

Install:
    pip install -e .

Usage after install:
    python -m rotational_unfolding run --poly archimedean/s05 --out outputs/
"""

from setuptools import setup, find_packages

setup(
    name="rotational_unfolding",
    version="0.1.0",
    description="Phase 1 CLI for rotational unfolding algorithm",
    author="Research Project",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies for Phase 1 (uses only stdlib)
    ],
    entry_points={
        "console_scripts": [
            "rotational-unfolding=rotational_unfolding.cli:main",
        ],
    },
)
