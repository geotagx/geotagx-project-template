# The GeoTag-X project builder tool.
# This module contains elements that will help write a project's task presenter
# (template.html) and tutorial (tutorial.html).
#
# Copyright (c) 2016 UNITAR/UNOSAT
#
# The MIT License (MIT)
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
class HtmlWriter():
	def __init__(self):
		from geotagx_sanitizer.core import get_sanitizers
		self.sanitizers = get_sanitizers()


	def _get_configurations(self, path):
		"""Returns the sanitized project configurations located at the specified path."""
		import os
		from geotagx_sanitizer.core import _deserialize_json
		from geotagx_sanitizer.core import sanitize_configurations

		filenames = {k: os.path.join(path, k + ".json") for k in self.sanitizers}
		configurations = {k: _deserialize_json(filename) for k, filename in filenames.iteritems()}

		# Add help to the configurations.
		questions = configurations["task_presenter"]["questionnaire"]["questions"]
		for question in questions:
			key = question["key"]
			try:
				help_file = open(os.path.join(path, "help", key + ".html"))
			except IOError:
				# A help file is not always guaranteed to exist so if an IOError occurs, skip it.
				pass
			else:
				with help_file:
					from htmlmin import minify
					question["help"] = minify(help_file.read(), remove_comments=True, remove_empty_space=True)

		return sanitize_configurations(configurations, self.sanitizers)


	@staticmethod
	def jsonify(input, compress=False):
		import json
		parameters = {
			"sort_keys": not compress,
			"indent": 0 if compress else 4,
			"separators": (",", ":" if compress else ": "),
			"encoding": "UTF-8",
			"ensure_ascii": False
		}
		output = json.dumps(input, **parameters).encode("UTF-8")
		return output.replace("\n", "") if compress else output


	#TODO Make this write(self, configurations, overwrite)
	def write(self, path, overwrite=False, compress=False):
		import os, logging
		from exceptions import HtmlWriterError

		if not os.path.isdir(path):
			raise HtmlWriterError("The path '%s' does not point to a directory." % path)
		elif not os.access(path, os.W_OK):
			raise HtmlWriterError("The directory '%s' is not writable. Please make sure you have the appropriate access permissions." % path)

		# If the overwrite flag is not set, make sure none of the target HTML files do not exist.
		TARGET_FILES = {
			"task_presenter": os.path.join(path, "template.html"),
			"tutorial": os.path.join(path, "tutorial.html")
		}
		if not overwrite and any(os.path.isfile(f) for f in TARGET_FILES.values()):
			raise HtmlWriterError("The directory '%s' already contains a generated task presenter (template.html) and or a tutorial (tutorial.html). To overwrite either, set the '-f' or '--force' flag." % path)

		configurations = self._get_configurations(path)

		# Remove the fields that can be retrieved from the server's database.
		project = configurations["project"]
		for key in ["name", "short_name", "description"]:
			project.pop(key, None)

		# Write the project's tutorial. Note that if no tutorial configuration exists,
		# an empty 'tutorial.html' file is still created as it is a requirement for
		# PyBossa's 'pbs' tool.
		with open(TARGET_FILES["tutorial"], "w") as file:
			if "tutorial" in configurations:
				logging.info("Writing tutorial (%s) ..." % TARGET_FILES["tutorial"])
				file.write(HtmlWriter.jsonify(configurations, compress))

		# Write the task presenter.
		with open(TARGET_FILES["task_presenter"], "w") as file:
			configurations.pop("tutorial", None) # Remove the tutorial configuration, if it exists.
			logging.info("Writing task presenter (%s) ..." % TARGET_FILES["task_presenter"])
			file.write(HtmlWriter.jsonify(configurations, compress))
