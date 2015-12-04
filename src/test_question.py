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
from question import Question

class TestQuestion(unittest.TestCase):
	def test_valid_keys(self):
		self.assertTrue(Question.iskey("A")[0], "Single-character")
		self.assertTrue(Question.iskey("thisIsALongKey")[0], "Multi-character")
		self.assertTrue(Question.iskey("--")[0], "Hyphens")
		self.assertTrue(Question.iskey("--key")[0], "Leading hyphens")
		self.assertTrue(Question.iskey("_")[0], "Underscores")
		self.assertTrue(Question.iskey("__key")[0], "Leading underscores")
		self.assertTrue(Question.iskey("_now-y0u_4re-pushing-1t")[0], "Mixed characters")
		self.assertTrue(Question.iskey("_end")[0], "Not a reserved keyword")

	def test_illegal_keys(self):
		self.assertFalse(Question.iskey("")[0], "Empty string")
		self.assertFalse(Question.iskey("   ")[0], "Whitespace only")
		self.assertFalse(Question.iskey("  key")[0], "Leading whitespace")
		self.assertFalse(Question.iskey("end\t")[0], "Traling tabulation")
		self.assertFalse(Question.iskey("*$/\\")[0], "Non-alphanumeric characters")
		self.assertFalse(Question.iskey("end")[0], "Reserved key")
		self.assertFalse(Question.iskey("photoVisible")[0], "Reserved key")
		self.assertFalse(Question.iskey(32768)[0], "Not a string")
		self.assertFalse(Question.iskey("\n")[0], "Illegal escape character")


if __name__ == "__main__":
	unittest.main()
