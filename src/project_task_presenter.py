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
class ProjectTaskPresenter:
	DEFAULT_LOCALE = "en-GB"

	def __init__(self, project, configuration):
		"""__init__(configuration:dict)
		Instantiates a ProjectTaskPresenter object from the specified configuration.
		"""
		from project import Project
		assert isinstance(project, Project), "project is not a Project instance."

		valid, message = ProjectTaskPresenterValidator.is_valid_configuration(configuration)
		if not valid:
			raise ProjectTaskPresenterError(message)

		from question import Questionnaire
		self.project = project
		self.locale = configuration["locale"]
		self.why = configuration["why"]
		self.subject = configuration["subject"]
		self.questionnaire = Questionnaire(configuration["questionnaire"])


	def get_asset_bundles(self):
		"""get_asset_bundles(self:ProjectTaskPresenter)
		Returns the names of asset bundles required by this task presenter.
		"""
		bundles = set(["core"])

		if len(self.locale["available"]) > 1 or self.locale["default"] != ProjectTaskPresenter.DEFAULT_LOCALE:
			bundles.add("multilanguage")

		for t in self.questionnaire.get_question_types():
			if "geolocation" not in bundles and t in {"geotagging"}:
				bundles.add("geolocation")
			elif "datetime" not in bundles and t in {"date", "datetime"}:
				bundles.add("datetime")

		return bundles


	def get_custom_js(self):
		"""get_custom_js(self:ProjectTaskPresenter)
		Returns the task presenter's custom javascript, if it exists.
		"""
		try:
			import os, utils
			return utils.load_js(os.path.join(self.project.path, "task_presenter.js"))
		except IOError:
			# Since the 'task_presenter.js' file is not a requirement and is therefore
			# not guaranteed to exist or be accessible, the I/O error can be
			# safely ignored.
			pass


	def get_custom_css(self):
		"""get_custom_css(self:ProjectTaskPresenter)
		Returns the task presenter's custom stylesheet, if it exists.
		"""
		try:
			import os, utils
			return utils.load_css(os.path.join(self.project.path, "task_presenter.css"))
		except IOError:
			# Since the 'task_presenter.css' file is not a requirement and is therefore
			# not guaranteed to exist or be accessible, the I/O error can be
			# safely ignored.
			pass


	@staticmethod
	def load_configuration(filename):
		"""load_configuration(filename:string)
		Loads the task presenter configuration from the file with the specified filename.
		"""
		import utils
		configuration = utils.load_configuration(filename)
		try:
			configuration = configuration["task-presenter"]
			configuration["locale"] = ProjectTaskPresenter.parse_locale_configuration(configuration.get("locale"))
			locale = configuration["locale"]["default"]
			configuration["why"] = ProjectTaskPresenter.parse_why_configuration(configuration["why"], locale)
			configuration["subject"] = ProjectTaskPresenter.parse_subject_configuration(configuration.get("subject"))
			configuration["questionnaire"] = ProjectTaskPresenter.parse_questionnaire_configuration(configuration["questionnaire"], locale)
		except KeyError as error:
			raise ProjectTaskPresenterError("the task presenter configuration is missing the field %s." % error)

		return configuration


	@staticmethod
	def parse_locale_configuration(configuration):
		"""parse_locale_configuration(configuration:dict)
		Returns an object containing the locale configuration, built from the
		specified configuration. If the configuration is not specified, then
		the default locale configuration is returned.
		"""
		if configuration:
			valid, message = ProjectTaskPresenterValidator.is_valid_locale_configuration(configuration)
			if valid:
				return configuration
			else:
				raise ProjectTaskPresenterError(message)
		else:
			return {
				"default":ProjectTaskPresenter.DEFAULT_LOCALE,
				"available":[ProjectTaskPresenter.DEFAULT_LOCALE]
			}


	@staticmethod
	def parse_why_configuration(configuration, default_locale):
		valid, message = ProjectTaskPresenterValidator.is_valid_why_configuration(configuration)
		if not valid:
			raise ProjectTaskPresenterError(message)

		import multilanguage as ml
		normalized, _ = ml.is_normalized(configuration)
		return configuration if normalized else ml.normalize_string(configuration, default_locale)


	@staticmethod
	def parse_subject_configuration(configuration):
		if configuration:
			valid, message = ProjectTaskPresenterValidator.is_valid_subject_configuration(configuration)
			if not valid:
				raise ProjectTaskPresenterError(message)
			return configuration
		else:
			# If there's no configuration, return a default configuration.
			return {
				"type":"image"
			}


	@staticmethod
	def parse_questionnaire_configuration(configuration, default_locale):
		from question import QuestionnaireValidator
		valid, message = QuestionnaireValidator.is_valid_configuration(configuration)
		if not valid:
			raise ProjectTaskPresenterError(message)

		from question import Question, QuestionValidator, QuestionError
		for question_configuration in configuration["questions"]:
			valid, message = QuestionValidator.is_valid_configuration(question_configuration)
			if not valid:
				raise QuestionError(message)

			# Add any missing parameters to the configuration.
			type = question_configuration["type"]
			if type in Question.DEFAULT_PARAMETERS and Question.DEFAULT_PARAMETERS[type]:
				default_parameters = Question.DEFAULT_PARAMETERS[type]
				current_parameters = question_configuration.get("parameters", {})
				for key in [k for k in default_parameters if k not in current_parameters]:
					current_parameters[key] = default_parameters[key]

				question_configuration["parameters"] = current_parameters

			# Normalize translatable question strings.
			import multilanguage as ml

			translatable = {"title", "hint"}
			available = [key for key in translatable if key in question_configuration]
			for key in available:
				normalized, _ = ml.is_normalized(question_configuration[key])
				if not normalized:
					question_configuration[key] = ml.normalize_string(question_configuration[key], default_locale)

			# Normalize translatable question parameters.
			parameters = question_configuration.get("parameters") # Remember, binary questions do not have parameters.
			if parameters:
				translatable = {"prompt", "placeholder"}
				available = [key for key in translatable if key in parameters]
				for key in available:
					normalized, _ = ml.is_normalized(parameters[key])
					if not normalized:
						parameters[key] = ml.normalize_string(parameters[key], default_locale)

				# Normalize labels for questions with multiple inputs.
				options = parameters.get("options", {})
				for option in options:
					normalized, _ = ml.is_normalized(option["label"])
					if not normalized:
						option["label"] = ml.normalize_string(option["label"], default_locale)

		return configuration


	@staticmethod
	def get_subject_type_name(type):
		"""get_subject_type_name(type:string)
		Returns the human-readable name for the specified subject type.
		"""
		return {
			"image":"Image",
			"pdf":"Portable Document Format (PDF)"
		}.get(type, "Unknown")


	def __str__(self):
		"""
		Returns the task presenter's string representation.
		"""
		default_locale = self.locale["default"]
		available_locales = self.locale["available"]
		return unicode(
			"TASK PRESENTER:\n"
			"* Default locale: {default_locale}\n"
			"* Available locales: {available_locales}\n"
			"* Subject type: {subject_type}\n"
			"* Why: {why}\n"
			"* Asset bundles: {asset_bundles}\n"
			"* Questionnaire:\n{questionnaire}"
		).format(
			default_locale = default_locale,
			available_locales = ", ".join(available_locales),
			subject_type = ProjectTaskPresenter.get_subject_type_name(self.subject["type"]),
			why = self.why[default_locale],
			asset_bundles = ", ".join(self.get_asset_bundles()),
			questionnaire = self.questionnaire
		).encode("utf-8")




class ProjectTaskPresenterValidator:
	@staticmethod
	def is_valid_configuration(configuration):
		"""is_valid_configuration(configuration:dict)
		Returns true if the specified configuration can create a valid task presenter,
		false otherwise.
		"""
		return (True, None)


	@staticmethod
	def is_valid_locale_configuration(configuration):
		"""is_valid_locale_configuration(configuration:dict)
		Returns true if the specified configuration is a valid locale configuration,
		false otherwise.
		"""
		return (True, None)


	@staticmethod
	def is_valid_why_configuration(configuration):
		"""is_valid_why_configuration(configuration:dict)
		Returns true if the specified configuration is a valid 'why' configuration,
		false otherwise.
		"""
		return (True, None)


	@staticmethod
	def is_valid_subject_configuration(configuration):
		"""is_valid_subject_configuration(configuration:dict)
		Returns true if the specified configuration is a valid subject configuration,
		false otherwise.
		"""
		return (True, None)




class ProjectTaskPresenterError(Exception):
	pass
