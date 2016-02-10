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
import os
from questionnaire import Questionnaire

class Tutorial:
	entries = None
	serialized = None


	def __init__(self, configuration):
		"""__init__(configuration:list)
		Instantiates a Tutorial object from the specified tutorial configuration.
		"""
		if configuration is None or len(configuration) < 1:
			raise Exception("Error! The configuration object does not contain a valid tutorial.")

		self.entries = configuration


	def __len__(self):
		"""
		Returns the number of <image, assertions> entries in the tutorial.
		"""
		return 0 if self.entries is None else len(self.entries)


	def __str__(self):
		"""
		Returns the tutorial as a JSON formatted string.
		"""
		if self.entries is None:
			return ""
		if self.serialized is None:
			import json
			self.serialized = json.dumps(self.entries)

		return self.serialized


	@staticmethod
	def isvalid(tutorial):
		"""iswhy(tutorial:dict)
		Returns true if the specified tutorial is valid, false otherwise.
		"""
		return (True, None)
