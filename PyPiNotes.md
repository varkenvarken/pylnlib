```bash
geany setup.py  # edit version number
python setup.py sdist
#twine upload -r pypi dist/pylnlib-<version>.tar.gz  # credentials are in ~/.pypirc
twine upload dist/`ls -1 dist/ | tail -1`
rm dist/*
```
