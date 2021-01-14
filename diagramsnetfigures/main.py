#!/usr/bin/env python3

import os
import re
import subprocess
import warnings
from pathlib import Path
from shutil import copy
from daemonize import Daemonize
import click
import platform
from .picker import pick
import pyperclip
from appdirs import user_config_dir

def diagramsnet(path):
    with warnings.catch_warnings():
        # leaving a subprocess running after interpreter exit raises a
        # warning in Python3.7+
        warnings.simplefilter("ignore", ResourceWarning)
        subprocess.Popen(['drawio', str(path)])

def indent(text, indentation=0):
    lines = text.split('\n');
    return '\n'.join(" " * indentation + line for line in lines)

def beautify(name):
    return name.replace('_', ' ').replace('-', ' ').title()

def latex_template(name, title):
    return '\n'.join((
        r"\begin{figure}[H]",
        r"    \centering",
        rf"    \incfig{{{name}}}",
        rf"    \caption{{{title}}}",
        rf"    \label{{fig:{name}}}",
        r"\end{figure}"))

def markdown_template(name, title):
    return rf"![{title}]({name})"

# From https://stackoverflow.com/a/67692
def import_file(name, path):
    import importlib.util as util
    spec = util.spec_from_file_location(name, path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load user config

user_dir = Path(user_config_dir("diagrams-net-figures", "John Sochacki"))

if not user_dir.is_dir():
    user_dir.mkdir()

roots_file =  user_dir / 'roots'
template = user_dir / 'template.svg'
config = user_dir / 'config.py'

if not roots_file.is_file():
    roots_file.touch()

if not template.is_file():
    source = str(Path(__file__).parent / 'template.svg')
    destination = str(template)
    copy(source, destination)

if config.exists():
    config_module = import_file('config', config)
    latex_template = config_module.latex_template
    markdown_template = config_module.markdown_template


def add_root(path):
    path = str(path)
    roots = get_roots()
    if path in roots:
        return None

    roots.append(path)
    roots_file.write_text('\n'.join(roots))


def get_roots():
    return [root for root in roots_file.read_text().split('\n') if root != '']


@click.group()
def cli():
    pass


@cli.command()
@click.argument('title')
@click.argument(
    'root',
    default=os.getcwd(),
    type=click.Path(exists=False, file_okay=False, dir_okay=True)
)
def markdown_create(title, root):
    """
    Creates a diagram for use in markdown.

    First argument is the title of the figure
    Second argument is the figure directory.

    """
    title = title.strip()
    file_name = title.replace(' ', '-').lower() + '.svg'
    pdf_file_name = title.replace(' ', '-').lower() + '.pdf'
    png_file_name = title.replace(' ', '-').lower() + '.png'
    figures = Path(root).absolute()
    if not figures.exists():
        figures.mkdir()

    figure_path = figures / file_name
    relative_file_name = Path(root) / pdf_file_name
    relative_png_file_name = 'images/' + png_file_name

    # If a file with this name already exists, append a '2'.
    if figure_path.exists():
        print(title + ' 2')
        return

    copy(str(template), str(figure_path))
    add_root(figures)
    diagramsnet(figure_path)

    # Print the code for including the figure to stdout.
    # Copy the indentation of the input.
    leading_spaces = len(title) - len(title.lstrip())
    print(indent(markdown_template(relative_png_file_name, title), indentation=leading_spaces))


@cli.command()
@click.argument('title')
@click.argument(
    'root',
    default=os.getcwd(),
    type=click.Path(exists=False, file_okay=False, dir_okay=True)
)
def latex_create(title, root):
    """
    Creates a diagram for use in latex.

    First argument is the title of the figure
    Second argument is the figure directory.

    """
    title = title.strip()
    file_name = title.replace(' ', '-').lower() + '.svg'
    figures = Path(root).absolute()
    if not figures.exists():
        figures.mkdir()

    figure_path = figures / file_name

    # If a file with this name already exists, append a '2'.
    if figure_path.exists():
        print(title + ' 2')
        return

    copy(str(template), str(figure_path))
    add_root(figures)
    diagramsnet(figure_path)

    # Print the code for including the figure to stdout.
    # Copy the indentation of the input.
    leading_spaces = len(title) - len(title.lstrip())
    print(indent(latex_template(figure_path.stem, title), indentation=leading_spaces))


@cli.command()
@click.argument(
    'root',
    default=os.getcwd(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
def edit(root):
    """
    Edits a figure.

    First argument is the figure directory.
    """

    figures = Path(root).absolute()

    # Find svg files and sort them
    files = figures.glob('*.svg')
    files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)

    # Open a selection dialog using a gui picker like rofi
    names = [beautify(f.stem) for f in files]
    _, index, selected = pick(names)
    if selected:
        path = files[index]
        add_root(figures)
        diagramsnet(path)

if __name__ == '__main__':
    cli()
