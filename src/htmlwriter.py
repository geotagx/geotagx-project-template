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


	def __init__(self, theme, compress, overwrite, verbose):
		self.theme     = theme
		self.compress  = compress
		self.overwrite = overwrite
		self.verbose   = verbose


	def is_writable_directory(self, path):
		"""is_writable_directory(self:HtmlWriter, path:string)
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

		tp = project.task_presenter

		task_presenter_css, task_presenter_js = self.theme.getassets(tp.get_asset_bundles())
		task_presenter_css += tp.get_custom_css()
		task_presenter_js += tp.get_custom_js()

		# Set the variables required to render the project's task presenter.
		context = {
			"name":project.name,
			"short_name":project.short_name,
			"description":project.description,
			"why":tp.why,
			"questionnaire":tp.questionnaire,
			"default_language":tp.locale["default"],
			"available_languages":tp.locale["available"],
			"subject_type":tp.subject["type"],
			"pdfmode":(tp.subject["type"] == "pdf"), # TODO Remove this when it is no longer used in the project theme.
			"is_tutorial":False,
			"js":task_presenter_js,
			"css":task_presenter_css,
		}

		# Write the project's task presenter.
		with open(os.path.join(project.path, "template.html"), "w") as output:
			self.__render(context, output)

		# Write the project's tutorial. Note that if no tutorial configuration
		# exists, an empty 'tutorial.html' file is still created as it is a
		# requirement for PyBossa's 'pbs' tool.
		with open(os.path.join(project.path, "tutorial.html"), "w") as output:
			if project.tutorial is not None:
				tutorial_css, tutorial_js = self.theme.getasset("tutorial")
				tutorial_css += tutorial.get_custom_css()
				tutorial_js += tutorial.get_custom_js()

				# Extend the context with variables required to render the the project's tutorial.
				context["tutorial_exercises"] = project.tutorial.exercises
				context["tutorial_length"] = len(project.tutorial)
				context["is_tutorial"] = True
				context["css"] += tutorial_css
				context["js"] += tutorial_js

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
			# Convert the control-flow graph and tutorial exercises into pure
			# Javascript objects.
			import json
			project.task_presenter.questionnaire.branches = json.dumps(project.task_presenter.questionnaire.branches)
			project.tutorial.exercises = json.dumps(project.tutorial.exercises)

			# Load questionnaire help, if it exists.
			questions = project.task_presenter.questionnaire.questions
			helpdir = os.path.join(project.path, "help")
			if os.path.isdir(helpdir) and os.access(helpdir, os.R_OK):
				for filename in [os.path.join(helpdir, f) for f in os.listdir(helpdir) if f.endswith(".html") and len(f) > 5]:
					key = os.path.splitext(os.path.basename(filename))[0]
					if key in questions:
						with open(filename) as file:
							help = file.read().decode('utf-8').strip()
							if len(help) > 0:
								questions[key].help = help

		return project
