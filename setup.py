from setuptools import setup

setup(
    name="pylnlib",
    version="0.1.1",
    description="A library to monitor LocoNet message on a serial interface",
    url="https://github.com/varkenvarken/pylnlib",
    author="varkenvarken",
    author_email="test@example.com",
    license="GPLv3",
    packages=["pylnlib"],
    install_requires=[
        "pyserial",
    ],
    zip_safe=False,
)
