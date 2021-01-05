import os
import sys

from setuptools import find_packages, setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

# The current version (bump it in libs/__init__.py)
def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            # __version__ = "0.9"
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

long_description = read('README.md')

# This call to setup() does all the work
setup(
    name="menu-beliebtheits-rechner",
    version=get_version("libs/__init__.py"),
    description="Bewertung der Beliebtheit angebotener Menus in entsprechenden Kombinationen",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biomodelling/menu_beliebtheit",
    author="Matteo Delucchi",
    license="LGPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
)
