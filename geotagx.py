#!/usr/bin/env python
import jinja2
from slimit import minify
from rcssmin import cssmin



TEMPLATE_DIRECTORY = "templates"
TEMPLATE_TASK_PRESENTER = "task_presenter.html"
TEMPLATE_STATIC_FILES = "render_static_files.html"

tLoader = jinja2.FileSystemLoader( searchpath="./"+TEMPLATE_DIRECTORY )
tEnv = jinja2.Environment( loader=tLoader )

"""
Instantiates variables for CSS and JS files
"""
JS_minified = ""
JS_raw = ""
CSS_minified = ""
CSS_raw = ""

"""
Resets collected JS and CSS files
"""
def geotagx_reset_js_css():
	global CSS_raw, JS_raw, CSS_minified, JS_minified
	JS_minified = ""
	JS_raw = ""
	CSS_minified = ""
	CSS_raw = ""	
	

"""
Collects CSS and JS files, minifies them,
and then embeds them directly into the rendered output
"""
def geotagx_collect_js_css():
	geotagx_reset_js_css();
	import os
	global CSS_raw, JS_raw, CSS_minified, JS_minified
	for root, dirs, files in os.walk(TEMPLATE_DIRECTORY+"/static", topdown=False):
		for name in files:
			if name.split(".")[-1] == "css":
				CSS_raw += open(os.path.join(root, name),"r").read()
			if name.split(".")[-1] == "js":
				JS_raw += open(os.path.join(root, name),"r").read()
	CSS_minified = cssmin(CSS_raw, keep_bang_comments=False)
	JS_minified = minify(JS_raw)

"""
Renders the task task_presenter after collecting the necessary data
"""
def geotagx_render_task_presenter():
	#Collect JS and CSS files
	geotagx_collect_js_css()
	#Render minified CSS and JS files
	template = tEnv.get_template(TEMPLATE_TASK_PRESENTER)
	return template.render(js=JS_minified, css=CSS_minified)

def main():
	print geotagx_render_task_presenter()
	

if __name__ == "__main__":
    main()