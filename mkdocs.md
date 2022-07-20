```bash
# use sudo if you want to install this site wide
# the mkdocs package takes care of generating a static site
python -m pip install mkdocs
# the mkapi extension converts docstrings to markdown
python -m pip install mkapi
# the material theme for mkdocs
python -m pip install mkdocs-material

# goto the top level project directory
cd pylnlib
# make sure it is included in the PYTHONPATH (because mkdocs will clobber it)
export PYTHONPATH=`pwd`
# build the docs directory
PYLNLIB_DUMMY=Y mkdocs build
# publish the site (will also build the docs)
PYLNLIB_DUMMY=Y mkdocs -v gh-deploy --force
# I would ove to make this a GitHub action but mkapi won play ball:
# it works perfectly fine locally but not on GitHub
```
