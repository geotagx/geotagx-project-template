# The GeoTag-X project builder tool.
# This module contains the project builder's entry point.
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
from geotagx_sanitizer.helper import filter_paths

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
	options.add_argument("-v", "--verbose", action="store_true", help="Detail the actions being performed.")
	options.add_argument("-V", "--version", action="version", help="Display version information and exit.", version=_version())

	parser.add_argument("paths", metavar="PATH", nargs="+")

	return parser


def _version():
	"""Returns the project's version string."""
	from __init__ import __version__
	return "GeoTag-X Project Builder Tool v%s, Copyright (C) 2016 UNITAR/UNOSAT." % __version__


def _run(arguments):
	"""Runs the builder with the specified arguments."""
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
			summarize_projects(arguments.paths)
		else:
			build_projects(arguments.paths, overwrite=arguments.force, compress=arguments.compress)
	except Exception as e:
		exit_code = 1
		if arguments.verbose:
			import traceback
			traceback.print_exc()
		else:
			print e.__class__.__name__ if not str(e) else "%s: %s" % (e.__class__.__name__, e)
	finally:
		return exit_code


#TODO Complete documentations.
def build_projects(paths, overwrite=False, compress=False):
	"""Builds the GeoTag-X projects at the specified paths.

	If a path does not contain a valid GeoTag-X project, it will be skipped.

	Raises:
		TypeError: If the 'paths' parameter is not a list.
		ValueError: If the 'paths' parameter is an empty list.
		IOError: If a path in the list of 'paths' can not be accessed.
	"""
	if not isinstance(paths, list):
		raise TypeError("The 'paths' parameter must be a list of paths.")
	elif not paths:
		raise ValueError("The 'paths' parameter must contain at least one path.")

	paths = filter_paths(paths)
	if not paths:
		logging.warning("No valid paths to build...")
		return

	import html_writer
	writer = html_writer.HtmlWriter()
	for p in paths:
		writer.write(p, overwrite=overwrite, compress=compress)


def summarize_projects(paths):
	"""Summarizes the GeoTag-X projects at the specified paths.

	If a path does not contain a valid GeoTag-X project, it will be skipped.

	Raises:
		TypeError: If the 'paths' parameter is not a list.
		ValueError: If the 'paths' parameter is an empty list.
		IOError: If a path in the list of 'paths' can not be accessed.
	"""
	if not isinstance(paths, list):
		raise TypeError("The 'paths' parameter must be a list of paths.")
	elif not paths:
		raise ValueError("The 'paths' parameter must contain at least one path.")

	paths = filter_paths(paths)
	if not paths:
		logging.warning("No (valid) paths to summarize...")
		return

	#TODO
	raise NotImplementedError()


def main(argv=None):
	import sys
	parser = _init_argparser()
	return _run(parser.parse_args(sys.argv[1:] if argv is None else argv))
