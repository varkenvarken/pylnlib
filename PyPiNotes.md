```bash
geany setup.py  # edit version numbeer
python setup.py sdist
twine upload -r pypi dist/pylnlib-<version>.tar.gz  # credentials are in ~/.pypirc
```
