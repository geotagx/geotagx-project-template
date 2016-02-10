# This module is part of the GeoTag-X project builder.
# Copyright (C) 2016 UNITAR-UNOSAT.
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
import os
from questionnaire import Questionnaire
from tutorial import Tutorial

class Project:
	path = None
	name = None
	slug = None
	description = None
	why = None
	questionnaire = None
	tutorial = None
	language = None
	subjecttype = None


	def __init__(self, path):
		"""__init__(path:string)
		Instantiates a Project object for the GeoTag-X project located at the
		specified path, a path that must point to a readable directory that
		contains a valid project configuration file, and optionally, a tutorial
		configuration file.
		"""
		if not os.path.isdir(path) or not os.access(path, os.R_OK):
			raise IOError("The path '{}' does not point to a readable directory.".format(path))

		config = Project.getconfiguration(path)
		if config is None:
			raise IOError("The directory '{}' does not contain a GeoTag-X project configuration file or you may not have sufficient access permissions.".format(path))
		else:
			from src.i18n import i18nify

			# Check for mandatory keys.
			for field in ["name", "short_name", "description", "why", "questionnaire"]:
				if field not in config:
					raise Exception("Error! The project configuration is missing the field '{}'.".format(field))

			self.path = os.path.realpath(path)
			self.name = config["name"].strip()
			self.slug = config["short_name"].strip()
			self.description = config["description"].strip()
			self.why = i18nify(config["why"])
			self.questionnaire = Questionnaire(config["questionnaire"])
			self.tutorial = None if config["tutorial"] is None else Tutorial(config["tutorial"])
			self.language = config["language"] if "language" in config else {"default":"en", "available":{"en":"English"}}
			self.subjecttype = str(config["subject-type"]).lower() if "subject-type" in config else "image"

			valid, message = Project.isvalid(self)
			if not valid:
				raise Exception(message)


	def __str__(self):
		"""
		Returns the object in the form of a string.
		"""
		default_language = self.language["default"]
		available_languages = self.language["available"]
		return unicode(
			"{name}\n"
			"{underline}\n"
			"Short name: {slug}\n"
			"Description: {description}\n"
			"Subject type: {subject_type}\n"
			"Default language: {default_language_name}\n"
			"Available languages: {available_language_names}\n"
			"Why: {why}\n"
			"Tutorial included: {has_tutorial}\n"
			"Questionnaire:\n{questionnaire}"
		).format(
			name = self.name,
			underline = ("-" * len(self.name)),
			slug = self.slug,
			description = self.description,
			subject_type = Project.getsubjecttypename(self.subjecttype),
			default_language_name = available_languages[default_language],
			available_language_names = ", ".join(available_languages.itervalues()),
			why = self.why[default_language],
			has_tutorial = "Yes" if self.tutorial is not None and len(self.tutorial) > 0 else "No",
			questionnaire = self.questionnaire
		).encode("utf-8")


	def getjs(self):
		"""
		Returns the project's custom javascript, if it exists.
		"""
		js = ""
		try:
			with open(os.path.join(self.path, "project.js"), "r") as file:
				data = file.read().decode('utf-8')
				if data is not None:
					import slimit
					data = slimit.minify(data, mangle=True)
					if len(data) > 0:
						js = data
		except IOError:
			# Since the 'project.js' file is not a requirement and is therefore
			# not guaranteed to exist or be accessible, the I/O error can be
			# safely ignored.
			pass

		return js


	def getcss(self):
		"""
		Returns the project's custom stylesheet, if it exists.
		"""
		css = ""
		try:
			with open(os.path.join(self.path, "project.css"), "r") as file:
				data = file.read().decode('utf-8')
				if data is not None:
					import rcssmin
					data = rcssmin.cssmin(data)
					if len(data) > 0:
						css = data
		except IOError:
			# Like with the getjs method, we can safely ignore any I/O error.
			pass

		return css


	def get_required_assets(self):
		"""
		Returns the names of asset bundles required by this project.
		"""
		requirements = set()
		for t in self.questionnaire.questiontypes:
			if "geolocation" not in requirements and t in {"geotagging"}:
				requirements.add("geolocation")
			elif "datetime" not in requirements and t in {"date", "datetime"}:
				requirements.add("datetime")

		if len(self.language["available"]) > 1:
			requirements.add("multilanguage")

		return requirements


	@staticmethod
	def getconfiguration(path):
		"""getconfigurations(path:string)
		Returns the project configuration for the GeoTag-X project located at
		the specified path. If a tutorial configuration exists, it is included
		in the returned object.
		"""
		configuration = None
		if path is not None and len(path) > 0:
			import json, yaml
			parsers = {
				".json":lambda file: json.loads(file.read()),
				".yaml":lambda file: yaml.load(file)
			}
			configuration = Project.getprojectconfiguration(path, parsers)
			if configuration is not None:
				configuration["tutorial"] = Project.gettutorialconfiguration(path, parsers)

		return configuration


	@staticmethod
	def getprojectconfiguration(path, parsers):
		"""getprojectconfiguration(path:string, parsers:dict)
		Returns the project configuration for the project located at the
		specified path.
		"""
		for filename in ["project.json", "project.yaml"]:
			filename = os.path.join(path, filename)
			if os.access(filename, os.F_OK | os.R_OK):
				extension = os.path.splitext(filename)[1]
				parser = parsers.get(extension)
				if parser:
					with open(filename) as file:
						configuration = parser(file)
						if configuration is not None:
							return configuration
				else:
					print "Error! Could not find a suitable configuration file parser for the extension '{}'.".format(extension)

		return None


	@staticmethod
	def gettutorialconfiguration(path, parsers):
		"""gettutorialconfiguration(path:string, parsers:dict)
		Returns the tutorial configuration for the project located at the
		specified path.
		"""
		for filename in ["tutorial.json", "tutorial.yaml"]:
			filename = os.path.join(path, filename)
			if os.access(filename, os.F_OK | os.R_OK):
				extension = os.path.splitext(filename)[1]
				parser = parsers.get(extension)
				if parser:
					with open(filename) as file:
						configuration = parser(file)
						if configuration is not None:
							return configuration.get("tutorial")
				else:
					print "Error! Could not find a suitable configuration file parser for the extension '{}'.".format(extension)

		return None


	@staticmethod
	def getsubjecttypename(subjecttype):
		"""getsubjecttypename(subjecttype:string)
		Returns the human-readable name for the specified subject type.
		"""
		return {
			"image":"Image",
			"pdf":"Portable Document Format (PDF)"
		}.get(subjecttype, "Unknown")


	@staticmethod
	def isvalid(project):
		"""isvalid(project:Project)
		Returns true if this project is valid, false otherwise.
		"""
		# Note that the Questionnaire object is validated upon instantiation.
		validations = [
			(Project.isname,        project.name),
			(Project.isslug,        project.slug),
			(Project.isdescription, project.description),
			(Project.iswhy,         project.why),
			(Project.istutorial,    project.tutorial),
			(Project.islanguage,    project.language),
			(Project.issubjecttype, project.subjecttype)
		]
		for validator, field in validations:
			valid, message = validator(field)
			if not valid:
				return (False, message)

		return (True, None)


	@staticmethod
	def isname(name):
		"""isname(name:string)
		Returns true if the specified name is valid, false otherwise.
		"""
		return (True, None)


	@staticmethod
	def isslug(short_name):
		"""isslug(slug:string)
		Returns true if the specified slug (short name) is valid, false otherwise.
		"""
		return (True, None)


	@staticmethod
	def isdescription(description):
		"""isdescription(description:string)
		Returns true if the specified description is valid, false otherwise.
		"""
		return (True, None)


	@staticmethod
	def iswhy(why):
		"""iswhy(why:string)
		Returns true if the specified reason is valid, false otherwise.
		"""
		return (True, None)


	@staticmethod
	def istutorial(tutorial):
		"""iswhy(tutorial:dict)
		Returns true if the specified tutorial is valid, false otherwise.
		"""
		return Tutorial.isvalid(tutorial)


	@staticmethod
	def islanguage(language):
		"""islanguage(language:dict)
		Returns true if the specified language configuration is valid, false otherwise.
		"""
		if language is not None:
			from src.i18n import isiso6391

			# Check for mandatory keys.
			for key in ["default", "available"]:
				if key not in language:
					return (False, "Error! The language configuration is missing the '%s' key." % key)

			# Make sure each available language has a valid ISO 639-1 code, and a human-readable name.
			available_languages = language["available"]
			for key in available_languages:
				if not isiso6391(key):
					return (False, "Error! '%s' is not a valid ISO 639-1 code. Please correct your project's language configuration." % key)
				elif not available_languages[key].strip():
					return (False, "Error! The language '%s' does not have a human-readable name. Please correct your project's language configuration." % key)

			# Make sure the default language value is part of the available languages.
			default_language = language["default"].strip()
			if default_language and default_language not in available_languages:
				return (False, "Error! There is no language with the code '%s' in the project's available languages." % default_language)
			elif not default_language:
				return (False, "Error! The project's language configuration is missing a default language.")

			return (True, None)
		else:
			return (False, "Error! The project's language configuration is empty.")


	@staticmethod
	def issubjecttype(type):
		"""iswhy(type:string)
		Returns true if the specified type is a recognized subject type, false otherwise.
		"""
		types = {"image", "pdf"}
		return (True, None) if type in types else (False, "Error! The subject type '%s' is not recognized. Please check your project's 'subject-type' configuration." % type)




