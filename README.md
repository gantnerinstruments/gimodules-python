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

To create the requirements file for the project, run the following command:

$ `pipreqs .`

To create project all current packages installed in your venv for requirements automatically:

$ `pip3 freeze > requirements.txt`
**_NOTE:_** Remove the old gimodules version from requirements.txt before pushing (dependency conflict).


### Documentation

The documentation is being built as extern script in the GI.Sphinx repository.

The documentation consists of partially generated content. 
To **generate .rst files** from the code package, run the following command from the root directory of the project:

```bash
sphinx-apidoc -o docs/source/ gimodules
```

To **build the documentation**, run the following command:

```bash
cd docs
make html
```


#### TODO
1. [ ] lint.sh diff between black and flake8 etc
2. [ ] Usage with python 3.12
3. [x] Doc requirements 
