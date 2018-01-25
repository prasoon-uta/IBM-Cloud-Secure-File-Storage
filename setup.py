
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='IBM Cloud Storage',
    version='1.0.0',
    description='Cryptographic storage using IBM Cloud and python flask',
    long_description=long_description,
    url='https://github.com/prasoon-uta/IBM-coud-storage',
    license='Apache-2.0', install_requires=['pyDes', 'python-swiftclient','flask', 'python-keystoneclient']
)