# GeoTag-X project template

[![Build Status](https://travis-ci.org/geotagx/geotagx-project-template.svg?branch=master)](https://travis-ci.org/geotagx/geotagx-project-template)


This is the template off which all projects for the [GeoTag-X](http://geotagx.org) platform are based. To use it,
you'll need to download it first
```
git clone https://github.com/geotagx/geotagx-project-template.git
cd geotagx-project-template/
```


## I. The project builder

In the PyBossa platform (and by extension GeoTag-X), a project requires a task
presenter `template.html` and optionally a tutorial `tutorial.html`. This means
that you will need to be familiar with HTML, a language that is relatively
simple to learn, albeit particularly prone to human error.

Included with this template is the project builder tool `build.py` that does a
lot of the heavy-lifting by generating the HTML, CSS and JavaScript required by
a project. Not only does it simplify the project creation process, it allows
creators to concentrate more on the content of their projects without having to
worry about the more technical details. Furthermore, it provides your project
with the same consistent look-and-feel as other GeoTag-X projects, making it
less confusing for volunteers who are already familiar with the platform.

The builder tool depends on other libraries that will need to be installed.


### I.a. Setting up an isolated environment
#### I.a.1 Linux/MacOSx
It is highly recommended, but not necessary, that you install the builder tool's
requirements in an isolated environment to prevent any possible conflicts with
your system. If you do not wish to create an isolated environment, head on over
to the [Installing the requirements](#ib-installing-the-requirements) chapter.

First off, you will need to install [`virtualenv`](https://virtualenv.pypa.io/en/latest/) on your system
```
sudo pip install virtualenv
```

Then create a virtual environment in a directory of your choice; make sure you remember it!
For this example, we create one in the `env` directory.
```
virtualenv env/
```

Finally, activate your new virtual environment
```
source env/bin/activate
```

Upon successful execution, the environment's directory (encased in parentheses)
should be prepended to your prompt, e.g. `(env)name@domain:~$`. Remember that
you will have to activate this virtual environment each time you wish to use the
builder tool.

### I.a.2 Windows

* Install Github Desktop from https://desktop.github.com
* Install Win-Python from http://winpython.sourceforge.net
* `Fork` the repository to your personal project account on Github Web Interface
* Log into Github from the Github Desktop client
* Clone this repository **INTO** the Win-Python directory (Select Recursive Clone)
* Open the Win-Python Command Prompt by double - clicking the respective icon via Windows explorer
* Navigate into the Cloned repository via the command prompt. Refer http://computerhope.com/issues/chusedos.htm for help if you are not used to the command prompt
* Follow the steps mentioned in the following sections


### I.b. Installing the requirements

To install the requirements, run
```
pip install --upgrade pip
pip install -r requirements.txt
```

The first command upgrades your `pip` installation while the second installs
the actual requirements. If you are not installing the requirements in an
isolated environment, you will need to run the commands as a superuser
```
sudo pip install --upgrade pip
sudo pip install -r requirements.txt
```

To make sure the requirements have been correctly installed, run
```
python build.py --help
```
which should display the script's instruction manual.


### I.c. Building the sample project

With the builder tool installed, it should be pretty straightforward creating
your own GeoTag-X project, provided you have the required files in place.

A [sample project](https://github.com/geotagx/geotagx-project-sample/) has been
provided and can be used as a foundation for you project. It is included as a
submodule so you will need to fetch it first
```
git submodule update --init
```
The `sample` directory should now contain the entire sample project. To build
it, run
```
python build.py sample/
```

The tool should produce a task presenter `template.html`, and tutorial
`tutorial.html` in the project's folder. The sample project is now ready
to be deployed to your server via PyBossa's [web](http://pybossa.readthedocs.org/en/latest/user/overview.html#using-the-web-interface)
or [command line](http://pybossa.readthedocs.org/en/latest/user/pbs.html) interface.

### I.d. Building your own project

While it is most certainly not a requirement to use the builder tool, it will
most likely quicken the project creation process. We have written a complete
[**creation guide**](GUIDE.pdf) to help you get started.

### I.e. Building in PDF mode

The PDF mode lets GeoTag-X projects analyse PDF files instead of images. The PDF mode can be used
by passing a `-pm` flag to `build.py`. For example :
```
python build.py sample/ -pm
```
or
```
python build.py sample/ --pdf
```
The structure of the `project.json` file, `tutorial.json` file, etc all remain exactly the same. The only difference now is `tasks.csv` expects PDF files in the `image_url` column, and the corresponding source in `image_source` column. These PDF files should be publicly hosted, and the server where they are hosted should set the following header when serving the files :
```
Access-Control-Allow-Origin "http://mozilla.github.io"
```
