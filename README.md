GeoTag-X project template
=========================

This is the template off which all projects for the GeoTag-X platform are based.


## INSTALLING

To build the template, you'll need to download it first
```
git clone https://github.com/spMohanty/geotagx_project_template.git
```


Install its requirements in an isolated environment. For this you'll need to install `virtualenv`
```
cd geotagx_project_template
pip install virtualenv
virtualenv env
source ./env/bin/activate
pip install -r requirements.txt
```

This is a sample project template built for use with the [**GeoTag-X**](http://geotagx.org) crowdsourcing platform.
This is a sample project built for use with the GeoTag-X crowdsourcing platform.



## TESTING

When installation is done, run the `build.py` script to create the template's task presenter, i.e. `template.html`.

To test the template, a project has been provided in the sample folder, ...
