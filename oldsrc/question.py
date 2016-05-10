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
class Question:
	RESERVED_KEYS = {
		"end",
		"photoAccessible",
		"photoVisible"
	}
	TYPES = {
		"binary",
		"dropdown-list",
		"select",
		"checklist",
		"illustrative-checklist",
		"text",
		"longtext",
		"number",
		"datetime",
		"date",
		"url",
		"geotagging",
		"custom"
	}
	DEFAULT_PARAMETERS = {
		"binary":{},
		"dropdown-list":{
			"options":None,
			"prompt":"Please select an option",
			"size":1
		},
		"select":{
			"options":None,
			"size":8
		},
		"checklist":{
			"options":None,
			"size":8
		},
		"illustrative-checklist":{
			"options":None
		},
		"text":{
			"placeholder":None,
			"maxlength":128
		},
		"longtext":{
			"placeholder":None,
			"maxlength":512
		},
		"number":{
			"placeholder":"Please enter a number",
			"min":None,
			"max":None,
			"maxlength":256
		},
		"datetime":{
			"mindate":None,
			"maxdate":None,
			"mintime":None,
			"maxtime":None
		},
		"date":{
			"min":None,
			"max":None
		},
		"url":{
			"placeholder":"Please enter a URL e.g. http://www.example.com",
			"maxlength":2000
		},
		"geotagging":{
			"location":None
		},
	}


	def __init__(self, configuration):
		"""__init__(self:Question, configuration:dict)
		Instantiates a Question object from the specified configuration.
		"""
		valid, message = QuestionValidator.is_valid_configuration(configuration)
		if not valid:
			raise QuestionError(message)

		self.key = configuration["key"]
		self.type = configuration["type"]
		self.title = configuration["title"]
		self.hint = configuration.get("hint")
		self.help = None
		self.parameters = configuration.get("parameters")


	@staticmethod
	def is_valid_title(title):
		"""is_valid_title(title:dict)
		Returns true if the question is an i18nified object, false otherwise.
		An i18nified object is a dictionary that assigns a string to an ISO 639-1
		language code, for instance {"en":"What is the answer to life?"}. Please
		also note that questions strings must not be empty.
		"""
		from src.i18n import isi18nified

		def isvalid(input):
			"""isvalid(input:string)
			Returns true if the string is non-empty, false otherwise.
			"""
			valid, message = True, None
			if isinstance(input, basestring):
				if len(input.strip()) == 0:
					valid, message = False, "Error! The string must not be empty!"
			else:
				valid, message = False, "Error! The input must be a StringType or UnicodeType."

			return (valid, message)

		return isi18nified(question, isvalid)


	@staticmethod
	def ishint(hint):
		"""ishint(hint:dict)
		Returns true if the hint is valid, false otherwise.
		A hint is optional and can therefore be a NoneType value however if it
		is specified, it must follow the same construction rules as a question
		(see Question.isquestion for more information).
		"""
		return (True, None) if hint is None else Question.isquestion(hint)


	@staticmethod
	def isparameters(parameters):
		"""isparameters(parameters:dict)
		Returns true if the parameters are valid, false otherwise.
		"""
		if parameters is None or isinstance(parameters, dict):
			return (True, None)
		else:
			return (False, "Error! Question parameters must be a dictionary.")




class Questionnaire:
	def __init__(self, configuration):
		"""__init__(self:Questionnaire, configuration:dict)
		Instantiates a Questionnaire object from the specified configuration.
		"""
		valid, message = QuestionnaireValidator.is_valid_configuration(configuration)
		if not valid:
			raise QuestionnaireError(message)

		import collections
		self.questions = collections.OrderedDict()
		self.branches = {}
		for configuration in configuration["questions"]:
			key = configuration["key"]
			self.questions[key] = Question(configuration)
			self.branches[key] = configuration.get("branch")

		valid, message = QuestionnaireValidator.is_valid_branching(self.branches)
		if not valid:
			raise QuestionnaireError(message)


	def get_question(self, key):
		"""get_question(self:Questionnaire, key:string)
		Returns the Question instance with the specified key.
		"""
		return self.questions.get(key)


	def get_question_types(self):
		"""get_question_types(self:Questionnaire)
		Returns a set containing the names of the question types in this questionnaire.
		"""
		return set([question.type for question in self.questions.itervalues()])


	def __str__(self):
		"""
		Returns the questionnaire's string representation.
		"""
		from math import log10
		output = []
		output.append("  + Questions:")
		for i, question in enumerate(self.questions.itervalues(), start=1):
			# Each normalized question title is a <locale ID, string> mapping
			# that contains a translation of the question in a specific language.
			titles = question.title.iteritems()
			(locale, title) = titles.next()
			output.append("    %d. (%s) %s [%s]" % (i, locale, title, question.key))

			# Output all remaining title translations.
			for locale, title in titles:
				whitespace = " " * (int(log10(i)) + 1) # Number of digits in N == log10(N) + 1
				output.append("    %s  (%s) %s" % (whitespace, locale, title))

		return unicode("\n".join(output)).encode("UTF-8") if len(output) > 0 else "Empty questionnaire."


	def __len__(self):
		"""
		Returns the number of questions in this questionnaire.
		"""
		return len(self.questions)




