from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Python package to deliver a Gantner cloud interface'
LONG_DESCRIPTION = ''

# Setting up
setup(
    name="gimodules",
    version=VERSION,
    author="gimodules devs",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['numpy >= 1.16.0',
                      'pandas >= 0.22.0',
                      'requests',
                      'ipywidgets',
                      'httpx',
                      'httpx[http2]'],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)