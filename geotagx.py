#!/usr/bin/env python
import jinja2


TEMPLATE_DIRECTORY = "templates"
TEMPLATE_ENTRY_FILE = "task_presenter.html"
SCRIPTS = []
CSS = []

tLoader = jinja2.FileSystemLoader( searchpath="./"+TEMPLATE_DIRECTORY )
tEnv = jinja2.Environment( loader=tLoader )

"""
Collects CSS and JS files, minifies them,
and then embeds them directly into the rendered output
"""
def geotagx_collect_js_css():
	import os
	for root, dirs, files in os.walk(TEMPLATE_DIRECTORY+"/static", topdown=False):
		for name in files:
			print(os.path.join(root, name))

def main():

	template = tEnv.get_template(TEMPLATE_ENTRY_FILE)

	#print template.render()
	geotagx_collect_js_css()


if __name__ == "__main__":
    main()