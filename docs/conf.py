"""Configuration file for the Sphinx documentation builder."""
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

from pathlib import Path

import pkg_resources

from pudl.metadata.classes import Package
from pudl.metadata.resources import RESOURCE_METADATA

DOCS_DIR = Path(__file__).parent.resolve()

# -- Path setup --------------------------------------------------------------
# We are building and installing the pudl package in order to get access to
# the distribution metadata, including an automatically generated version
# number via pkg_resources.get_distribution() so we need more than just an
# importable path.

# The full version, including alpha/beta/rc tags
release = pkg_resources.get_distribution('catalystcoop.pudl').version

# -- Project information -----------------------------------------------------

project = 'PUDL'
copyright = '2016-2021, Catalyst Cooperative, CC-BY-4.0'  # noqa: A001
author = 'Catalyst Cooperative'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'autoapi.extension',
    'sphinx_issues',
    'sphinx_reredirects',
    'sphinx_rtd_dark_mode',
    'sphinxcontrib.bibtex',
]
todo_include_todos = True
bibtex_bibfiles = [
    'catalyst_pubs.bib',
    'catalyst_cites.bib',
    'further_reading.bib',
]

# Redirects to keep folks from hitting 404 errors:
redirects = {
    "data_dictionary": "data_dictionaries/pudl_db.html",
}

# Automatically generate API documentation during the doc build:
autoapi_type = 'python'
autoapi_dirs = ['../src/pudl', ]
autoapi_ignore = [
    "*_test.py",
    "*/package_data/*",
]

# GitHub repo
issues_github_path = "catalyst-cooperative/pudl"

# In order to be able to link directly to documentation for other projects,
# we need to define these package to URL mappings:
intersphinx_mapping = {
    'arrow': ('https://arrow.apache.org/docs/', None),
    'dask': ('https://docs.dask.org/en/latest/', None),
    'geopandas': ('https://geopandas.org/', None),
    'networkx': ('https://networkx.org/documentation/stable/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable', None),
    'pytest': ('https://docs.pytest.org/en/latest/', None),
    'python': ('https://docs.python.org/3', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference', None),
    'setuptools': ('https://setuptools.pypa.io/en/latest/', None),
    'sklearn': ('https://scikit-learn.org/stable', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/latest/', None),
    'tox': ('https://tox.readthedocs.io/en/latest/', None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.

# user starts in dark mode
default_dark_mode = False

master_doc = 'index'
html_theme = 'sphinx_rtd_theme'
html_logo = '_static/catalyst_logo-200x200.png'
html_icon = '_static/favicon.ico'

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "catalyst-cooperative",  # Username
    "github_repo": "pudl",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "collapse_navigation": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Custom build operations -------------------------------------------------
def metadata_to_rst(app):
    """Export metadata structures to RST for inclusion in the documentation."""
    # Create an RST Data Dictionary for the PUDL DB:
    print("Exporting PUDL DB metadata to RST.")
    skip_names = ["datasets", "accumulated_depreciation_ferc1"]
    names = [name for name in sorted(RESOURCE_METADATA) if name not in skip_names]
    package = Package.from_resource_ids(names)
    # Sort fields within each resource by name:
    for resource in package.resources:
        resource.schema.fields = sorted(
            resource.schema.fields, key=lambda x: x.name
        )
    package.to_rst(path=DOCS_DIR / "data_dictionaries/pudl_db.rst")


def cleanup_rst(app, exception):
    """Remove generated RST files when the build is finished."""
    (DOCS_DIR / "data_dictionaries/pudl_db.rst").unlink()


def setup(app):
    """Add custom CSS defined in _static/custom.css."""
    app.add_css_file('custom.css')
    app.connect("builder-inited", metadata_to_rst)
    app.connect("build-finished", cleanup_rst)