class ProjectX:
	path = None
	name = None
	short_name = None
	description = None
	task_presenter = None
	tutorial = None

	def __init__(
		self,
		path,
		project_configuration_filename="project.json",
		task_presenter_configuration_filename="task_presenter.json",
		tutorial_configuration_filename="tutorial.json"
	):
		"""__init__(self:Project, path:string, project_configuration_filename:string, task_presenter_configuration_filename:string, tutorial_configuration_filename:string)
		Instantiates a Project object for the GeoTag-X project located at the specified path.
		The path must point to a readable directory that contains valid project, task presenter,
		and, optionally, tutorial configuration files.
		"""
		if not os.path.isdir(path) or not os.access(path, os.R_OK):
			raise IOError("could not access '%s'. Please make sure the directory exists and that you have sufficient access permissions." % path)

		filename = os.path.join(path, project_configuration_filename)
		configuration = ProjectX.load_configuration(filename)
		self.path = path
		self.name = configuration["name"]
		self.short_name = configuration["short_name"]
		self.description = configuration["description"]

		# Load the project's task presenter.
		from project_task_presenter import ProjectTaskPresenter
		filename = os.path.join(path, task_presenter_configuration_filename)
		configuration = ProjectTaskPresenter.load_configuration(filename)
		self.task_presenter = ProjectTaskPresenter(configuration)

		# Load the project's tutorial.
		from project_tutorial import ProjectTutorial
		filename = os.path.join(path, tutorial_configuration_filename)
		configuration = ProjectTutorial.load_configuration(filename)
		self.tutorial = ProjectTutorial(self.task_presenter, configuration)


	@staticmethod
	def load_configuration(filename):
		"""load_configuration(filename:string)
		Returns a project configuration from the file with the specified filename.
		If the file does not contain a valid configuration, a ProjectError exception is raised.
		"""
		from utils import load_configuration
		configuration = load_configuration(filename)
		valid, message = ProjectValidator.is_valid_configuration(configuration)
		if not valid:
			raise ProjectError(message)

		return configuration


	def __str__(self):
		"""
		Returns the project's string representation.
		"""
		return unicode(
			"{name}\n"
			"{underline}\n"
			"PATH: {path}\n"
			"SHORT NAME: {short_name}\n"
			"DESCRIPTION: {description}\n"
			"{task_presenter}\n"
			"{tutorial}"
		).format(
			name = self.name,
			underline = ("-" * len(self.name)),
			path = self.path,
			short_name = self.short_name,
			description = self.description,
			task_presenter = self.task_presenter,
			tutorial = self.tutorial
		).encode("utf-8")




