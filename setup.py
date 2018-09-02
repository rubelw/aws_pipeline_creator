#!/usr/bin/env python

from __future__ import absolute_import, division, print_function
from setuptools import setup, find_packages
import sys


DESCRIPTION = ("Creates AWS Codepipeline.")
LONG_DESCRIPTION = open('README.rst').read()
VERSION = '0.0.3'

setup_requires = (
    ['pytest-runner'] if any(x in sys.argv for x in ('pytest', 'test', 'ptr')) else []
)

setup(
    name='aws_pipeline_creator',
    version=VERSION,
    description=DESCRIPTION,
    url='https://github.com/rubelw/aws_pipeline_creator',
    author='Will Rubel',
    author_email='willrubel@gmail.com',
    long_description=LONG_DESCRIPTION,
    platforms=["any"],
    packages=find_packages(),
    include_package_data=True,
    setup_requires=setup_requires,
    tests_require=['pytest','mock'],
    test_suite="aws_pipeline_creator.tests",
    install_requires=[
        "boto3>=1.4.3",
        "requests>=2.18",
        "Click>=6.7",
        "configparser>=3.5.0",
        "future>=0.16.0",
        "six>=1.11.0",
        "pip"
    ],
    keywords=['aws', 'codebuild', 'pipeline', 'creator'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    entry_points="""
        [console_scripts]
        pipeline-creator=aws_pipeline_creator.command:cli
    """
)