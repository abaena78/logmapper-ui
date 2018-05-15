# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 09:19:53 2017

@author: abaena
"""

import os
import configparser
import logging
import enum


__version__ = "0.0.1"



class LogMapperMasterState(enum.Enum):
    STARTING = 0
    READING = 1


logger = logging.getLogger(__name__)

CONFIGFILE_NAME = "conf.ini"

SECTION_LOGMAPPER = "LOGMAPPER"
PROP_MASTERPORT = "master.port" 
PROP_WORKINGPATH = "working.path"
PROP_DEBUGLEVEL = "logger.debug.level"
PROP_LOGFILE = "logger.file"


def loadConfig(filepath=CONFIGFILE_NAME):
    """
    Load initial config file. 
    If the file not exist create a new one.
    Return ConfigParser Class. Query setting with: config.get(section, key)
    """  
    # Check if there is already a configurtion file
    if not os.path.isfile(filepath):
        createDefaultConfigfile()
        
    config = configparser.ConfigParser()
    config.read(filepath)
    return config 


def printConfig(config):
    """
    Print in logger config data
    """
    for section in config.sections():
        for key in config[section]: 
            print(section+'.'+key+'='+config.get(section, key))
       

def saveConfig(config):
    """
    Create configfile with Default Data
    """  
    # Create the configuration file as it doesn't exist yet
    cfgfile = open(CONFIGFILE_NAME, 'w')
    config.write(cfgfile)
    cfgfile.close()  
        
  

def createDefaultConfigfile():
    """
    Create configfile with Default Data
    """  

    # Add content to the file
    config = configparser.ConfigParser()
    config.add_section(SECTION_LOGMAPPER)
    config.set(SECTION_LOGMAPPER, PROP_MASTERPORT, '5005')

    config.set(SECTION_LOGMAPPER, PROP_WORKINGPATH, '/tmp')
    config.set(SECTION_LOGMAPPER, PROP_DEBUGLEVEL, 'INFO')
    config.set(SECTION_LOGMAPPER, PROP_LOGFILE, '/tmp/lmpa.log')
    
    saveConfig(config)

if __name__ == '__main__':
    createDefaultConfigfile()
    config=loadConfig()     
    printConfig(config)