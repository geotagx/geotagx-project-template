import os

class Project:
	path = None
	configfile = None
	name = None
	short_name = None
	description = None
	why = None
	js = None
	css = None
	questions = None
	tutorials = None


	def __init__(self, path):
		"""__init__(path:string)
		Instantiates a Project object for the GeoTag-X project located at the
		specified path, a path that must point to a read/writable directory that
		contains a valid project configuration file, and optionally, a tutorial file.
		"""
		if not os.path.isdir(path) or not os.access(path, os.W_OK):
			raise IOError("The path '{}' does not point to a read/writable directory, or you may not have sufficient access permissions.".format(path))

		self.path = os.path.realpath(path)
		self.configfile = Project.findconfigfile(self.path)
		if not self.configfile:
			raise IOError("The directory '{}' does not contain a GeoTag-X project configuration file or you may not have sufficient access permissions.".format(path))


	def parseconfigfile(self):
		"""parseconfigfile(filename:string)
		Returns the project configuration defined in the file with the specified filename.
		"""
		configuration = None
		extension = os.path.splitext(self.configfile)[1]

		# Find the parser to use based on the filename extension.
		parser = {
			".json":lambda file: json.loads(file.read()),
			".yaml":lambda file: yaml.load(file)
		}.get(extension)
		if parser:
			with open(self.configfile) as file:
				import json, yaml
				configuration = parser(file)
		else:
			print "Error! Could not find a suitable configuration file parser for the extension '{}'.".format(extension)

		return configuration


	def build(self, css, js, compress):
		"""build(css:string, js:string, compress:boolean)
		Builds the project from its configuration file.
		"""
		configuration = self.parseconfigfile()
		if configuration:
			self.name = configuration["name"].strip()
			self.short_name = configuration["short_name"].strip()
			self.description = configuration["description"].strip()
			self.why = configuration["why"].strip()
			self.js = Project.getjs(self.path, js, compress)
			self.css = Project.getcss(self.path, css, compress)
			self.questions = Project.getquestions(configuration, self.path)
			self.tutorials = Project.gettutorials(configuration)

			if not self.isvalid():
				print "The project located at '{}' is not valid! Please verify its configuration file.".format(self.path)
				return False
			else:
				return True

		# The project could not be built successfully.
		return False


	def isvalid(self):
		"""
		Returns true if this project is valid, false otherwise. A project is
		considered valid if it has a name, short name, description, a reason
		why contributions matter, and at least one valid question.
		"""
		return (
			self.name and
			self.short_name and
			self.description and
			self.why and
			self.questions
		)


	def __str__(self):
		"""
		Returns the object in the form of a string.
		"""
		return """{name}
		\r{underline}
		\rShort name: {short_name}
		\rDescription: {description}
		\rWhy: {why}
		\rNumber of questions: {question_count}
		\rConfiguration file: {configfile}
		\rTutorial included: {has_tutorial}""".format(
			name=self.name,
			underline=("-" * len(self.name)),
			short_name=self.short_name,
			description=self.description,
			why=self.why,
			question_count=len(self.questions) if self.questions else 0,
			configfile=os.path.basename(self.configfile),
			has_tutorial="Yes" if self.tutorials else "No"
		)


	@staticmethod
	def create(path, overwrite=False):
		instance = None

		# Is the path read/writable? It has to be if we want to write our final
		# result to it. Also not that unless the overwrite parameter is set to
		# true, we can not overwrite any existing task presenters or tutorials.
		if os.path.isdir(path) and os.access(path, os.W_OK):
			skip = not overwrite and (
				os.access(os.path.join(path, "template.html"), os.F_OK) or
				os.access(os.path.join(path, "tutorial.html"), os.F_OK)
			)
			if skip:
				print "The directory '{}' already contains either a task presenter or a tutorial. To overwrite them, set the '-f' or '--force' flag.".format(path)
			else:
				try:
					instance = Project(path)
				except Exception as e:
					print e

		return instance


	@staticmethod
	def findconfigfile(path):
		"""findconfigfile(path:string)
		Returns the project configuration file's name for the project located
		at the specified path.
		"""
		for name in ["project.json", "project.yaml"]:
			filename = os.path.join(path, name)
			if os.access(filename, os.F_OK | os.R_OK):
				return filename

		return None


	@staticmethod
	def getjs(path, js, compress):
		"""getjs(path:string, js:string, compress:boolean)
		Loads the task presenter's custom javascript for the project located at
		the specified path. If the custom script does not exist or is empty,
		then the builder will automatically generate one.
		"""
		output = js if js else None
		try:
			with open(os.path.join(path, "project.js"), "r") as file:
				data = file.read()
				if data:
					data = data if not compress else minify(js)
					output = output + data if output else data
					output = output.strip()
		except:
			pass

		return output


	@staticmethod
	def getcss(path, css, compress):
		"""getcss(path:string, css:string, compress:boolean)
		Loads the task presenter's custom stylesheet for the project located at
		the specified path.
		"""
		output = css if css else None
		try:
			with open(os.path.join(path, "project.css"), "r") as file:
				data = file.read()
				if data:
					data = data if not compress else cssmin(data, keep_bang_comments=False)
					output = output + data if output else data
					output = output.strip()
		except:
			pass

		return output


	@staticmethod
	def getquestions(configuration, projectpath):
		"""getquestions(configuration:dictionary, projectpath:string)
		Returns the set of questions defined in the specified project configuration.
		If projectpath is specified then the function will look for help in the
		'<projectpath>/help' directory.
		"""
		questions = configuration["questions"]

		# Attach help to the corresponding question.
		if projectpath:
			helpdir = os.path.join(projectpath, "help")
			for question in questions:
				try:
					# Find the help in an HTML file with the same name as the question ID.
					with open(os.path.join(helpdir, "{}.html".format(question["id"])), "r") as file:
						data = file.read().strip()
						if data:
							question["help"] = data
				except:
					pass

		return questions


	@staticmethod
	def gettutorials(configuration):
		"""gettutorials(configuration:dictionary)
		Returns the set of tutorials defined in the specified project configuration.
		"""
		return None
