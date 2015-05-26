GeoTag-X project template
=========================

This is the template off which all projects for the [GeoTag-X](http://geotagx.org) platform are based. To build and
use it, you'll need to download it first
```
git clone https://github.com/spMohanty/geotagx_project_template.git
cd geotagx_project_template/
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

In case you do not have a working project, a [sample project](https://github.com/geotagx/geotagx-project-sample/) is provided.
It is included as a submodule so you will need to fetch it before it can be used
```
git submodule update --init
```
The sample `sample` directory should now contain the entire sample project. To build it, run
```
python build.py sample/
```

The `build.py` script should produce a `template.html` file, i.e. the
project's task presenter, in the project's folder. You can now setup the
project via PyBossa's [web interface](http://pybossa.readthedocs.org/en/latest/user/overview.html#using-the-web-interface) or [command line interface](http://pybossa.readthedocs.org/en/latest/user/pbs.html).

## Configuration files
`geotagx-project-template` currently supports two types of configuration files   
* JSON : https://github.com/geotagx/geotagx-project-sample/blob/master/project.json
* YAML : https://github.com/geotagx/geotagx-project-sample/blob/master/project.yaml.sample

It first looks for a `project.json` file in the project directory, and if it doesnt find one, then it also looks for 
a `project.yaml` file.