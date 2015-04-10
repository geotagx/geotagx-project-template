#!/usr/bin/env python
import jinja2
from slimit import minify
from rcssmin import cssmin



TEMPLATE_DIRECTORY = "templates"
TEMPLATE_ENTRY_FILE = "task_presenter.html"

tLoader = jinja2.FileSystemLoader( searchpath="./"+TEMPLATE_DIRECTORY )
tEnv = jinja2.Environment( loader=tLoader )

"""
Collects CSS and JS files, minifies them,
and then embeds them directly into the rendered output
"""
JS_minified = ""
JS_raw = ""
CSS_minified = ""
CSS_raw = ""
def geotagx_collect_js_css():
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

def main():

	template = tEnv.get_template(TEMPLATE_ENTRY_FILE)

	#print template.render()
	geotagx_collect_js_css()


if __name__ == "__main__":
    main()