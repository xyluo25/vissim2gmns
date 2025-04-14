'''
##############################################################
# Created Date: Monday, March 3rd 2025
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''

from __future__ import absolute_import
import logging
import os
import sys
from pathlib import Path
import datetime
import os
import sys
# import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(1, os.path.abspath('../../vissim2gmns'))

root = Path(__file__).resolve().parents[2]
sys.path = [str(root)] + sys.path

logger = logging.getLogger(__name__)

# Python's default allowed recursion depth is 1000.
sys.setrecursionlimit(5000)

# General information about the project.
project = "utdf2gmns"  # Name of the project to document, e.g. 'utdf2gmns'
author = 'Xiangyong Luo'
copyright = f'2022 - {datetime.datetime.now().year} Xiangyong Luo'
version = "1.5.4"
release = version
language = "en"

source_suffix = {'.rst': 'restructuredtext',
                 ".txt": 'restructuredtext',  # allow .txt files to be processed as rst
                 '.md': 'markdown'}  # allow .md files to be processed as rst, if markdown is installed
source_encoding = "utf-8"
master_doc = "index"

# -- General configuration -----------------------------------------------
extensions = [
    'sphinx.ext.napoleon',
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.ifconfig",
    "sphinx.ext.intersphinx",
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.extlinks',
    'sphinx.ext.todo',
    'sphinx_copybutton',
    'myst_parser',  # for parsing markdown files, must be after sphinx.ext.autodoc to work properly
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"
templates_path = ["./_templates/"]

# If true, section author and module author directives will be shown in the
# output. They are ignored by default.
show_authors = True

# -- Options for HTML output ---------------------------------------------
html_theme = 'sphinx_rtd_theme'

# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
# so a file named "default.css" will overwrite the builtin "default.css".
html_title = "vissim2gmns"
html_short_title = "vissim2gmns"
html_logo = "./_static/vissim2gmns.ico"
html_favicon = "./_static/vissim2gmns.ico"
html_static_path = ["_static"]

# Output file base name for HTML help builder.
htmlhelp_basename = "vissim2gmns"
