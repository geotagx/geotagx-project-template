#!/usr/bin/python
# The GeoTag-X template builder.


def get_static_css(compress, inline):
	return None


def get_static_js(compress, inline):
	return None


def build(path, css, js, compress, overwrite):
	"""build(path:string, css:string, js:string, compress:boolean, overwrite:boolean)
	Builds a GeoTag-X project at the directory pointed to by the specified path.
	"""
	from _project import Project

	project = Project.create(path, overwrite)
	if project and project.build(css, js, compress):
		write(project)


def write(project):
	"""write(project:Project)
	Renders the specified project's task presenter and, if it exists, tutorial.
	"""
	print project


def main(argv):
	import argparse
	from _argparse import CustomArgumentParser, CustomHelpFormatter

	parser = CustomArgumentParser(
		description="builds the task presenter and tutorial for the GeoTag-X projects located in the specified directories.",
		formatter_class=CustomHelpFormatter,
		add_help=False
	)
	parser.add_argument("path", metavar="PATH", nargs='+')
	parser.add_argument("-c", "--compress", action="store_true", help="compresses the generated files, effectively generating smaller, albeit less readable, task presenters and tutorials.")
	parser.add_argument("-f", "--force",    action="store_true", help="overwrites any existing task presenter and/or tutorial in the specified directory.")
	parser.add_argument("-h", "--help",     action="help",       help="prints this help message and exits.")

	# TODO This is a work in progress so it's hidden from users by suppressing the help.
	parser.add_argument("-i", "--inline",   action="store_true", help=argparse.SUPPRESS)#help="inlines static cascading stylsheets and scripts in the task presenters and tutorials. Inlining external resources is not recommended, however it may be useful in cases where you would like to test your project on a platform other than GeoTag-X, such as crowdcrafting.org, while maintaining the same look-and-feel.")

	if len(sys.argv) < 2:
		parser.print_usage()
		sys.exit(1)
	else:
		args = parser.parse_args()
		js   = get_static_js(args.compress, args.inline)
		css  = get_static_css(args.compress, args.inline)

		# TODO Thread this for projects > 3.
		for path in args.path:
			build(path, css, js, args.compress, args.force)

if __name__ == "__main__":
	import sys
	main(sys.argv)
