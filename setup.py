# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='learm',
    version='0.0.1',
    description='Hiwonder Learm Controller',
    long_description=readme,
    author='Andrew Dassonville',
    author_email='dassonville.andrew@gmail.com',
    url='https://github.com/andrewda/learm',
    license=license,
    packages=find_packages(),
)
