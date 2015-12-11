# -*- coding: utf-8 -*-
#
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
import unittest
import i18n

class TestI18n(unittest.TestCase):
	def test_valid_iso_codes(self):
		self.assertTrue(i18n.isiso6391("en"), "Valid ISO 639-1 code for English language")
		self.assertTrue(i18n.isiso6391("fr"), "Valid ISO 639-1 code for French language")
		self.assertTrue(i18n.isiso6391("de"), "Valid ISO 639-1 code for German language")
		self.assertTrue(i18n.isiso6391("it"), "Valid ISO 639-1 code for Italian language")

	def test_illegal_iso_codes(self):
		self.assertFalse(i18n.isiso6391(None), "No value")
		self.assertFalse(i18n.isiso6391(""), "Empty string")
		self.assertFalse(i18n.isiso6391({}), "Non-string value (dictionary)")
		self.assertFalse(i18n.isiso6391(43), "Non-string value (number)")
		self.assertFalse(i18n.isiso6391("FR"), "Uppercase string")
		self.assertFalse(i18n.isiso6391("e"), "Single-character string")
		self.assertFalse(i18n.isiso6391("32"), "String containing non-alphabet characters")
		self.assertFalse(i18n.isiso6391("en "), "String containing trailing space")
		self.assertFalse(i18n.isiso6391("en fr"), "String containing more than one ISO 639-1 code")


if __name__ == "__main__":
	unittest.main()
