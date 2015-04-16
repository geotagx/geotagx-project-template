#!/usr/bin/env python
import os, sys, codecs, locale, json, htmlmin
from jinja2 import Environment, FileSystemLoader
from slimit import minify
from rcssmin import cssmin

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

USAGE = """Usage: """ + __file__ + """ directory [OPTIONS]
Build the task presenter for the GeoTag-X project located in the specified directory.
The following is a list of OPTIONS you can use to modify the script's behavior:\n
\r    -f, --force       overwrites the file 'template.html' in the specified directory.
\r    -c, --compress    compresses the generated task presenter.
\r    -h, --help        prints this help message.\n"""


LAYOUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "layout")


def has_valid_project(path):
	"""Returns true if the directory with the specified path is writable, and contains a valid GeoTag-X project, false otherwise."""
	return  os.path.isdir(path) \
		and os.access(path, os.W_OK) \
		and os.access(os.path.join(path, "project.json"), os.F_OK | os.R_OK)


def is_valid_project_json(json):
	"""Returns true if the specified JSON object has a valid project structure, false otherwise."""
	# TODO
	return True


def get_project_json(filename):
	"""Converts the project.json file into a JSON object and returns it."""
	with open(filename) as file:
		data = file.read()
		return json.loads(data)

"""
Collects CSS files from the template static folder, optionally minifies them,
and then embeds them directly into the rendered output
"""
def get_template_css(compress):
	import os
	css_raw = ""
	for root, dirs, files in os.walk(LAYOUT_DIR+"/static", topdown=False):
		for name in files:
			if name.split(".")[-1] == "css":
				css_raw += open(os.path.join(root, name),"r").read()
	return css_raw if not compress else cssmin(css_raw, keep_bang_comments=False)

"""
Collects JS files from the template static folder, optionally minifies them,
and then embeds them directly into the rendered output
"""
def get_template_js(compress):
	import os
	js_raw = ""
	for root, dirs, files in os.walk(LAYOUT_DIR+"/static", topdown=False):
		for name in files:
			if name.split(".")[-1] == "js":
				js_raw += open(os.path.join(root, name),"r").read()
	return js_raw if not compress else minify(js_raw)

def get_project_css(filename, compress):
	"""Returns the project's custom stylesheet, minified."""
	with open(filename, "r") as f:
		css = f.read()
		return css if not compress else cssmin(css, keep_bang_comments=False)


def get_project_js(filename, compress):
	"""Returns the project's custom script, minified."""
	with open(filename, "r") as f:
		js = f.read()
		return js if not compress else minify(js)


def get_project_help(directory):
	"""Returns a dictionary that contains the help provided for a specific question."""
	help = {}
	filenames = filter(lambda file: file.endswith(".html"), os.listdir(directory))

	for filename in filenames:
		with open(os.path.join(directory, filename)) as file:
			filedata = file.read().strip()
			if filedata:
				# Associate the file's content with a question identifier.
				id = os.path.splitext(os.path.basename(filename))[0]
				help[id] = filedata

	return help


def build(path, compress=True):
	"""Builds the task presenter for the project located at the specified path."""
	project_dir = os.path.realpath(path)

	json = get_project_json(os.path.join(project_dir, "project.json"))
	if not is_valid_project_json(json):
		print "Error! The 'project.json' file is not valid."
		sys.exit(1)

	template   = Environment(loader=FileSystemLoader(searchpath=LAYOUT_DIR)).get_template("base.html")
	short_name = json["short_name"].strip()
	why_       = json["why"].strip()
	questions_ = json["questions"]

	# Assign the help to its corresponding question.
	help = get_project_help(os.path.join(project_dir, "help"))
	if len(help) > 0:
		for question in questions_:
			key = str(question["id"])
			try:
				question[u"help"] = help[key]
			except:
				pass

	# Build the template.
	with open(os.path.join(project_dir, "template.html"), "w") as output:
		js_  = get_template_js(compress) # Collects JS common to the whole template
		css_ = get_template_css(compress) # Collects CSS common to the whole template
		css_ += get_project_css(os.path.join(project_dir, "project.css"), compress)
		js_  += get_project_js(os.path.join(project_dir, "project.js"), compress)
		html = template.render(questions=questions_, css=css_, js=js_, slug=short_name, why=why_)

		if compress:
			html = htmlmin.minify(html, remove_comments=True, remove_empty_space=True)

		output.write(html.encode("UTF-8"))


def main(argv):
	argc = len(argv)
	if argc != 2:
		print USAGE
	else:
		path = argv[1]
		if not path or path in ("-h", "--help"):
			print USAGE
		else:
			if has_valid_project(path):
				build(path)
			else:
				print "The directory '" + path + "' does not contain a valid GeoTag-X project, or you may not have read/write permissions."


if __name__ == "__main__":
	main(sys.argv)
