#!/usr/bin/env python3
"""
Setup script for the Neo4j MCP server.
"""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="neo4j-mcp",
        version="0.1.0",
        description="Neo4j MCP Server - A Model Context Protocol server for Neo4j database operations",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        author="dleblancjr",
        author_email="dleblancjr@gmail.com",
        url="https://github.com/dleblancjr/neo4j-mcp",
        packages=find_packages(),
        python_requires=">=3.13",
        install_requires=[
            "mcp>=1.12.4,<2.0.0",
            "neo4j>=5.28.2,<6.0.0",
            "python-dotenv>=1.0.0,<2.0.0",
        ],
        entry_points={
            "console_scripts": [
                "neo4j-mcp=neo4j_mcp.server:main",
            ],
        },
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.13",
        ],
    )