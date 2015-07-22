#!/usr/bin/env python
import os, sys, codecs, locale, json, htmlmin
from jinja2 import Environment, FileSystemLoader
from slimit import minify
from rcssmin import cssmin

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

USAGE = """Usage: """ + __file__ + """ directory [OPTIONS]
Build the task presenter for the GeoTag-X project located in the specified directory.
The following is a list of OPTIONS you can use to modify the script's behavior:\n
\r    -f, --force             overwrites the file 'template.html' in the specified directory.
\r    -c, --compress          compresses the generated task presenter.
\r    -s, --no-static-inline  disables inlining GeoTag-X's common CSS and JS files, adding external links to them instead.
\r    -p, --no-pybossa-run    disables automatic generation of the pybossa launcher. In this case, the launcher must be implemented in project.js.
\r    -h, --help              prints this help message.\n"""


LAYOUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "layout")


def has_valid_project(path):
	"""Returns true if the directory with the specified path is writable, and contains a valid GeoTag-X project, false otherwise."""
	return  os.path.isdir(path) \
		and os.access(path, os.W_OK) \
		and (os.access(os.path.join(path, "project.json"), os.F_OK | os.R_OK) or os.access(os.path.join(path, "project.yaml"), os.F_OK | os.R_OK))


def is_valid_project_json(json):
	"""Returns true if the specified JSON object has a valid project structure, false otherwise."""
	# TODO
	return True


def get_project_json(project_dir):
	"""Converts the project.json file into a JSON object and returns it."""
	if os.access(os.path.join(project_dir, "project.json"), os.F_OK | os.R_OK):
		filename = os.path.join(project_dir, "project.json")
		with open(filename) as file:
			data = file.read()
			return json.loads(data)
	elif os.access(os.path.join(project_dir, "project.yaml"), os.F_OK | os.R_OK):
		import yaml
		filename = os.path.join(project_dir, "project.yaml")
		with open(filename) as file:
			return yaml.load(file)


def get_template_css(compress):
	"""Collects CSS files from the template static folder, optionally minifies them,
	and then embeds them directly into the rendered output.
	"""
	CSS_DIR = os.path.join(LAYOUT_DIR, *["static","css"])

	css = ""
	for root, dirs, filenames in os.walk(CSS_DIR, topdown=False):
		for filename in filter(lambda f: f.endswith(".css"), filenames):
			css += open(os.path.join(root, filename), "r").read()

	return css if not compress else cssmin(css, keep_bang_comments=False)


def get_template_js(compress):
	"""Collects JS files from the template static folder, optionally minifies them,
	and then embeds them directly into the rendered output
	"""
	JS_DIR = os.path.join(LAYOUT_DIR, *["static","js"])
	js = ""
	for root, dirs, filenames in os.walk(JS_DIR, topdown=False):
		for filename in filter(lambda f: f.endswith(".js"), filenames):
			js += open(os.path.join(root, filename), "r").read()

	return js if not compress else minify(js)


def get_project_css(project_dir, compress):
	"""Returns the project's custom stylesheet, possibly minified, if it exists."""
	try:
		with open(os.path.join(project_dir, "project.css"), "r") as f:
			css = f.read()
			return css if not compress else cssmin(css, keep_bang_comments=False)
	except:
		return ""


def get_project_js(project_dir, compress):
	"""Returns the project's custom script, possibly minified, if it exists."""
	try:
		with open(os.path.join(project_dir, "project.js"), "r") as f:
			js = f.read()
			return js if not compress else minify(js)
	except:
		return ""


def get_project_help(directory):
	"""Returns a dictionary that contains the help provided for a specific question."""
	help = {}

	if os.path.isdir(directory):
		for filename in filter(lambda f: f.endswith(".html"), os.listdir(directory)):
			with open(os.path.join(directory, filename)) as file:
				filedata = file.read().strip()
				if filedata:
					# Associate the file's content with a question identifier.
					id = os.path.splitext(os.path.basename(filename))[0]
					help[id] = filedata

	return help


def get_questionnaire_flow_handler(questions):
	"""Generates an anonymous javascript function that determines the next question based on the current question and it's anwer."""
	def decode_question_id(id):
		if isinstance(id, int) and id >= 0:
			return id
		elif isinstance(id, unicode) and id == "finish":
			return len(questions) + 1
		else:
			return 0

	def get_statements(branch, question_type):
		if isinstance(branch, list):
			statements = ""
			for entry in branch:
				for key in entry:
					answer = key.lower()
					answer = answer.replace("'","") #Handle quoted versions of Yes and No in YAML
					next_question = decode_question_id(entry.get(key))

					if question_type == "binary" and answer == "no":
						statements += "else if (answer !== \"yes\"){{ return {}; }} ".format(next_question)
					else:
						statements += "else if (answer === \"{0}\"){{ return {1}; }} ".format(answer, next_question)

			# Append default action.
			statements += "else { return question + 1; }"

			return statements.lstrip("else ") # Remember to remove the leading "else".
		else:
			return "return {};".format(decode_question_id(branch))

	cases = ""
	for question in questions:
		branch = question.get("branch")
		if branch is not None:
			condition  = "case {}: ".format(question.get("id"))
			statements = get_statements(branch, question.get("type"))
			cases     += "{0}{1}\n\t\t\t".format(condition, statements)

	return """
	function(question, answer){{
		answer = $.type(answer) === "string" ? answer.toLowerCase() : answer; // toLowerCase for case-insensitive string comparisons.
		switch(question){{
			{}
			default: return question + 1;
		}}
	}}
	""".strip().format(cases.rstrip("\n\t\t\t"))


