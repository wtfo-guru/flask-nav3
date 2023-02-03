extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build"]

project = "Flask-Nav"
copyright = "2015, Marc Brinkmann"
author = "Marc Brinkmann"
version = "0.6"
release = "0.6.dev1"

pygments_style = "sphinx"
html_theme = "alabaster"
html_theme_options = {
    "github_user": "mbr",
    "github_repo": "flask-nav",
}
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
        "donate.html",
    ],
}

intersphinx_mapping = {
    "https://docs.python.org/": None,
    "http://flask.pocoo.org/docs/": None,
}
