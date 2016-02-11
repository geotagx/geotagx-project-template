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
import unittest, multilanguage

class TestMultilanguage(unittest.TestCase):
	def test_valid_locale_identifiers(self):
		self.assertTrue(multilanguage.is_locale_id("en-GB"), "English (British) locale identifier.")
		self.assertTrue(multilanguage.is_locale_id("en-US"), "English (American) locale identifier.")
		self.assertTrue(multilanguage.is_locale_id("mt"), "Maltese locale identifier.")
		self.assertTrue(multilanguage.is_locale_id("haw"), "Hawaiian locale identifier.")

	def test_illegal_locale_identifiers(self):
		self.assertFalse(multilanguage.is_locale_id(None), "No value")
		self.assertFalse(multilanguage.is_locale_id(""), "Empty string")
		self.assertFalse(multilanguage.is_locale_id({}), "Non-string value (dictionary)")
		self.assertFalse(multilanguage.is_locale_id(43), "Non-string value (number)")
		self.assertFalse(multilanguage.is_locale_id("e"), "Single-character string")
		self.assertFalse(multilanguage.is_locale_id("32"), "String containing non-alphabet characters")
		self.assertFalse(multilanguage.is_locale_id("en "), "String containing trailing space")
		self.assertFalse(multilanguage.is_locale_id("en fr"), "String containing more than one ISO 639-1 code")
		self.assertFalse(multilanguage.is_locale_id("FR"), "Uppercase language designator.")


if __name__ == "__main__":
	unittest.main()
