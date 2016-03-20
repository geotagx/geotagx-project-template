# The GeoTag-X project builder tool.
# This module contains the core elements that help build a project's HTML files.
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
def main(paths, overwrite=False, compress=False, summarize=False, theme_path=None, verbose=False):
	"""Builds the HTML files for the projects located at the specified paths.

	Args:
		paths (list): A collection of paths to GeoTag-X projects.
		overwrite (bool): A flag that determines whether or not project configurations can be
			overwritten with their formatted variations.
		compress (bool): If set to True, the generated HTML files will be compressed.
		summarize (bool): A flag that if set to True, will display a summary of the project at a
			specified path, without building it.
		theme_path (str): A path to a directory containing a custom project theme. If no theme is specified,
			the default project theme is used.

	Raises:
		TypeError: If the 'paths' parameter is not a list.
		ValueError: If the 'paths' parameter is an empty list.
		IOError: If a path in the list of 'paths' can not be accessed.
	"""
	if not isinstance(paths, list):
		raise TypeError("The 'paths' parameter must be a list of paths.")
	elif not paths:
		raise ValueError("The 'paths' parameter must contain at least one path.")

	import os, logging

	# Remove all duplicate, invalid target paths, including symbolic links.
	paths = set([os.path.realpath(p) for p in paths])
	# paths = filter(validators.Validator.has_project, paths)
	if not paths:
		logging.warning("No (valid) paths to build...")
		return

	if summarize:
		for p in paths:
			summarize_project(p)
	else:
		from html_writer import HtmlWriter

		# If no path to a custom theme is specified, use the default theme. If a path
		# is specified however, note that it will be stored as the first item in a list.
		if not theme_path or (isinstance(theme_path, basestring) and not theme_path.strip()):
			theme_path = get_default_theme_path()
		else:
			theme_path = theme_path.strip()

		writer = HtmlWriter(theme_path)
		for p in paths:
			writer.write(p, overwrite=overwrite, compress=compress, verbose=verbose)


def summarize_project(path):
	"""Summarizes the project at the specified path.

	Args:
		path (str): A path to the GeoTag-X project to summarize.

	Raises:
		TypeError: If the path is not a string.
		ValueError: If the path is an empty string.
		IOError: If the path is not a readable directory.
	"""
	import os, logging
	if path is None:
		logging.info("Unspecified path to summarize. Skipping...")
		return
	elif not isinstance(path, basestring):
		raise TypeError("The 'path' parameter must be a string.")
	elif not path.strip():
		raise ValueError("The 'path' parameter must be a non-empty string.")
	elif not (os.path.isdir(path) and os.access(path, os.R_OK)):
		raise IOError("Could not open '%s'. Please make sure it is a directory and that you have the appropriate access permissions." % path)

	#TODO
	raise NotImplementedError()


def get_default_theme_path():
	"""Returns the path to the default project theme."""
	import os.path as path
	return path.join(path.dirname(path.realpath(__file__)), "theme")
