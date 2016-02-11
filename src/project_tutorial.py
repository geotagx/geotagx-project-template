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
class ProjectTutorial:
	def __init__(self, task_presenter, configuration):
		"""__init__(self:Tutorial, task_presenter:TaskPresenter, configuration:dict)
		Instantiates a ProjectTutorial object from the specified configuration, and
		that is bound to the given task presenter.
		"""
		from project_task_presenter import ProjectTaskPresenter
		assert isinstance(task_presenter, ProjectTaskPresenter), "task_presenter is not a ProjectTaskPresenter instance."

		valid, message = ProjectTutorialValidator.is_valid_configuration(configuration)
		if not valid:
			raise ProjectTutorialError(message)

		self.exercises = configuration["exercises"]


	def get_custom_js(self):
		"""get_custom_js(self:ProjectTutorial)
		Returns the tutorial's custom javascript, if it exists.
		"""
		try:
			import os, utils
			return utils.load_js(os.path.join(self.project.path, "tutorial.js"))
		except IOError:
			# Since the 'tutorial.js' file is not a requirement and is therefore
			# not guaranteed to exist or be accessible, the I/O error can be
			# safely ignored.
			pass


	def get_custom_css(self):
		"""get_custom_css(self:ProjectTutorial)
		Returns the tutorial's custom stylesheet, if it exists.
		"""
		try:
			import os, utils
			return utils.load_css(os.path.join(self.project.path, "tutorial.css"))
		except IOError:
			# Since the 'tutorial.css' file is not a requirement and is therefore
			# not guaranteed to exist or be accessible, the I/O error can be
			# safely ignored.
			pass


	@staticmethod
	def load_configuration(filename, default_locale):
		"""load_configuration(filename:string, default_locale:string)
		Loads the tutorial configuration from the file with the specified filename.
		"""
		import utils
		configuration = utils.load_configuration(filename)
		try:
			configuration = configuration["tutorial"]
			ProjectTutorial.sanitize_exercises_configuration(configuration["exercises"], default_locale)
		except KeyError as error:
			raise ProjectTutorialError("the tutorial configuration is missing the field %s." % error)

		return configuration


	@staticmethod
	def sanitize_exercises_configuration(configuration, locale):
		"""sanitize_exercises_configuration(configuration:dict, locale:string)
		Sanitizes an object containing the exercises configuration.
		"""
		if not isinstance(configuration, list):
			raise ProjectTutorialError("the tutorial configuration's 'exercises' field is not a list.")

		for exercise_configuration in configuration:
			ProjectTutorial.sanitize_exercise_configuration(exercise_configuration, locale)


	@staticmethod
	def sanitize_exercise_configuration(configuration, locale):
		"""sanitize_exercise_configuration(configuration:dict, locale:string)
		Sanitizes an object containing an exercise configuration.
		Any optional fields that are missing are added to the configuration with
		their respective default values. Furthermore, all translatable strings
		are normalized.
		"""
		valid, message = ProjectTutorialValidator.is_valid_exercise_configuration(configuration)
		if not valid:
			raise ProjectTutorialError(message)


	def __len__(self):
		"""
		Returns the number of exercises in this tutorial.
		"""
		return 0 if self.exercises is None else len(self.exercises)


	def __str__(self):
		"""
		Returns the tutorial's string representation.
		"""
		return (
			"TUTORIAL:\n"
			"* Number of exercises: {number_of_exercises}"
		).format(
			number_of_exercises = len(self)
		)




class ProjectTutorialValidator:
	@staticmethod
	def is_valid_configuration(configuration):
		"""is_valid_configuration(configuration:dict)
		Returns true if the specified project tutorial configuration is valid, false otherwise.
		"""
		return (True, None)

		if configuration is None or len(configuration) < 1:
			raise Exception("Error! The configuration object does not contain a valid tutorial.")

		self.entries = configuration


	@staticmethod
	def is_valid_exercise_configuration(configuration):
		"""is_valid_exercise_configuration(configuration:dict)
		Returns true if the specified configuration can be used to instantiate
		a tutorial exercise, false otherwise.
		"""
		return (True, None)




class ProjectTutorialError(Exception):
	pass
