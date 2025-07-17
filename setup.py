#!/usr/bin/env python3
"""
AI Wiki - Auto-generate browsable Django REST API documentation
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aiwiki",
    version="1.0.0",
    author="AI Wiki Team",
    description="Auto-generate a browsable, searchable technical wiki from your Django REST codebase using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
        "djangorestframework>=3.12",
        "Flask>=2.0",
        "markdown2>=2.4",
        "requests>=2.25",
    ],
    entry_points={
        "console_scripts": [
            "aiwiki=aiwiki.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
