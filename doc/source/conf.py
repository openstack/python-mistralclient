# Mistral documentation build configuration file

import os
import pbr.version
import sys

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('./'))

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinxcontrib.apidoc',
    'openstackdocstheme',
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# sphinxcontrib.apidoc options
apidoc_module_dir = '../../mistralclient'
apidoc_output_dir = 'api'
apidoc_excluded_paths = [
    'test',
    'tests/*']
apidoc_separate_modules = True

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Mistral Client'
copyright = u'2016, Mistral Contributors'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
version_info = pbr.version.VersionInfo('python-mistralclient')
release = version_info.release_string()
version = version_info.version_string()

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ['mistralclient.']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'openstackdocs'

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'
# Must set this variable to include year, month, day, hours, and minutes.
html_last_updated_fmt = '%Y-%m-%d %H:%M'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = 'MistralClient'

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    'index': [
        'sidebarlinks.html', 'localtoc.html', 'searchbox.html',
        'sourcelink.html'
    ],
    '**': [
        'localtoc.html', 'relations.html',
        'searchbox.html', 'sourcelink.html'
    ]
}

# Output file base name for HTML help builder.
htmlhelp_basename = 'Mistraldoc'


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'mistral_client', u'Mistral Client Documentation',
    [u'Mistral Contributors'], 1)
]

# -- Options for openstackdocstheme -------------------------------------------
repository_name = 'openstack/python-mistralclient'
bug_project = 'python-mistralclient'
bug_tag = ''