def get_project_tutorial(project_dir):
	"""Generates an array object containing assertions about a specified image."""
	def parse_assertions(assertions):
		def parse_messages(messages):
			output = ""
			for key in messages:
				message = messages[key]
				output += "\"{0}\":\"{1}\",\n{2}".format(key, message, "\t"*6)

			return output.strip()

		output = ""
		for question in assertions:
			assertion = assertions[question]
			expects = assertion["expects"].lower() # lower-case for case-insensitive string comparisons.
			default_message = assertion["default_message"]
			messages = parse_messages(assertion["messages"])

			output += """
			{0}:{{
					"expects":"{1}",
					"default_message":"{2}",
					"messages":{{
						{3}
					}}
			\t}},
			""".format(question, expects, default_message, messages).strip()

		return output.rstrip(",")

	try:
		tutorial = ""
		with open(os.path.join(project_dir, "tutorial.json")) as file:
			data = file.read()
			for entry in json.loads(data)["tutorial"]:
				image = entry["image"]
				image_source = entry["image_source"]
				assertions = parse_assertions(entry["assertions"])

				tutorial += "\n\t\t"
				tutorial += """
				{{
				"image":"{0}",
				"image_source":"{1}",
				"assertions":{{
					{2}
				}}\r\t\t}},
				""".format(image, image_source, assertions).strip()

		return "[{}\n\t]".format(tutorial.strip().rstrip(",")) # "[{}]".format(tutorial)
	except:
		return None


def build(path, compress=False):
	"""Builds the task presenter for the project located at the specified path."""
	project_dir = os.path.realpath(path)

	json = get_project_json(project_dir)
	if not is_valid_project_json(json):
		print "Error! The 'project.json' file is not valid."
		sys.exit(1)

	template           = Environment(loader=FileSystemLoader(searchpath=LAYOUT_DIR)).get_template("base.html")
	short_name         = json["short_name"].strip()
	why_               = json["why"].strip()
	questions_         = json["questions"]
	get_next_question_ = get_questionnaire_flow_handler(questions_)

	# Add backwards compatibility for old question type names.
	question_types = {
		"single_choice":"select",
		"multiple_choice":"checklist",
		"illustrated_multiple_choice":"illustrative-checklist",
		"textinput":"text",
		"textarea":"longtext"
	}
	for question in questions_:
		new_type = question_types.get(question["type"])
		if new_type:
			question["type"] = new_type

	# Assign the help to its corresponding question.
	help = get_project_help(os.path.join(project_dir, "help"))
	if len(help) > 0:
		for question in questions_:
			key = str(question["id"])
			try:
				question[u"help"] = help[key]
			except:
				pass

	# Build the template and tutorial.
	js_   = get_template_js(compress) # Collects JS common to the whole template
	css_  = get_template_css(compress) # Collects CSS common to the whole template
	js_  += get_project_js(project_dir, compress)
	css_ += get_project_css(project_dir, compress)

	with open(os.path.join(project_dir, "template.html"), "w") as output:
		html = template.render(is_tutorial=False, questions=questions_, css=css_, js=js_, slug=short_name, why=why_, get_next_question=get_next_question_)

		# if compress:
		# 	html = htmlmin.minify(html, remove_comments=True, remove_empty_space=True)

		output.write(html.encode("UTF-8"))

	# Build the tutorial.
	with open(os.path.join(project_dir, "tutorial.html"), "w") as output:
		tutorial_ = get_project_tutorial(project_dir)

		if tutorial_ is not None:
			html = ""
			html = template.render(is_tutorial=True, questions=questions_, css=css_, js=js_, slug=short_name, why=why_, get_next_question=get_next_question_, tutorial=tutorial_)
			# if compress:
			# 	html = htmlmin.minify(html, remove_comments=True, remove_empty_space=True)

			output.write(html.encode("UTF-8"))


def main(argv):
	argc = len(argv)
	if argc != 2:
		print USAGE
	else:
		path = argv[1]
		if not path or path in ("-h", "--help"):
			print USAGE
		else:
			if has_valid_project(path):
				build(path)
			else:
				print "The directory '" + path + "' does not contain a valid GeoTag-X project, or you may not have read/write permissions."


if __name__ == "__main__":
	main(sys.argv)
