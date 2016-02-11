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
import unittest
from project import Project, ProjectValidator

class TestProject(unittest.TestCase):
	pass




class TestProjectValidator(unittest.TestCase):
	def test_valid_name(self):
		self.assertTrue(ProjectValidator.is_valid_name("hello")[0], "Valid name.")
		self.assertTrue(ProjectValidator.is_valid_name("hello   ")[0], "Valid name with trailing whitespace.")
		self.assertTrue(ProjectValidator.is_valid_name("   hello")[0], "Valid name with leading whitespace.")
		self.assertTrue(ProjectValidator.is_valid_name("   hello   ")[0], "Valid name with leading and trailing whitespace.")

	def test_illegal_name(self):
		self.assertFalse(ProjectValidator.is_valid_name(None)[0], "NoneType object used as name.")
		self.assertFalse(ProjectValidator.is_valid_name("")[0], "Empty string.")
		self.assertFalse(ProjectValidator.is_valid_name("   ")[0], "Whitespace only.")
		self.assertFalse(ProjectValidator.is_valid_name(1)[0], "Project name is a numerical value (not a string).")

	def test_valid_short_name(self):
		self.assertTrue(ProjectValidator.is_valid_short_name("hello")[0], "Alphabet characters.")
		self.assertTrue(ProjectValidator.is_valid_short_name("hello32")[0], "Alphanumeric characters.")
		self.assertTrue(ProjectValidator.is_valid_short_name("hello-world")[0], "Hyphen-separated characters.")
		self.assertTrue(ProjectValidator.is_valid_short_name("hello_world")[0], "Underscore-separated characters.")
		self.assertTrue(ProjectValidator.is_valid_short_name("h")[0], "Single letter project name.")
		self.assertTrue(ProjectValidator.is_valid_short_name("1")[0], "Single digit project name.")

	def test_illegal_short_name(self):
		self.assertFalse(ProjectValidator.is_valid_short_name(None)[0], "NoneType object used as short name.")
		self.assertFalse(ProjectValidator.is_valid_short_name("")[0], "Empty string.")
		self.assertFalse(ProjectValidator.is_valid_short_name("   ")[0], "Whitespace only.")
		self.assertFalse(ProjectValidator.is_valid_short_name("   hello")[0], "Valid short name but leading whitespace.")
		self.assertFalse(ProjectValidator.is_valid_short_name("hello   ")[0], "Valid short name but trailing whitespace.")
		self.assertFalse(ProjectValidator.is_valid_short_name("   hello   ")[0], "Valid short name but leading and trailing whitespace.")
		self.assertFalse(ProjectValidator.is_valid_short_name("hello*world")[0], "Invalid character (star).")
		self.assertFalse(ProjectValidator.is_valid_short_name("#hello-world")[0], "Invalid character (hash).")
		self.assertFalse(ProjectValidator.is_valid_short_name(1)[0], "Project short name is a not a string.")

	def test_valid_description(self):
		self.assertTrue(ProjectValidator.is_valid_description("?")[0], "Description is a non-empty string.")
		self.assertTrue(ProjectValidator.is_valid_description("   hello")[0], "Valid description with leading whitespace.")
		self.assertTrue(ProjectValidator.is_valid_description("hello   ")[0], "Valid description with trailing whitespace.")
		self.assertTrue(ProjectValidator.is_valid_description("   hello   ")[0], "Valid description with leading and trailing whitespace.")

	def test_illegal_description(self):
		self.assertFalse(ProjectValidator.is_valid_description(None)[0], "NoneType object used as description.")
		self.assertFalse(ProjectValidator.is_valid_description("")[0], "Empty string.")
		self.assertFalse(ProjectValidator.is_valid_description("   ")[0], "Whitespace only.")
		self.assertFalse(ProjectValidator.is_valid_description(1)[0], "Project description is a not a string.")


if __name__ == "__main__":
	unittest.main()
