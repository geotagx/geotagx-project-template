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
class Project:
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
		import os
		if not os.path.isdir(path) or not os.access(path, os.R_OK):
			raise IOError("could not access '%s'. Please make sure the directory exists and that you have sufficient access permissions." % path)

		filename = os.path.join(path, project_configuration_filename)
		configuration = Project.load_configuration(filename)
		self.path = path
		self.name = configuration["name"]
		self.short_name = configuration["short_name"]
		self.description = configuration["description"]

		# Load the project's task presenter.
		from project_task_presenter import ProjectTaskPresenter
		filename = os.path.join(path, task_presenter_configuration_filename)
		configuration = ProjectTaskPresenter.load_configuration(filename)
		self.task_presenter = ProjectTaskPresenter(self, configuration)

		# Load the project's tutorial.
		from project_tutorial import ProjectTutorial
		filename = os.path.join(path, tutorial_configuration_filename)
		configuration = ProjectTutorial.load_configuration(filename, self.task_presenter.locale["default"])
		self.tutorial = ProjectTutorial(self, configuration)


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
		mandatory_keys = ["name", "short_name", "description"]
		missing_keys = ["'%s'" % key for key in mandatory_keys if key not in configuration]
		if missing_keys:
			return (False, "the project configuration is missing the following key(s): %s." % ", ".join(missing_keys))

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
		A valid project name is simply a non-empty string.
		"""
		from utils import is_nonempty_string
		try:
			return (True, None) if is_nonempty_string(name) else (False, "the project name is empty.")
		except ValueError:
			return (False, "the project name is not a string.")


	@staticmethod
	def is_valid_short_name(short_name):
		"""is_valid_short_name(short_name:string)
		Returns true if the specified project short name is valid, false otherwise.
		A valid short name is a non-empty string that is comprised solely of
		alphanumeric characters (a-z, A-Z, 0-9), hyphes (-) and underscores (_).
		"""
		from utils import is_nonempty_string
		try:
			if is_nonempty_string(short_name):
				from re import match
				matches = match(r"[a-zA-Z0-9-_]+", short_name)
				matched = matches and (matches.group() == short_name)
				return (True, None) if matched else (False, "the project short name contains an invalid character. A short name may only be comprised of alphanumeric characters (a-z, A-Z, 0-9), hyphens (-) and underscores (_).")
			else:
				return (False, "the project short name is empty.")
		except ValueError:
			return (False, "the project short name is not a string.")


	@staticmethod
	def is_valid_description(description):
		"""is_valid_description(description:string)
		Returns true if the specified project description is valid, false otherwise.
		A valid project description is simply a non-empty string.
		"""
		from utils import is_nonempty_string
		try:
			return (True, None) if is_nonempty_string(description) else (False, "the project description is empty.")
		except ValueError:
			return (False, "the project description is not a string.")




class ProjectError(Exception):
	pass
