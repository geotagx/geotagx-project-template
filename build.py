#!/usr/bin/env python
import os, sys, codecs, locale, json, htmlmin
from jinja2 import Environment, FileSystemLoader
from slimit import minify
from rcssmin import cssmin

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

LAYOUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "layout")
TEMPLATE = "base.html"

HELP_TEXT = """
<p>In this question we are trying to identify photos in which there is water and would therefore be relevant to the application.</p>
<p>If you can see water in this photo select <button class="btn btn-xs btn-success" disabled>Yes</button>. Water includes smaller water bodies such as irrigation channels, open sewers, ponds, puddles of water, or pools of water accumulated in garbage like tyres and bits of plastic, along with large water bodies such as lakes, rivers, and flood waters.</p>
<p>In short, if you see a water body, big, small, or even just a puddle, click <button class="btn btn-xs btn-success" disabled>Yes</button></p>
<p>Here are some examples for which you would click <button class="btn btn-xs btn-success" disabled>Yes</button></p>
<div class="row">
	<div class="col-sm-4">
		<a target="_blank" rel="nofollow" href="http://i.dailymail.co.uk/i/pix/2013/06/19/article-2344673-1A686A7B000005DC-545_634x396.jpg"><img src="http://i.dailymail.co.uk/i/pix/2013/06/19/article-2344673-1A686A7B000005DC-545_634x396.jpg" class="img-responsive img-thumbnail"></a>
		<small><p><i class="fa fa-fw fa-lg fa-photo"></i>Reuters</p></small>
	</div>
	<div class="col-sm-4">
		<a target="_blank" rel="nofollow" href="https://dl.dropboxusercontent.com/u/46576246/India/DSCI0434.JPG"><img src="https://dl.dropboxusercontent.com/u/46576246/India/DSCI0434.JPG" class="img-responsive img-thumbnail"></a>
		<small><p><i class="fa fa-fw fa-lg fa-photo"></i><a target="_blank" rel="nofollow" href="http://yamuna.womenforsustainablecities.org/">Yamuna's Daughters</a></p></small>
	</div>
	<div class="col-sm-4">
		<a target="_blank" rel="nofollow" href="https://dl.dropboxusercontent.com/u/46576246/India/DSCI0145.JPG"><img src="https://dl.dropboxusercontent.com/u/46576246/India/DSCI0145.JPG" class="img-responsive img-thumbnail"></a>
		<small><p><i class="fa fa-fw fa-lg fa-photo"></i><a target="_blank" rel="nofollow" href="http://yamuna.womenforsustainablecities.org/">Yamuna's Daughters</a></p></small>
	</div>
</div>
<hr>
<p>In this photo there is no water body, large or small, and so you should click <button class="btn btn-xs btn-danger" disabled>No</button></p>
<div class="row">
	<div class="col-sm-4">
		<a target="_blank" rel="nofollow" href="https://dl.dropboxusercontent.com/u/46576246/India/DSCI0074.JPG"><img src="https://dl.dropboxusercontent.com/u/46576246/India/DSCI0074.JPG" class="img-responsive img-thumbnail"></a>
		<small><p><i class="fa fa-fw fa-lg fa-photo"></i><a target="_blank" rel="nofollow" href="http://yamuna.womenforsustainablecities.org/">Yamuna's Daughters</a></p></small>
	</div>
</div>
"""



def print_usage():
	print """Usage: """ + __file__ + """ directory [OPTIONS]
	\rBuild the task presenter for the GeoTag-X project located in the specified directory.
	\rThe following is a list of OPTIONS you can use to modify the script's behavior:\n
\r    -f, --force       overwrites the file 'template.html' in the specified directory.
\r    -c, --compress    compresses the generated HTML file.
\r    -h, --help        prints this help message."""


def has_valid_project(path):
	"""Returns true if the directory with the specified path is writable, and contains a valid GeoTag-X project, false otherwise."""
	return  os.path.isdir(path) \
		and os.access(path, os.W_OK) \
		and os.access(os.path.join(path, "project.json"), os.F_OK | os.R_OK)


def get_project_json(filename):
	"""Converts the project.json file into a JSON object and returns it."""
	with open(filename) as file:
		data = file.read()
		return json.loads(data)


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


def build(path, compress=False):
	"""Builds the task presenter for the project located at the specified path."""
	project_dir = os.path.realpath(path)

	with open(os.path.join(project_dir, "template.html"), "w") as output:
		json = get_project_json(os.path.join(project_dir, "project.json"))
		css_ = get_project_css(os.path.join(project_dir, "project.css"), compress)
		js_  = get_project_js(os.path.join(project_dir, "project.js"), compress)

		env = Environment(loader=FileSystemLoader(searchpath=LAYOUT_DIR))
		template = env.get_template(TEMPLATE)
		html = template.render(css=css_, js=js_, slug=json["short_name"], questions=json["questions"], help=HELP_TEXT)
		html = html if not compress else htmlmin.minify(html, remove_comments=True, remove_empty_space=True)

		output.write(html.encode("UTF-8"))


def main(argv):
	argc = len(argv)
	if argc != 2:
		print_usage()
	else:
		path = argv[1]
		if not path or path in ("-h", "--help"):
			print_usage()
		else:
			if has_valid_project(path):
				build(path)
			else:
				print "The directory '" + path + "' does not contain a valid GeoTag-X project, or you may not have read/write permissions."


if __name__ == "__main__":
	main(sys.argv)
