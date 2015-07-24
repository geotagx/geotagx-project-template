# GeoTag-X project template

This is the template off which all projects for the [GeoTag-X](http://geotagx.org) platform are based. To build and
use it, you'll need to download it first
```
git clone https://github.com/geotagx/geotagx-project-template.git
cd geotagx-project-template/
```


## Setting up an isolated environment

It is highly recommended, but not necessary, that you install the template's
requirements in an isolated environment to prevent any possible conflicts with your system.
If you do not wish to create an isolated environment, head on over to the [Installing requirements](#installing-requirements) chapter.

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
should be appended to your prompt, e.g. `(env)name@domain:~$`.



## Installing requirements

To install the template requirements, run
```
pip install -r requirements.txt
```

If you are not installing the requirements in an isolated environment, you will
need to run the previous command as a super-user
```
sudo pip install -r requirements.txt
```

To make sure the requirements have been correctly installed, run
```
python build.py
```
which should display the script's instruction manual.

PS. If you are using a virtual environment, you must activate it each time you
you wish to run the `build.py` script.



## Building the sample project

With the template requirements installed, it should be pretty straightforward
building your own GeoTag-X project, provided you have the required files in place.

The [sample project](https://github.com/geotagx/geotagx-project-sample/) is
included as a submodule so you will need to fetch it before it can be used
```
git submodule update --init
```
The `sample` directory should now contain the entire sample project. To build it, run
```
python build.py sample/
```

The `build.py` script should produce a task presenter `template.html`, and
tutorial `tutorial.html` in the project's folder. The sample project is now ready
to be uploaded to your server via PyBossa's [web](http://pybossa.readthedocs.org/en/latest/user/overview.html#using-the-web-interface)
or [command line](http://pybossa.readthedocs.org/en/latest/user/pbs.html) interface.



## Building your own project

While it is not necessary to build your project with this template, it does
greatly simplify the process.

To build your project using this template, we have added a few more requirements
that you will need to specify in your project configuration. We have also added
the possibility of defining a tutorial configuration that allows you to create
one or more tutorials to go alongside your project.

The aforementioned configurations can be written in both JSON and YAML formats.

#### The project configuration (project.json/project.yaml)

The project configuration -- based on the classic PyBossa configuration -- has been
extended to include a few requirements to help create a project's task presenter.
In addition to the `name`, `short_name` and `description` fields required by PyBossa,
you will need to specify the following fields:
- `why`: a reminder to volunteers about the importance of their contribution to the project.
- `questions`: a set of one or more questions asked to volunteers.

#### The tutorial configuration (tutorial.json/tutorial.yaml)

Project tutorials are a great way of introducing volunteers to your project and
while optional, it is highly recommended that you include a few in your project.

The tutorial configuration is comprised of one or more tutorials where each one
contains the following fields:
- `image`: a direct link to an image to analyse.
- `image_source`: a link to a web page that provides contextual information about `image`.
- `assertions`: a set of assertions about `image`.


For more information on how to create your project's questionnaire and tutorial,
please refer to the [**creation guide**](GUIDE.md).
