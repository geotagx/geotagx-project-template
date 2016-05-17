# -*- coding: utf-8 -*-
#
# This module is part of the GeoTag-X project builder tool.
#
# Authors: Jeremy Othieno (j.othieno@gmail.com), S. P. Mohanty
#
# Copyright (c) 2016 UNITAR/UNOSAT
#
# The MIT License (MIT)
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
from geotagx_sanitizer.helper import is_directory, filter_paths, serialize_json
from geotagx_sanitizer.sanitizer import read_configurations, sanitize_configurations

def _init_argparser(subparsers=None, parents=None):
    """Initializes the tool's command line argument parser."""
    import argparse

    PARAMETERS = {
        "description":"A tool that builds a GeoTag-X project's task presenter and tutorial from its configurations.",
        "add_help":False
    }
    parser = None
    if subparsers is None:
        parser = argparse.ArgumentParser(prog="geotagx-builder", **PARAMETERS)
    elif isinstance(subparsers, argparse._SubParsersAction):
        parser = subparsers.add_parser("build", help="Build one or more GeoTag-X projects.", **PARAMETERS)
        parser.set_defaults(handler=main)
    else:
        raise TypeError("'subparser' parameter must be a '_SubParsersAction' instance.")

    options = parser.add_argument_group("OPTIONS")
    options.add_argument("-c", "--compress", action="store_true", help="Compresses the generated HTML files.")
    options.add_argument("-f", "--force", action="store_true", help="Forcefully overwrite existing HTML files.")
    options.add_argument("-h", "--help", action="help", help="Display this help and exit.")
    options.add_argument("-q", "--quiet", action="store_true", help="Suppress all warnings.")
    options.add_argument("-s", "--summarize", action="store_true", help="Display a project's summary.")
    options.add_argument("-v", "--verbose", action="store_true", help="Detail the actions being performed.")
    options.add_argument("-V", "--version", action="version", help="Display version information and exit.", version=_version())

    parser.add_argument("paths", metavar="PATH", nargs="+")

    return parser


def _version():
    """Returns the project's version string."""
    from __init__ import __version__
    return "GeoTag-X Project Builder Tool v%s, Copyright (C) 2016 UNITAR/UNOSAT." % __version__


def _get_configurations(path):
    """Returns the configurations for the GeoTag-X project located at the specified path.
    """
    configurations = read_configurations(path)

    # Add a questionnaire index.
    questionnaire = configurations["task_presenter"]["questionnaire"]
    questionnaire["index"] = {q["key"]: i for (i, q) in enumerate(questionnaire["questions"])}

    # Add the questionnaire help.
    import os
    for question in questionnaire["questions"]:
        key = question["key"]
        filename = os.path.join(path, "help", key + ".html")
        try:
            file = open(filename)
        except IOError:
            # A help file is not always guaranteed to exist so if an IOError occurs, ignore it.
            pass
        else:
            with file:
                from htmlmin import minify
                filedata = file.read().decode("UTF-8").strip()
                question["help"] = minify(filedata, remove_comments=True, remove_empty_space=True)

    configurations = sanitize_configurations(configurations)

    # Remove redundant fields. These can be retrieved from the server's database.
    project = configurations["project"]
    for key in ["name", "short_name", "description"]:
        project.pop(key, None)

    return configurations


def parse_arguments():
    """Parses the command line arguments passed to the program.

    Returns:
        (argparse.Namespace): The collection of parsed arguments.
    """
    from sys import argv
    return _init_argparser().parse_args(argv[1:])


def summarize(paths):
    """Summarizes the GeoTag-X projects at the specified paths.

    If a path does not contain a valid GeoTag-X project, it will be ignored.

    Args:
        paths (list): A list of paths to directories containing GeoTag-X projects to summarize.

    Raises:
        TypeError: If the 'paths' parameter is not a list.
        IOError: If a path in the specified list of paths cannot be accessed.
    """
    if not isinstance(paths, list):
        raise TypeError("Invalid parameter type: summarize expects 'list' but got '{}'.".format(type(paths).__name__))

    for p in filter_paths(paths):
        raise NotImplementedError()


