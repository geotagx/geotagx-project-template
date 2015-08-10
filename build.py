#!/usr/bin/env python
#
# The GeoTag-X template builder.
# Copyright (C) 2015 UNITAR, Jeremy Othieno.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
from builder.src.project import Project

def summarize(path):
	"""summarize(path:string)
	Prints a summary of the GeoTag-X project at the directory pointed to by the specified path.
	"""
	try:
		print Project(path)
		exitval = 0
	except Exception as e:
		print e
		exitval = 1
	finally:
		sys.exit(exitval)


def write(writer, path):
	"""write(writer:HtmlWriter, path:string)
	For the project located at the specified path, this method will write its
	task presenter and tutorial, if the respective configurations exist.
	"""
	try:
		exitval = 0
		writable, message = writer.iswritabledir(path)
		if writable:
				project = Project(path)
				writer.write(project)
		else:
			print message
			exitval = 1
	except Exception as e:
		print e
		exitval = 1
	finally:
		sys.exit(exitval)


def main(argv):
	from builder.src._argparse import CustomArgumentParser, CustomHelpFormatter

	parser = CustomArgumentParser(
		description="builds the task presenter and tutorial for the GeoTag-X projects located in the specified directories.",
		formatter_class=CustomHelpFormatter,
		add_help=False
	)
	parser.add_argument("path", metavar="PATH", nargs='+')
	parser.add_argument("-c", "--compress",  action="store_true", help="compresses the generated files, effectively generating smaller, albeit less readable, task presenters and tutorials.")
	parser.add_argument("-f", "--force",     action="store_true", help="overwrites any existing task presenter and/or tutorial in the specified directory.")
	parser.add_argument("-h", "--help",      action="help",       help="prints this help message and exits.")

	# TODO This is a work in progress so it's hidden from users by suppressing the help.
	import argparse # TODO Remove this import when '-i' is implemented, i.e. when argparse.SUPPRESS is no longer required.
	parser.add_argument("-i", "--inline",    action="store_true", help=argparse.SUPPRESS)#help="inlines static cascading stylsheets and scripts in the task presenters and tutorials. Inlining external resources is not recommended, however it may be useful in cases where you would like to test your project on a platform other than GeoTag-X, such as crowdcrafting.org, while maintaining the same look-and-feel.")
	parser.add_argument("-s", "--summarize", action="store_true", help="prints a project's overview.")

	if len(sys.argv) < 2:
		parser.print_usage()
		sys.exit(1)
	else:
		args = parser.parse_args()

		# Remove duplicate absolute paths.
		import os
		args.path = set([os.path.realpath(path) for path in args.path])

		if args.summarize:
			for path in args.path:
				summarize(path)
		else:
			import os
			from builder.src.htmlwriter import HtmlWriter

			layout = os.path.join(os.path.dirname(os.path.realpath(__file__)), "layout")
			writer = HtmlWriter(layout, args.compress, args.force, args.inline)

			# TODO Thread this for a large number of projects.
			for path in args.path:
				write(writer, path)


if __name__ == "__main__":
	import sys
	main(sys.argv)
