# gimodules-python

## Information on how to manually distribute this package can be found here

https://packaging.python.org/en/latest/tutorials/packaging-projects/

### Distribute with CI / CD
Edit setup.py version number and create a release.
-> Creating a release will trigger the workflow to push the package to PyPi

## tests

run tests locally:

$ `pipenv run test -v` 

or 

$ `pytest`

### requirements

To create project all current requirements automatically:

$ `pip3 freeze > requirements.txt`
**_NOTE:_** Remove the old gimodules version from requirements.txt before pushing (dependency conflict).