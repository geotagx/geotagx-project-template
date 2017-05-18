# -*- coding: utf-8 -*-
#
# This module is part of the GeoTag-X project builder tool.
#
# Authors: Jeremy Othieno (j.othieno@gmail.com), S. P. Mohanty
#
# Copyright (c) 2016-2017 UNITAR/UNOSAT
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
import argparse
import os
from geotagx_validator.helper import check_arg_type

def main():
    """Executes the application.
    """
    import sys
    sys.exit(run(get_argparser().parse_args(sys.argv[1:])))


def run(arguments):
    """Executes the application with the specified command-line arguments.

    Args:
        arguments (argparse.Namespace): A set of command-line arguments.

    Returns:
        int: 0 if building was successful, 1 otherwise.
    """
    check_arg_type(run, "arguments", arguments, argparse.Namespace)

    from geotagx_validator.helper import sanitize_paths
    from geotagx_validator.core import is_configuration_set
    from helper import get_formatted_configuration_set, generate_html

    exit_code = 0
    try:
        if not arguments.quiet:
            _setup_logging(arguments.verbose)

        for path in sanitize_paths(arguments.paths):
            configuration_set = get_formatted_configuration_set(path, enable_logging=arguments.verbose)
            valid, message = is_configuration_set(configuration_set, enable_logging=arguments.verbose)
            if not valid:
                print message
                exit_code = 1
                break
            else:
                generate_html(configuration_set, path, arguments.force, arguments.compress)
                print "The project located at '{}' was successfully built.".format(path)
    except Exception as e:
        _print_exception(e, arguments.verbose)
        exit_code = 1
    finally:
        return exit_code


def get_argparser(subparsers=None):
    """Constructs the application's command-line argument parser. The build tool
    is a standalone program but also a part of the GeoTag-X toolkit which means
    that its arguments can be sub-commands to a specific command. For more information,
    check out: https://docs.python.org/2/library/argparse.html#sub-commands

    Args:
        subparsers (argparse._SubParsersAction): If specified, the argument parser is
            created as a parser for a program command, and not the actual program.

    Returns:
        argparse.ArgumentParser: A command-line argument parser instance.

    Raises:
        TypeError: If the subparsers argument is not a NoneType or an argparse._SubParsersAction instance.
    """
    check_arg_type(get_argparser, "subparsers", subparsers, (argparse._SubParsersAction, type(None)))

    parser = None
    parser_arguments = {
        "description": "A tool that builds a GeoTag-X project's task presenter and tutorial from its configurations.",
        "add_help": False,
    }
    if subparsers is None:
        parser = argparse.ArgumentParser(prog="geotagx-builder", **parser_arguments)
    elif isinstance(subparsers, argparse._SubParsersAction):
        parser = subparsers.add_parser("build", help="Build your GeoTag-X projects.", **parser_arguments)
        parser.set_defaults(run=run)

    options = parser.add_argument_group("OPTIONS")
    options.add_argument("-c", "--compress", action="store_true", help="Compresses the generated HTML files.")
    options.add_argument("-f", "--force", action="store_true", help="Forcefully overwrite existing HTML files.")
    options.add_argument("-h", "--help", action="help", help="Display this help and exit.")
    options.add_argument("-q", "--quiet", action="store_true", help="Suppress all warnings.")
    options.add_argument("-v", "--verbose", action="store_true", help="Detail the actions being performed.")
    options.add_argument("-V", "--version", action="version", help="Display version information and exit.", version=_version())

    parser.add_argument("paths", metavar="PATH", nargs="+")

    return parser


def _version():
    """Returns the tool's version string."""
    from __init__ import __version__
    return "GeoTag-X Project Builder Tool v%s, Copyright (C) 2016-2017 UNITAR/UNOSAT." % __version__


def _setup_logging(verbose=False):
    """Sets up logging.

    Args:
        verbose (bool): If set to True, the build tool will log most of its operations, even the mundane.
    """
    import logging
    logging_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging_level)


def _print_exception(exception, verbose=True):
    """Prints the specified exception information.
    If the exception does not contain a message, the stack trace will be printed
    by default.

    Args:
        exception (Exception): The exception information to print.
        verbose (bool): If set to True, the entire stack trace will be printed.
    """
    if not str(exception) or verbose:
        import traceback
        traceback.print_exc()
    else:
        print "{0}: {1}".format(exception.__class__.__name__, exception)


if __name__ == "__main__":
    main()
