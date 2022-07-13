from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pylnlib",
    version="0.2.2",
    description="A library to monitor LocoNet message on a serial interface",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://varkenvarken.github.io/pylnlib/",
    author="varkenvarken",
    author_email="test@example.com",
    license="GPLv3",
    packages=["pylnlib"],
    python_requires='>=3.8',
    install_requires=[
        "pyserial",
    ],
    extras_require={"webserver": "fastapi[all]"},
    zip_safe=False,
)