def build(paths, overwrite=False, compress=False):
    """Builds the GeoTag-X projects at the specified paths.

    This function will create the following HTML files:
    - template.html: the project's task presenter template,
    - tutorial.html: the project's tutorial template.

    Note that if a path does not contain a valid GeoTag-X project, it will simply be ignored.

    Args:
        paths (list): A list of paths to directories containing GeoTag-X projects to build.
        overwrite (bool): If set to True, all existing HTML files will be overwritten.
        compress (bool): If set to True, all generated files will be compressed.

    Raises:
        TypeError: If the 'paths' parameter is not a list, or the 'overwrite' and 'compress'
            parameters are not booleans.
        IOError: If a path in the specified list of paths cannot be accessed.
    """
    if not isinstance(paths, list):
        raise TypeError("Invalid parameter type: build expects 'list' for 'paths' parameter but got '{}'.".format(type(paths).__name__))
    elif not isinstance(overwrite, bool):
        raise TypeError("Invalid parameter type: build expects 'bool' for 'overwrite' parameter but got '{}'.".format(type(overwrite).__name__))
    elif not isinstance(compress, bool):
        raise TypeError("Invalid parameter type: build expects 'bool' for 'compress' parameter but got '{}'.".format(type(compress).__name__))

    for p in filter_paths(paths):
        write(_get_configurations(p), p, overwrite, compress)


# TODO Document me
def write(configurations, path, overwrite=False, compress=False):
    """
    """
    if not isinstance(configurations, dict):
        raise TypeError("Invalid parameter type: write expects 'dict' for 'configurations' parameter but got '{}'.".format(type(configurations).__name__))
    elif not isinstance(path, basestring):
        raise TypeError("Invalid parameter type: write expects 'str' or 'unicode' for 'path' parameter but got '{}'.".format(type(path).__name__))
    elif not is_directory(path, check_writable=True):
        raise IOError("The path '{}' is not a writable directory. Please make sure you have the appropriate access permissions.".format(path))
    elif not isinstance(compress, bool):
        raise TypeError("Invalid parameter type: write expects 'bool' for 'compress' parameter but got '{}'.".format(type(compress).__name__))
    elif not isinstance(overwrite, bool):
        raise TypeError("Invalid parameter type: write expects 'bool' for 'overwrite' parameter but got '{}'.".format(type(overwrite).__name__))

    import os
    output = {
        "task_presenter": os.path.join(path, "template.html"),
        "tutorial": os.path.join(path, "tutorial.html")
    }

    # If the overwrite flag is not set, make sure none of the target HTML files exists.
    if not overwrite and any(os.path.isfile(f) for f in output.values()):
        raise HtmlFileExistsError("The directory '{}' already contains a task presenter (template.html) and, or, a tutorial (tutorial.html). To overwrite either, set the '-f' or '--force' flag.".format(path))

    # Write the project's tutorial. Note that if no tutorial configuration exists,
    # an empty 'tutorial.html' file is still created as it is a requirement for
    # PyBossa's 'pbs' tool.
    with open(output["tutorial"], "w") as file:
        if configurations.get("tutorial") is not None:
            file.write(serialize_json(configurations, compress))

    # Write the task presenter.
    with open(output["task_presenter"], "w") as file:
        configurations.pop("tutorial", None) # Remove the tutorial configuration, if it exists.
        file.write(serialize_json(configurations, compress))


def main(arguments=None):
    arguments = parse_arguments() if arguments is None else arguments
    exit_code = 0

    import os, logging
    try:
        loglevel = logging.WARNING
        if arguments.quiet:
            loglevel = logging.ERROR
        elif arguments.verbose:
            loglevel = logging.INFO

        logging.basicConfig(format="[%(levelname)s] %(message)s", level=loglevel)

        if arguments.summarize:
            summarize(arguments.paths)
        else:
            build(arguments.paths, overwrite=arguments.force, compress=arguments.compress) # TODO Change arguments.force to arguments.overwrite
    except HtmlFileExistsError as e:
        print e
    except Exception as e:
        exit_code = 1
        if arguments.verbose:
            import traceback
            traceback.print_exc()
        else:
            print e.__class__.__name__ if not str(e) else "%s: %s" % (e.__class__.__name__, e)
    finally:
        return exit_code


class HtmlFileExistsError(Exception):
    pass
