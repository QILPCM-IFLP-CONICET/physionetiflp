from setuptools import find_packages, setup

setup(
    name="physionetiflp",
    version="0.1.0",
    author="Juan Mauricio Matera",
    author_email="matera@fisica.unlp.edu.ar",
    description="A Python package for accesing physionet data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/physionetiflp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        # List your dependencies here, e.g.:
        "numpy>=1.21.0",
        "pandas",
        # 'scipy>=1.7.0',
    ],
    include_package_data=True,  # Ensures package data is included
    package_data={
        "physionet": ["data/*.pcl"],  # Ensures the data file is included
    },
)