class QuestionValidator:
	@staticmethod
	def is_valid_configuration(configuration):
		"""is_valid_configuration(configuration:dict)
		Returns true if the specified configuration can be used to create a valid
		Question instance, false otherwise.
		"""
		return (True, None)


	@staticmethod
	def is_valid_question(question):
		"""is_valid_question(question:Question)
		Returns true if the specified question object is a valid Question instance,
		false otherwise.
		"""
		validations = {
			QuestionValidator.is_valid_key:        question.key,
			QuestionValidator.is_valid_type:       question.type,
			QuestionValidator.is_valid_title:      question.title,
			QuestionValidator.is_valid_hint:       question.hint,
			QuestionValidator.is_valid_parameters: question.parameters
		}
		for validator, value in validations.items():
			valid, message = validator(value)
			if not valid:
				return (False, message)

		return (True, None)


	@staticmethod
	def is_reserved_key(key):
		"""is_reserved_key(key:string)
		Returns true if the specified key is reserved for internal use, false otherwise.
		"""
		valid, message = True, None
		if isinstance(key, basestring):
			if key not in Question.RESERVED_KEYS:
				valid, message = True, ("the key '%s' is not reserved." % key)
		else:
			valid, message = False, "key is not a string."

		return (valid, message)


	@staticmethod
	def is_valid_key(key):
		"""is_valid_key(key:string)
		Returns true if the specified key is valid, false otherwise.
		A key is considered valid if it is a non-empty string that is strictly
		composed of alphanumeric characters, hypens or underscores, and no
		whitespace. It must also not be reserved for internal use.
		"""
		from re import match

		valid, message = False, None

		if not isinstance(key, basestring) or len(key) < 1:
			message = "Error! A question key must be a non-empty string."
		elif match(r"[\w-]*", key).group() != key:
			message = "Error! The key '{}' contains an illegal character. A key may only contain letters (a-z, A-Z), numbers (0-9), hyphens (-), and underscores (_). It must not contain any whitespace.".format(key)
		elif QuestionValidator.is_reserved_key(key):
			message = "Error! The string '{}' is reserved for internal use and can not be used as a question key.".format(key)
		else:
			valid = True

		return (valid, message)


	@staticmethod
	def is_valid_type(type):
		"""is_valid_type(type:string)
		Returns true if the specified type is a valid question type, false otherwise.
		"""
		valid, message = True, None
		if isinstance(type, basestring):
			if type not in Question.TYPES:
				valid, message = False, ("the type '%s' is not valid." % key)
		else:
			valid, message = False, "type is not a string."

		return (valid, message)




class QuestionnaireValidator:
	@staticmethod
	def is_valid_configuration(configuration):
		"""is_valid_configuration(configuration:dict)
		Returns true if the specified configuration can be used to create a valid
		Questionnaire instance, false otherwise.
		"""
		return (True, None)


	@staticmethod
	def is_valid_branching(branches):
		"""is_valid_branching(branches:dict)
		Returns true if the questionnaire has a valid branching tree, false otherwise.
		"""
		for branch in [branch for branch in branches.itervalues() if branch is not None]:
			if isinstance(branch, basestring) and branch not in branches:
				return (False, "the key %s does not exist." % branch)
			elif isinstance(branch, dict):
				for key in branch.itervalues():
					if key not in branches:
						return (False, "the key %s does not exist." % key)

		return (True, None)




class QuestionError(Exception):
	pass




class QuestionnaireError(Exception):
	pass
