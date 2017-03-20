#!/usr/bin/env python
#
# This setup script is inspired by code from the Pip setup.py found
# here: https://github.com/pypa/pip/blob/develop/setup.py
import os, re, codecs
from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    # https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(cwd, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="geotagx-builder",
    version=find_version("src", "__init__.py"),
    description="The GeoTag-X Project Builder Tool.",
    long_description=read("README.md"),
    zip_safe=True,
    install_requires=[
        "geotagx_validator>=0.1.0",
        "geotagx_formatter>=0.1.0",
        "htmlmin>=0.1.10",
    ],
    dependency_links=[
        "https://github.com/geotagx/geotagx-tool-validator/archive/v0.1.0.tar.gz#egg=geotagx_validator-0.1.0",
        "https://github.com/geotagx/geotagx-tool-formatter/archive/v0.1.0.tar.gz#egg=geotagx_formatter-0.1.0",
    ],
    keywords="geotag-x project builder tool command line",
    author="Jeremy Othieno, S.P. Mohanty",
    author_email="j.othieno@gmail.com, sp.mohanty@cern.ch",
    url="https://github.com/geotagx/geotagx-tool-builder",
    download_url="https://github.com/geotagx/geotagx-tool-builder",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities"
    ],
    platforms="any",
    license="MIT",
    packages=["geotagx_builder"],
    package_dir={"geotagx_builder": "src"},
    entry_points={
        "console_scripts":[
            "geotagx-builder=geotagx_builder.__main__:main"
        ]
    }
)
