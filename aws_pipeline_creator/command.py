"""
The command line interface to cfn_nagger.

"""
from __future__ import absolute_import, division, print_function
import sys
import inspect
import logging
import os
import time
import traceback
from configparser import RawConfigParser
import boto3
import click
import aws_pipeline_creator
from aws_pipeline_creator import PipelineCreator


def lineno():
    """Returns the current line number in our program."""
    return str(' - PipelineCreator - line number: '+str(inspect.currentframe().f_back.f_lineno))


@click.group()
@click.version_option(version='0.0.9')
def cli():
    pass


@cli.command()
@click.option('--version', '-v', help='code version')
@click.option('--dryrun', '-d', help='dry run', is_flag=True)
@click.option('--no-poll', help='Start the stack work but do not poll', is_flag=True)
@click.option('--ini', '-i', help='INI file with needed information', required=True)
@click.option('--debug', help='Turn on debugging', required=False, is_flag=True)
def upsert(
        version,
        dryrun,
        no_poll,
        ini,
        debug
    ):
    '''
    primary function for creating a pipeline
    :return:
    '''

    ini_data = read_config_info(ini,debug)
    if 'environment' not in ini_data:
        print('[environment] section is required in the INI file')
        sys.exit(1)

    if 'template' in ini_data['environment']:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ini_data['environment']['template']= str(dir_path)+'/'+str(ini_data['environment']['template'])

    if 'region' not in ini_data['environment']:
        ini_data['environment']['region'] = find_myself()

    ini_data['no_poll'] = bool(no_poll)
    ini_data['dryrun'] = bool(dryrun)

    ini_data['cwd'] = str(os.getcwd())

    if version:
        ini_data['codeVersion'] = version
    else:
        ini_data['codeVersion'] = str(int(time.time()))

    print(ini_data)

    if 'meta-parameters' in ini_data:
        if 'ProjectName' in ini_data['meta-parameters']:
            project_name = ini_data['meta-parameters']['ProjectName']
        else:
            print('Need to have ProjectName in meta-parameters')
            sys.exit(1)

    else:
        print('Need to have meta-parameters in template to set the cloudformation template project name')
        sys.exit(1)

    if version:
        myversion()
    else:
        start_create(
            ini_data,
            debug,
            project_name
        )


@cli.command()
@click.option('--ini', '-i', help='INI file with needed information', required=True)
@click.option('--debug', help='Turn on debugging', required=False, is_flag=True)
def delete(ini, debug):
    """
    Delete the given CloudFormation stack.
    Args:
        stack - [required] indicatate the stack to smash
        region - [optional] indicate where the stack is located
        profile - [optionl[ AWS crendential profile
    Returns:
       sys.exit() - 0 is good and 1 is bad
    """

    ini_data = read_config_info(ini,debug)
    ini_data['cwd'] = str(os.getcwd())


    if 'meta-parameters' in ini_data:
        if 'ProjectName' in ini_data['meta-parameters']:
            project_name = ini_data['meta-parameters']['ProjectName']
        else:
            print('Need to have ProjectName in meta-parameters')
            sys.exit(1)

    else:
        print('Need to have meta-parameters in template to set the cloudformation template project name')
        sys.exit(1)

    if start_smash(ini_data, debug, project_name):
        sys.exit(0)
    else:
        sys.exit(1)


@click.option('--version', '-v', help='Print version and exit', required=False, is_flag=True)
def version(version):
    """
    Get version
    :param version:
    :return:
    """
    myversion()


def myversion():
    '''
    Gets the current version
    :return: current version
    '''
    print('Version: ' + str(aws_pipeline_creator.__version__))

def start_smash(
        ini,
        debug,
        project_name
    ):
    """
    Facilitate the smashing of a CloudFormation stack
    Args:
        command_line - a dictionary to of info to inform the operation
    Returns:
       True if happy else False
    """
    creator = PipelineCreator(ini,debug,project_name)

    if debug:
        print('Starting delete')

    if creator.smash():
        if debug:
            print('deleted')
    else:
        if debug:
            print('not deleted')


def start_create(
        ini,
        debug,
        project_name
    ):
    '''
    Starts the creation
    :return:
    '''
    if debug:
        print('command - start_create'+lineno())
        print('ini data: '+str(ini)+lineno())



    creator = PipelineCreator(ini,debug,project_name)
    if debug:
        print('print have PipelineCreator')
    if creator.create():
        if debug:
            print('created')
    else:
        if debug:
            print('not created')

def find_myself():
    """
    Find myself
    Args:
        None
    Returns:
       An Amazon region
    """
    my_session = boto3.session.Session()
    return my_session.region_name

def read_config_info(ini_file,debug):
    """
    Read the INI file
    Args:
        ini_file - path to the file
    Returns:
        A dictionary of stuff from the INI file
    Exits:
        1 - if problems are encountered
    """
    try:
        config = RawConfigParser()
        config.optionxform = lambda option: option
        config.read(ini_file)
        the_stuff = {}
        for section in config.sections():
            the_stuff[str(section)] = {}
            for option in config.options(section):
                the_stuff[str(section)][str(option)] = str(config.get(section, option.replace('\n', '')))


        if debug:
            print('ini data: '+str(the_stuff))

        return the_stuff
    except Exception as wtf:
        logging.error('Exception caught in read_config_info(): {}'.format(wtf))
        traceback.print_exc(file=sys.stdout)
        return sys.exit(1)



