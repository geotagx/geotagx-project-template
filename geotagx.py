#!/usr/bin/env python
import jinja2
from slimit import minify
from rcssmin import cssmin


import codecs, locale, sys
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout) 

"""
Temporary Variables for debugging
"""

HELP_TEXT="""
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
	return template.render(js=JS_minified, css=CSS_minified, help_html=HELP_TEXT, slug="geotagx_project_template")

def main():
	print geotagx_render_task_presenter()
	

if __name__ == "__main__":
    main()