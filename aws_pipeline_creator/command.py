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
@click.version_option(version='0.0.7')
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



