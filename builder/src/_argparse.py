# This module is part of the GeoTag-X template builder.
# Copyright (C) 2015 UNITAR, Jeremy Othieno.
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
import argparse

def bold(text):
	"""bold(text:string)
	Prints the specified text in bold.
	"""
	BOLD_TEXT_ON  = "\033[1m"
	BOLD_TEXT_OFF = "\033[0m"
	return BOLD_TEXT_ON + text + BOLD_TEXT_OFF


class CustomHelpFormatter(argparse.RawTextHelpFormatter):
	def _multiline(self, text):
		"""_multiline(text:string)
		Converts the block of text into smaller blocks in multiple arrays.
		"""
		import textwrap

		text = self._whitespace_matcher.sub(" ", text).strip()
		return textwrap.wrap(text, self._width)


	def _format_action(self, action):
		if not action.help:
			return None

		invocation = bold(self._format_action_invocation(action))
		parts      = ["\t%s\n" % (invocation)]

		for line in self._multiline(self._expand_help(action)):
			parts.append("\t%*s%s\n" % (6, " ", line))

		parts.append("\n")

		# Format sub-actions.
		for subaction in self._iter_indented_subactions(action):
			parts.append(self._format_action(subaction))

		# return a single string
		return self._join_parts(parts)


	def add_name(self, name):
		self.add_text("{0}\n\t{1}".format(bold("NAME"), name))


	def add_synopsis(self, prog):
		self.add_text("{0}\n\t{1}".format(bold("SYNOPSIS"),
		"{0} [OPTIONS]... PATH...".format(bold(prog))))


	def add_description(self, action_groups):
		"""add_description(action_groups:list<ActionGroup>)
		Pretty-prints the script's positional arguments, optional arguments, as well as user-defined groups.
		"""
		self.add_text("{0}\n\t{1}".format(
			bold("DESCRIPTION"),
			"The following is a set of OPTIONS you can use to modify the script's behavior:")
		)
		for group in action_groups:
			self.add_text(group.description)
			self.add_arguments(group._group_actions)


	def add_epilogue(self, epilogue):
		"""add_epilogue(epilog:string)
		Adds an epilogue to the help.
		"""
		self.add_text(
			"{authors_label}\n\tWritten by Jeremy Othieno.\n\n"
			"{report_label}\n\tReport bugs or any issues at https://github.com/geotagx/geotagx-project-template/issues.\n\n"
			"{copyright_label}\n\t{copyright_notice}".format(
				# epilogue, #TODO Add me.
				authors_label    = bold("AUTHORS"),
				report_label     = bold("REPORTING BUGS"),
				copyright_label  = bold("COPYRIGHT"),
				copyright_notice = "\n\t".join(self._multiline("Copyright (c) 2015 UNITAR. This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version."))
			)
		)


class CustomArgumentParser(argparse.ArgumentParser):
	def error(self, message):
		"""error(message:string)
		Prints an error message to stderr and exits.
		"""
		self.exit(1, ("%s\n") % (message))


	def format_help(self):
		"""
		Formats the help.
		"""
		formatter = self._get_formatter()

		formatter.add_name("{0} - {1}".format(self.prog, self.description))
		formatter.add_synopsis(self.prog)
		formatter.add_description(self._action_groups)
		formatter.add_epilogue(self.epilog)

		return formatter.format_help()
