![Test](https://github.com/varkenvarken/pylnlib/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/varkenvarken/pylnlib/branch/master/graph/badge.svg?token=8080H7HK2F)](https://codecov.io/gh/varkenvarken/pylnlib)
![CodeQL](https://github.com/varkenvarken/pylnlib/actions/workflows/codeql-analysis.yml/badge.svg)
![Black](https://github.com/varkenvarken/pylnlib/actions/workflows/black.yml/badge.svg)
[![Versions](https://img.shields.io/pypi/v/pylnlib)](https://pypi.org/project/pylnlib/)
![Python versions](https://img.shields.io/pypi/pyversions/pylnlib)

# pylnlib
A python library to monitor LocoNet traffic on a usb/serial bus.

Documentation (a work in progress) can be found on [https://varkenvarken.github.io/pylnlib/](https://varkenvarken.github.io/pylnlib/)

# installation

just the library:

```bash
pip install pylnlib
```

with the experimental webserver (this will also pull all dependencies, like fastapi, uvicorn, etc):

```bash
pip install pylnlib[webserver]
```

