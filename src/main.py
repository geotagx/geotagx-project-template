#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The GeoTag-X project builder.
# Copyright (C) 2015 UNITAR.
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
def main(argv):
	exitval = 0
	try:
		from _argparse import CustomArgumentParser, CustomHelpFormatter

		parser = CustomArgumentParser(
			description="builds the task presenter and tutorial for the GeoTag-X projects located in the specified directories.",
			formatter_class=CustomHelpFormatter,
			add_help=False
		)
		parser.add_argument("path", metavar="PATH", nargs='+')
		parser.add_argument("-c", "--compress",  action="store_true", help="compresses the generated files, effectively generating smaller, albeit less readable, task presenters and tutorials.")
		parser.add_argument("-f", "--force",     action="store_true", help="overwrites any existing task presenter and/or tutorial in the specified directory.")
		parser.add_argument("-h", "--help",      action="help",       help="prints this help message and exits.")
		parser.add_argument("-s", "--summarize", action="store_true", help="prints a project's overview.")
		parser.add_argument("-t", "--theme",     nargs=1, metavar="THEME", help="sets the path to a user-defined theme.")
		parser.add_argument("-v", "--verbose",   action="store_true", help="explains what is being done.")

		if len(sys.argv) < 2:
			parser.print_usage()
			exitval = 1
		else:
			from project import Project
			import os

			args = parser.parse_args()
			args.path = set([os.path.realpath(path) for path in args.path]) # Remove all duplicate paths, including symbolic links.

			if args.summarize:
				for path in args.path:
					print Project(path)
			else:
				from theme import Theme
				from htmlwriter import HtmlWriter

				# If no path to a custom theme is specified, use the default theme.
				args.theme = args.theme[0] if args.theme else os.path.join(os.path.dirname(os.path.realpath(__file__)), "theme")
				print
				print args.theme
				print

				theme = Theme(args.theme)
				writer = HtmlWriter(theme, args.compress, args.force, args.verbose)

				for path in args.path:
					writable, message = writer.iswritabledir(path)
					if writable:
						project = Project(path)
						writer.write(project)
					else:
						print message

	except Exception as e:
		exitval = 1
		if args.verbose:
			import traceback
			traceback.print_exc()
		else:
			print e.__class__.__name__ if not str(e) else "%s: %s" % (e.__class__.__name__, e)
	finally:
		sys.exit(exitval)


if __name__ == "__main__":
	import sys
	main(sys.argv)
