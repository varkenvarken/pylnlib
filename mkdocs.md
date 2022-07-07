```bash
# use sudo if you want to install this site wide
# the mkdocs package takes care of generating a static site
python -m pip install mkdocs
# the jetblack-markdown extension to mkdocs converts docstrings to markdown
python -m pip install jetblack-markdown
# the material theme for mkdocs
python -m pip install mkdocs-material

# goto the top level project directory
cd pylnlib
# make sure it is included in the PYTHONPATH (because mkdocs will clobber it)
export PYTHONPATH=`pwd`
# build the docs directory
mkdocs build
```
