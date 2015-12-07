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

def isiso6391(code):
	"""isiso6391(code:string)
	Returns true if the specified code is an ISO 639-1 code, false otherwise.
	ISO 639-1 language codes are two-letter lowercase strings, examples of
	which can be found at https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
	"""
	valid = False
	if isinstance(code, basestring) and len(code.strip()) == 2:
		from re import match

		matches = match(r"[a-z]{2}", code)
		valid = matches is not None and matches.group() == code

	return valid


def i18nify(input, language="en"):
	"""i18nify(input:string|dict, language:string)
	Returns a dictionary where the input is assigned to the specified
	ISO 639-1 language code. If the input is either None or already a
	dictionary, or the language code is invalid, no conversion operation
	is performed and the input is returned as is.
	"""
	if not isiso6391(language):
		raise ValueError("[i18nify] Error! The language code '%s' is invalid. An ISO 639-1 code is a two-character string comprised of lowercase letters only, e.g. 'en', 'fr', or 'de'." % language)

	if isinstance(input, basestring):
		return None if len(input.strip()) == 0 else {language:input}

	return input


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
			if not isiso6391(code):
				valid, message = False, "[isi18nified] Error! The language code '%s' is invalid. An ISO 639-1 code is a two-character string comprised of lowercase letters only, e.g. 'en', 'fr', or 'de'." % code
				break
			else:
				valid, message = isvalid(value)
				if not valid:
					break
	else:
		valid, message = False, "Error! The input must be a dictionary!"

	return (valid, message)
