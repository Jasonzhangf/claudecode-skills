#!/usr/bin/env python3
"""
Sysmem - 项目架构链条化管理系统
自动化项目架构管理工具
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="sysmem",
    version="2.0.0",
    author="Sysmem Team",
    author_email="sysmem@example.com",
    description="项目架构链条化管理系统",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/example/sysmem",
    py_modules=["utils"],
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Documentation",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pathlib",
        "jsonschema>=3.0",
        "click>=8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "sysmem=sysmem.cli:main",
            "sysmem-collect=sysmem.scripts.collect_data:main",
            "sysmem-scan=sysmem.scripts.scan_project:main",
            "sysmem-analyze=sysmem.scripts.analyze_architecture:main",
            "sysmem-update=sysmem.scripts.update_claude_md:main",
            "sysmem-monitor=sysmem.scripts.system_monitor:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sysmem": [
            "references/*.md",
            "assets/*.json",
            "examples/**/*.md",
            "scripts/*.py",
        ],
    },
    zip_safe=False,
)