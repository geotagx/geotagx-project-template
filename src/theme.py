# This module is part of the GeoTag-X project builder.
# Copyright (C) 2016 UNITAR.
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
class Theme:
	path = None
	assets = {
		"core":{
			"js":None,
			"css":None
		},
		"geolocation":{
			"js":None,
			"css":None
		},
		"datetime":{
			"js":None,
			"css":None
		},
		"multilanguage":{
			"js":None,
			"css":None
		},
	}
	template = None

	def __init__(self, path):
		"""__init__(path:string)
		Instantiates a Theme object from the content of the directory located at
		the specified path.
		"""
		import os
		from jinja2 import Environment, FileSystemLoader

		valid, message = Theme.hastheme(path)
		if not valid:
			raise Exception(message)

		self.path = path
		self.template = Environment(loader=FileSystemLoader(searchpath=os.path.join(self.path, "templates"))).get_template("base.html")


	def getasset(self, name):
		"""getasset(name:string)
		Returns the set of assets contained in the bundle with the specified name.
		"""
		css, js = "", ""

		name = name.strip()
		bundle = self.assets.get(name, None)

		if bundle is None:
			print "[Theme::getasset] Warning! Unknown asset bundle '%s'." % name
		else:
			# If any assets have not been loaded into memory, do so.
			empties = filter(lambda item: item[1] is None, bundle.iteritems())
			if len(empties) > 0:
				import os
				basefile = os.path.join(self.path, *["assets", "bundles", "asset.bundle.%s" % name])
				for key, _ in empties:
					filepath = "%s.%s" % (basefile, key)
					try:
						with open(filepath, "r") as file:
							bundle[key] = file.read()
					except IOError:
						# If a theme does not contain a specified asset, set its
						# value to an empty string. Leaving it as 'None' means
						# the script will keep searching for the missing file.
						bundle[key] = ""

			css = unicode(bundle["css"].strip(), "UTF-8")
			js  = unicode(bundle["js"].strip(),  "UTF-8")

		return css, js


	def getassets(self, bundles=set()):
		"""getassets(bundles:set)
		Returns the themes JS and CSS assets, based on the specified bundles.
		"""
		try: assert type(bundles) is set, "[Theme::getassets] Error! 'bundles' parameter is not a set!"
		except AssertionError as error: raise Exception(error)

		# The core bundle is always returned, however if it is explicitly added to
		# the bundle set, it needs to be removed or it will be concatenated to
		# the result twice.
		if "core" in bundles:
			bundles.remove("core")

		css, js = self.getasset("core")
		for bundle in bundles:
			css_, js_ = self.getasset(bundle)

			if len(css_) > 0: css += css_
			if len(js_)  > 0: js  += ";" + js_ # ';' makes sure statements between concatenated scripts are separated.

		return css, js

	@staticmethod
	def hastheme(path):
		"""hastheme(path:string)
		Returns true if the specified path contains a valid theme, false otherwise.
		"""
		return (True, None)
