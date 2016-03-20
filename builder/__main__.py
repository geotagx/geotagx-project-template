#!/usr/bin/env python
#
# The GeoTag-X project builder tool.
# This module contains the entry point for the builder tool.
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
import sys

def _version():
	"""Returns the project's version string."""
	from __init__ import __version__
	return "GeoTag-X Project Builder Tool v%s, Copyright (C) 2016 UNITAR/UNOSAT." % __version__


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
		parser.set_defaults(handler=_run)
	else:
		raise TypeError("'subparser' parameter must be a '_SubParsersAction' instance.")

	options = parser.add_argument_group("OPTIONS")
	options.add_argument("-c", "--compress", action="store_true", help="Compresses the generated HTML files.")
	options.add_argument("-f", "--force", action="store_true", help="Forcefully overwrite existing HTML files.")
	options.add_argument("-h", "--help", action="help", help="Display this help and exit.")
	options.add_argument("-q", "--quiet", action="store_true", help="Suppress all warnings.")
	options.add_argument("-s", "--summarize", action="store_true", help="Display a project's summary.")
	options.add_argument("-t", "--theme", metavar="THEME", nargs=1, help="Set the path to a custom defined project theme.")
	options.add_argument("-v", "--verbose", action="store_true", help="Detail the actions being performed.")
	options.add_argument("-V", "--version", action="version", help="Display version information and exit.", version=_version())

	parser.add_argument("paths", metavar="PATH", nargs="+")

	return parser


def _run(arguments):
	"""Runs the builder with the specified arguments."""
	exit_code = 0
	import os, logging
	try:
		loglevel = logging.WARNING
		if arguments.quiet:
			loglevel = logging.ERROR
		if arguments.verbose:
			loglevel = logging.INFO

		logging.basicConfig(format="[%(levelname)s] %(message)s", level=loglevel)

		# If set, the 'theme' argument is a list of strings. Pick the first element of this list.
		if arguments.theme is not None:
			arguments.theme = arguments.theme[0]

		import core
		core.main(arguments.paths, overwrite=arguments.force, compress=arguments.compress, summarize=arguments.summarize, theme_path=arguments.theme)
	except Exception as e:
		exit_code = 1
		if arguments.verbose:
			import traceback
			traceback.print_exc()
		else:
			print e.__class__.__name__ if not str(e) else "%s: %s" % (e.__class__.__name__, e)
	finally:
		return exit_code


def main(argv=None):
	parser = _init_argparser()
	return _run(parser.parse_args(sys.argv[1:] if argv is None else argv))




if __name__ == "__main__":
	sys.exit(main())
