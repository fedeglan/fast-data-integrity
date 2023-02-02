import os
from distutils.core import setup

from setuptools import find_packages

# Optional project description in README.md:
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(
        os.path.join(current_directory, "README.md"), encoding="utf-8"
    ) as f:
        long_description = f.read()
except Exception:
    long_description = ""

# Requirements.txt
with open(
    os.path.join(current_directory, "requirements.txt"), encoding="utf-8"
) as f:
    requirements_list = f.read()

# License file
try:
    with open(
    os.path.join(current_directory, "LICENSE"), encoding="utf-8"
    ) as f:
        license_file = f.read()
except:
    license_file = "None."


setup(
    # Project name:
    name = 'fastDataIntegrity',
    # Packages to include in the distribution:
    packages = find_packages('fastDataIntegrity'),
    # Package directory
    package_dir = {'fastDataIntegrity':'src'},
    # Project version number:
    version = '1.0',
    # List a license for the project, eg. MIT License
    license_file = license_file,
    # Short description of your library:
    description="Easy-to-use data integrity and data quality package for tabular datasets.",
    # Long description of your library:
    long_description = long_description,
    long_description_content_type = "text/markdown",
    # Your name:
    author = "Federico Glancszpigel",
    # Your email address:
    author_email = "...",
    # Link to your github repository or website:
    url="https://github.com/fedeglan/fast-data-integrity",
    # Download Link from where the project can be downloaded from:
    download_url = "https://github.com/fedeglan/fast-data-integrity",
    # List of keywords:
    keywords = ["data"],
    # List project dependencies:
    install_requires = [requirements_list],
    # https://pypi.org/classifiers/
    classifiers = [],
)
