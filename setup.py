from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-ai-wiki",
    version="0.1.0",
    author="AI Wiki Team",
    author_email="team@aiwiki.dev",
    description="Auto-generate a browsable, searchable technical wiki from your Django REST codebase using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/django-ai-wiki",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=2.0.0",
        "markdown2>=2.4.0",
        "openai>=0.27.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aiwiki=aiwiki.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "aiwiki": [
            "templates/*.html",
            "static/*",
        ],
    },
)
