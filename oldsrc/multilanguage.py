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
def normalize_string(string, locale_id):
	"""normalize_string(string:string, locale_id:string)
	Returns a dictionary that contains the specified string mapped to the given locale identifer.
	No conversion is performed if the string is None and an error is raised if the locale
	identifier is invalid or the string parameter is not a string (or None).
	"""
	if string is None:
		return None
	elif not isinstance(string, basestring):
		raise ValueError("'string' parameter is not a string.")
	else:
		locale_id = locale_id.strip()
		if locale_id and is_locale_identifier(locale_id):
			return {locale_id:string}
		else:
			raise MultilanguageError("the locale identifier '%s' is not valid." % locale_id)


def is_normalized(value):
	"""is_normalized(value:dict)
	Returns true if the specified value is normalized, false otherwise.
	A value is normalized if it's a dictionary where each key is a locale identifier that
	is mapped to a string.
	"""
	valid, message = True, None
	if isinstance(value, dict):
		for locale_id, string in value.items():
			if not is_locale_identifier(locale_id):
				valid, message = False, "the locale identifier '%s' is not valid." % locale_id
				break
			elif not isinstance(string, basestring):
				valid, message = False, "the string is not a string." # TODO: Write a better error message.
				break
	else:
		valid, message = False, "value is not a dictionary."

	return (valid, message)


def is_locale_identifier(identifier):
	"""is_locale_identifier(identifier:string)
	Returns true if the specified locale identifier is valid, false otherwise.
	"""
	if isinstance(identifier, basestring):
		from re import match
		matches = match(r"([a-z]{2,3})(-[A-Z]+){0,1}", identifier)
		return matches is not None and matches.group() == identifier

	return False




class MultilanguageError(Exception):
	pass
