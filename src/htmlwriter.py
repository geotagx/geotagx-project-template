# This module is part of the GeoTag-X project builder.
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
import os, jinja2

# TODO Find out what this does.
import sys, locale, codecs; sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

class HtmlWriter:
	templatedir = None
	template    = None
	js          = {"core":None, "geotagging":None, "datetime":None}
	css         = {"core":None, "geotagging":None, "datetime":None}
	compress    = None
	overwrite   = None
	inline      = None


	def __init__(self, templatedir, compress, overwrite, inline):
		self.templatedir = templatedir.strip()
		self.template    = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=self.templatedir)).get_template("base.html")
		self.compress    = compress
		self.overwrite   = overwrite
		self.inline      = inline


	def iswritabledir(self, path):
		"""iswritabledir(path:string)
		Returns true if the path points to a writable directory, false otherwise.
		This method will also return false if the path contains an existing
		task presenter (template.html) and tutorial (tutorial.html), and the
		overwrite flag is set to false.
		"""
		if not os.path.isdir(path):
			return (False, "The path '{}' does not point to a directory, or you may not have sufficient access permissions.".format(path))
		elif not os.access(path, os.W_OK):
			return (False, "The path '{}' does not point to a writable directory.".format(path))
		elif not self.overwrite and (os.access(os.path.join(path, "template.html"), os.F_OK) or os.access(os.path.join(path, "tutorial.html"), os.F_OK)):
			return (False, "The directory '{}' already contains either a task presenter and or a tutorial. To overwrite them, set the '-f' or '--force' flag.".format(path))
		else:
			return (True, None)


	def getjs(self, project):
		"""getjs(project:Project)
		Returns the concatenated template and project javascript files for the
		specified project.
		"""
		# TODO Filter out unnecessary javascript files.
		js = ""

		for root, __, filenames in os.walk(os.path.join(self.templatedir, *["static","js"]), topdown=False):
			for filename in filter(lambda f: f.endswith(".js"), filenames):
				js += open(os.path.join(root, filename), "r").read()

		projectjs = project.getjs()
		if projectjs is not None:
			js += projectjs

		return js if len(js) > 0 else None


	def getcss(self, project):
		"""getcss(project:Project)
		Returns the concatenated template and project stylesheets for the specified project.
		"""
		# TODO Filter out unnecessary stylesheets.
		css = ""

		for root, __, filenames in os.walk(os.path.join(self.templatedir, *["static","css"]), topdown=False):
			for filename in filter(lambda f: f.endswith(".css"), filenames):
				css += open(os.path.join(root, filename), "r").read()

		projectcss = project.getcss()
		if projectcss is not None:
			css += projectcss

		return css if len(css) > 0 else None


	def write(self, project):
		"""write(project:Project)
		Writes the specified project's task presenter and tutorial.
		"""
		project = HtmlWriter.__preprocess(project)
		js, css = self.getjs(project), self.getcss(project)
		context = {
			"name":project.name,
			"slug":project.slug,
			"description":project.description,
			"why":project.why,
			"questionnaire":project.questionnaire,
			"istutorial":False,
			"js":js,
			"css":css
		}
		with open(os.path.join(project.path, "template.html"), "w") as output:
			self.__render(context, output)

		if project.tutorial is not None:
			with open(os.path.join(project.path, "tutorial.html"), "w") as output:
				# FIXME Set correct js and css
				# context["js"] = None
				# context["css"] = None
				context["tutorial"] = project.tutorial
				context["istutorial"] = True

				self.__render(context, output)


	def __render(self, context, f):
		"""__render(context:dict, f:file)
		Renders a Jinja2 template in the given context, to the specified file in HTML format.
		"""
		html = self.template.render(context)
		if html is not None and len(html) > 0:
			if self.compress:
				import htmlmin
				html = htmlmin.minify(html, remove_comments=True, remove_empty_space=True)

			f.write(html.encode("UTF-8"))


	@staticmethod
	def __preprocess(project):
		# TODO Document me.
		if project is not None:
			# Convert the tutorial and control-flow dictionaries into Javascript
			# map objects.
			import json
			project.questionnaire.controlflow = json.dumps(project.questionnaire.controlflow)
			project.tutorial = json.dumps(project.tutorial.get("tutorial"))

			# Load questionnaire help.
			helpdir = os.path.join(project.path, "help")
			filenames = [os.path.join(helpdir, f) for f in os.listdir(helpdir) if f.endswith(".html") and len(f) > 5]
			for filename in filenames:
				key = os.path.splitext(os.path.basename(filename))[0]
				if key in project.questionnaire.questions:
					with open(filename) as file:
						help = file.read().strip()
						if len(help) > 0:
							project.questionnaire.questions[key].help = help

		return project


	@staticmethod
	def findcss(path):
		"""findcss(path:string)
		Returns an array of paths to all the stylesheets contained in the
		parent directory specified by the given path.
		"""
		output = None
		if path is not None and len(path) > 0:
			output = []
			for root, __, files in os.walk(path):
				output.extend([(root + f) for f in files if f.endswith(".css")])

		return output


	@staticmethod
	def findjs(path):
		"""findjs(path:string)
		Returns an array of paths to all the javascript files contained in the
		parent directory specified by the given path.
		"""

		# js = ""
		# for root, dirs, filenames in os.walk(JS_DIR, topdown=False):
		# 	for filename in filter(lambda f: f.endswith(".js"), filenames):
		# 		js += open(os.path.join(root, filename), "r").read()
		#
		# return js if not compress else minify(js)



		output = None
		if path is not None and len(path) > 0:
			output = []
			for root, __, files in os.walk(path):
				output.extend([(root + f) for f in files if f.endswith(".js")])

		return output


	@staticmethod
	def isreservedkeyword(keyword):
		"""isreservedkeyword(keyword:string)
		Returns true if the specified keyword is reserved for internal use by
		the HtmlWriter, false otherwise.
		"""
		return keyword in [
			"end",
			"photoVisible",
		]
