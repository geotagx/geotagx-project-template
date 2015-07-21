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
		# return textwrap.wrap(self._whitespace_matcher.sub(" ", text).strip(), width)
		text = self._whitespace_matcher.sub(" ", text).strip()
		return textwrap.wrap(text, self._width)
		# help_lines = textwrap.wrap(self._whitespace_matcher.sub(" ", help_text).strip(), help_width)


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
		self.add_text("""\r\n{0}\n\tWritten by Jeremy Othieno.
			\r\n{1}\n\tReport bugs or any issues at https://github.com/geotagx/geotagx-project-template/issues
			\r\n{2}\n\tTo be confirmed""".format( #TODO Set copyright.
				# epilogue, #TODO Add me.
				bold("AUTHORS"),
				bold("REPORTING BUGS"),
				bold("COPYRIGHT")
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
