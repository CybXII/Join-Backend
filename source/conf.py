# Configuration file for the Sphinx documentation builder.
#
import os
import sys
import django

# Set a Path to your Django-Projekt
sys.path.insert(0, os.path.abspath('../../join_ba'))

# Set a Django-Settings-Modul
os.environ['DJANGO_SETTINGS_MODULE'] = 'join_ba.settings'

# Load Django-Config
django.setup()

# Load Django-Config
django.setup()# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Join Backend'
copyright = '2024, Alexander Luft'
author = 'Alexander Luft'
release = '07.09.2024'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # For Google und NumPy Style
]
templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
