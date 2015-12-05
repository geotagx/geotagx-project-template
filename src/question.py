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
	key = None
	type = None
	question = None
	hint = None
	help = None
	parameters = None
	__default_parameters = {
		"binary":{},
		"dropdown-list":{
			"options":None,
			"prompt":{"en":"Please select an option"},
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
			"placeholder":{"en":"Please enter a number"},
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
			"placeholder":{"en":"Please enter a URL e.g. http://www.example.com"},
			"maxlength":2000
		},
		"geotagging":{
			"location":None
		},
	}


	def __init__(self, key, entry):
		"""__init__(key:string, entry:dict)
		Instantiates a Question object with the given key, from the specified questionnaire entry.
		"""
		self.key        = key
		self.type       = entry.get("type")
		self.type       = self.type.strip() if isinstance(self.type, basestring) else None
		self.question   = Question.i18nify(entry.get("question"))
		self.hint       = Question.i18nify(entry.get("hint"))
		self.parameters = Question.getparameters(self.type, entry.get("parameters"))
		valid, message  = Question.isvalid(self)
		if not valid:
			raise Exception(message)


	@staticmethod
	def isvalid(question):
		"""isvalid(question:Question)
		Returns true if the question is valid, false otherwise.
		"""
		validations = {
			Question.iskey:        question.key,
			Question.istype:       question.type,
			Question.isquestion:   question.question,
			Question.ishint:       question.hint,
			Question.isparameters: question.parameters
		}
		for validator, value in validations.items():
			valid, message = validator(value)
			if not valid:
				return (False, message)

		return (True, None)


	@staticmethod
	def iskey(key):
		"""iskey(key:string)
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
		elif Question.isreservedkey(key):
			message = "Error! The string '{}' is reserved for internal use and can not be used as a question key.".format(key)
		else:
			valid = True

		return (valid, message)


	@staticmethod
	def isreservedkey(key):
		"""isreservedkey(key:string)
		Returns true if the specified key is reserved for internal use, false otherwise.
		"""
		return key in [
			"end",
			"photoAccessible",
			"photoVisible",
		]


	@staticmethod
	def istype(type):
		"""istype(type:string)
		Returns true if the type is valid, false otherwise.
		"""
		types = [
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
		]
		deprecated = {
			"single_choice":"select",
			"multiple_choice":"checklist",
			"illustrated_multiple_choice":"illustrative-checklist",
			"textinput":"text",
			"textarea":"longtext"
		}
		if type not in types:
			if type in deprecated:
				return (False, "Error! The question type '{}' is deprecated and has been replaced with '{}'.".format(type, deprecated.get(type)))
			else:
				return (False, "Error! The question type '{}' is not recognized.".format(type))
		else:
			return (True, None)


	@staticmethod
	def isISO6391(code):
		"""isISO6391(code:string)
		Returns true if the specified code is an ISO 639-1 code, false otherwise.
		ISO 639-1 language codes are two-letter lowercase strings, examples of
		which can be found at https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
		"""
		valid, message = True, None
		if isinstance(code, basestring):
			if len(code.strip()) == 0:
				valid, message = False, "Error! A language code must be a non-empty string."
			else:
				from re import match

				matches = match(r"[a-z]{2}", code)
				if matches is None or matches.group() != code:
					valid, message = False, "Error! The ISO code '%s' is invalid. An ISO 639-1 code is a two-character string comprised of lowercase letters only, e.g. 'en', 'fr', or 'de'." % code
		else:
			valid, message = False, "Error! Language code is not a string."

		return (valid, message)


	@staticmethod
	def isi18nified(input, isvalid):
		"""isi18nified(input:dict, isvalid:function)
		Returns true if the specified input is a dictionary where each value
		is associated to an ISO 639-1 language code and is considered valid
		by the isvalid function, false otherwise.
		"""
		valid, message = True, None
		if not input:
			valid, message = False, "Error! No input value is specified."
		elif isinstance(input, dict):
			for code, value in input.items():
				valid, message = Question.isISO6391(code)
				if valid:
					valid, message = isvalid(value)
					if not valid:
						break
				else:
					break
		else:
			valid, message = False, "Error! The input must be a dictionary!"

		return (valid, message)


	@staticmethod
	def isquestion(question):
		"""isquestion(question:dict)
		Returns true if the question is an i18nified object, false otherwise.
		An i18nified object is a dictionary that assigns a string to an ISO 639-1
		language code, for instance {"en":"What is the answer to life?"}. Please
		also note that questions strings must not be empty.
		"""
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

		return Question.isi18nified(question, isvalid)


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


	@staticmethod
	def i18nify(input, language="en"):
		"""i18nify(input:none|string|dict, language:string)
		Returns the input as an i18nified object, a dictionary that assigns each
		value to an ISO 639-1 language code.
		"""
		if isinstance(input, basestring):
			input = input.strip()
			return None if len(input) == 0 else {language:input}
		else:
			return input


	@staticmethod
	def getparameters(type, defaults=None):
		"""getparameters(type:string, defaults:dict)
		Returns the parameters for the specified type of question. If the
		defaults object is not empty, then any parameter found in it will be
		used as a default value.
		"""
		parameters = Question.__default_parameters[type].copy()

		# Set the user-defined default values.
		if defaults is not None:
			for key in [k for k in defaults if defaults[k] is not None]:
				parameters[key] = defaults[key]

		return parameters
