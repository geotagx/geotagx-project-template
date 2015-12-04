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
	theme     = None
	compress  = None
	overwrite = None
	verbose   = None
	pdfmode   = False


	def __init__(self, theme, compress, overwrite, pdfmode, verbose):
		self.theme     = theme
		self.compress  = compress
		self.overwrite = overwrite
		self.pdfmode   = pdfmode
		self.verbose   = verbose


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


	def getassets(self, project):
		"""getassets(project:Project)
		Returns the assets for the specified project.
		"""
		# Get theme assets required by the project.
		css, js = self.theme.getassets(project.get_required_assets())

		# Append project-specific assets to the theme assets.
		css += project.getcss()
		js  += project.getjs()

		return css, js


	def write(self, project):
		"""write(project:Project)
		Writes the specified project's task presenter and tutorial.
		"""
		project = HtmlWriter.__preprocess(project)
		css, js = self.getassets(project)
		context = {
			"name":project.name,
			"slug":project.slug,
			"description":project.description,
			"why":project.why,
			"questionnaire":project.questionnaire,
			"istutorial":False,
			"js":js,
			"css":css,
			"pdfmode" : self.pdfmode
		}
		with open(os.path.join(project.path, "template.html"), "w") as output:
			self.__render(context, output)

		with open(os.path.join(project.path, "tutorial.html"), "w") as output:
			# Note that in the event of a non-existent project tutorial configuration,
			# an empty tutorial.html file is created.
			if project.tutorial is not None:
				css, js = self.theme.getasset("tutorial")
				context["tutorial"] = str(project.tutorial)
				context["tutorial_len"] = len(project.tutorial)
				context["istutorial"] = True
				context["pdfmode"] = self.pdfmode
				context["css"] += css
				context["js"] += js

				self.__render(context, output)


	def __render(self, context, f):
		"""__render(context:dict, f:file)
		Renders a Jinja2 template in the given context, to the specified file in HTML format.
		"""
		html = self.theme.template.render(context)
		if html is not None and len(html) > 0:
			if self.compress:
				import htmlmin
				html = htmlmin.minify(html, remove_comments=True, remove_empty_space=True)

			f.write(html.encode("UTF-8"))


	@staticmethod
	def __preprocess(project):
		# TODO Document me.
		if project is not None:
			# Convert the control-flow dictionary into a Javascript object.
			import json
			project.questionnaire.controlflow = json.dumps(project.questionnaire.controlflow)

			# Load questionnaire help, if it exists.
			helpdir = os.path.join(project.path, "help")
			if os.path.isdir(helpdir) and os.access(helpdir, os.R_OK):
				for filename in [os.path.join(helpdir, f) for f in os.listdir(helpdir) if f.endswith(".html") and len(f) > 5]:
					key = os.path.splitext(os.path.basename(filename))[0]
					if key in project.questionnaire.questions:
						with open(filename) as file:
							help = file.read().decode('utf-8').strip()
							if len(help) > 0:
								project.questionnaire.questions[key].help = help

		return project
