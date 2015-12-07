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
import os
from src.questionnaire import Questionnaire
from src.tutorial import Tutorial

class Project:
	path = None
	name = None
	slug = None
	description = None
	why = None
	questionnaire = None
	tutorial = None


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

			valid, message = Project.isvalid(self)
			if not valid:
				raise Exception(message)


	def __str__(self):
		"""
		Returns the object in the form of a string.
		"""
		return (
			"{name}\n"
			"{underline}\n"
			"Short name: {slug}\n"
			"Description: {description}\n"
			"Why: {why}\n"
			"Tutorial included: {has_tutorial}\n"
			"Questionnaire:\n{questionnaire}"
		).format(
			name = self.name,
			underline = ("-" * len(self.name)),
			slug = self.slug,
			description = self.description,
			why = self.why,
			has_tutorial = "Yes" if self.tutorial is not None and len(self.tutorial) > 0 else "No",
			questionnaire = self.questionnaire
		)


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
			if t in {"geotagging"}:
				requirements.add("geolocation")
			elif t in {"date", "datetime"}:
				requirements.add("datetime")

		if self.questionnaire.languages is not None and len(self.questionnaire.languages) > 1:
			requirements.add("i18n")

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
			(Project.istutorial,    project.tutorial)
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
