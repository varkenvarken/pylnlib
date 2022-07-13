from setuptools import setup

setup(
    name="pylnlib",
    version="0.2.1",
    description="A library to monitor LocoNet message on a serial interface",
    url="https://varkenvarken.github.io/pylnlib/",
    author="varkenvarken",
    author_email="test@example.com",
    license="GPLv3",
    packages=["pylnlib"],
    install_requires=[
        "pyserial",
    ],
    extras_require={"webserver": "fastapi[all]"},
    zip_safe=False,
)
