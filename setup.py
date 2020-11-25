import pathlib
from setuptools import setup, find_packages
from distutils.spawn import find_executable
import platform


def readme():
    with open('README.md') as f:
        return f.read()


dependencies = ['pyperclip', 'click', 'appdirs', 'daemonize']
if find_executable("fswatch") is None:
    if platform.system() == "Linux":
        dependencies.append("inotify")
    else:
        raise ValueError(
                "diagrams-net-figures needs fswatch to run on MacOS. You "
                "can install it using `brew install fswatch`"
                )

setup(
    name="diagrams-net-figures",
    version="0.0.1",
    description="Script for managing diagrams.net figures",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jsochacki/diagrams-net-figures",
    author="John Sochacki",
    author_email="johnsochacki@hotmail.com",
    license="GPL-3.0",
    classifiers=[
        "License :: GNU General Public License v3.0",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=['diagramsnetfigures'],
    scripts=['bin/diagrams-net-figures'],
    install_requires=dependencies,
    include_package_data=True
)
