# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Laser Offset'
copyright = '2022, Andrey Zarembo-Godzyatskiy'
author = 'Andrey Zarembo-Godzyatskiy'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc'
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_theme_options = {
    # Disable showing the sidebar. Defaults to 'false'
    'nosidebar': True,
    'show_powered_by': False,
    'github_user': 'AndreyZarembo',
    'github_repo': 'LaserOffset',
    'github_banner': True,
    'show_related': False,
    'note_bg': '#FFF59C'
}