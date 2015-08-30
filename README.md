# GeoTag-X project template

This is the template off which all projects for the [GeoTag-X](http://geotagx.org) platform are based. To use it,
you'll need to download it first
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
greatly simplify and quicken the process. Furthermore, it provides your project
with the same consistent look-and-feel as other GeoTag-X projects, making it
less confusing for volunteers who are already familiar with the platform.

We have written a detailed [**creation guide**](GUIDE.md) to help you get started.
