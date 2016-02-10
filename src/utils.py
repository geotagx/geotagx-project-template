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
def load_configuration(filename):
	"""load_configuration(filename:string)
	Returns the configuration from the file with the specified filename.
	"""
	import os
	if not os.access(filename, os.F_OK | os.R_OK):
		raise IOError("could not access '%s'. Please make sure the file exists and that you have sufficient access permissions." % filename)

	with open(filename) as file:
		try:
			import json
			return json.loads(file.read())
		except ValueError as e:
			print "ValueError:", e

	return None


def load_js(filename):
	"""load_js(filename:string)
	Returns the minified javascript from the file with the specified filename.
	"""
	js = ""
	with open(filename, "r") as file:
		data = file.read().decode("utf-8")
		if data is not None:
			import slimit
			data = slimit.minify(data, mangle=True)
			if len(data) > 0:
				js = data

	return js


def load_css(filename):
	"""load_css(filename:string)
	Returns the minified CSS from the file with the specified filename.
	"""
	css = ""
	with open(filename, "r") as file:
		data = file.read().decode("utf-8")
		if data is not None:
			import rcssmin
			data = rcssmin.cssmin(data)
			if len(data) > 0:
				css = data

	return css