class ProjectValidator:
	@staticmethod
	def is_valid_configuration(configuration):
		"""is_valid_configuration(configuration:dict)
		Returns true if the specified configuration is valid, false otherwise.
		"""
		# Check for mandatory keys.
		for field in ["name", "short_name", "description"]:
			if field not in configuration:
				return (False, "the project configuration is missing the field '%s'." % field)

		validations = [
			(ProjectValidator.is_valid_name,        configuration["name"]),
			(ProjectValidator.is_valid_short_name,  configuration["short_name"]),
			(ProjectValidator.is_valid_description, configuration["description"])
		]
		for validator, field in validations:
			valid, message = validator(field)
			if not valid:
				return (False, message)


		return (True, None)


	@staticmethod
	def is_valid_name(name):
		"""is_valid_name(name:string)
		Returns true if the specified project name is valid, false otherwise.
		"""
		if not isinstance(name, basestring):
			return (False, "the project name is not a string.")
		else:
			if not name.strip():
				return (False, "the project name is empty.")
			else:
				return (True, None)

		return (True, None)


	@staticmethod
	def is_valid_short_name(short_name):
		"""isslug(short_name:string)
		Returns true if the specified project short name is valid, false otherwise.
		"""
		if not isinstance(short_name, basestring):
			return (False, "the project short name is not a string.")
		else:
			if not short_name.strip():
				return (False, "the project short name is empty.")
			else:
				from re import match
				matches = match(r"[a-zA-Z0-9-_]+", short_name)
				if matches is None or matches.group() != short_name:
					return (False, "the project short name contains an invalid character. A short name may only be comprised of alphanumeric characters (a-z, 0-9), hyphens (-) and underscores (_).")

		return (True, None)


	@staticmethod
	def is_valid_description(description):
		"""is_valid_description(description:string)
		Returns true if the specified project description is valid, false otherwise.
		"""
		if not isinstance(description, basestring):
			return (False, "the project description is not a string.")
		else:
			if not description.strip():
				return (False, "the project description is empty.")

		return (True, None)




class ProjectError(Exception):
	pass
