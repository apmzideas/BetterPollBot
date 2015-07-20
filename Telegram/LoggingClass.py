#!/usr/bin/python

''' a logging tool'''

__author__ = "Adrian Hornung"
__copyright__ = "Copyright (C) Adrian Hornung 2013-2015"
__credits__ = ["Adrian Hornung"]
__license__ = "License GNU General Public License https://www.gnu.org/copyleft/gpl.html"
__version__ = "0.1"
__maintainer__ = "Adrian Hornung"
__email__ = "hornung.adrian@gmial.com"
__status__ = "Development"

import logging
import logging.config


#read logging info
class Logger(object):

    def __init__(self, config_name='config.ini', log_to_file=True):
        self.config_name = config_name
        self.log_to_file = log_to_file

        try:
            if self.log_to_file is True:
                logging.config.fileConfig(self.config_name)
                self.logger = logging.getLogger('root')
            elif self.log_to_file is not True:
                logging.config.fileConfig(self.config_name)
                self.logger = logging.getLogger('Console')
            else:
                logging.basicConfig(filename='log.txt', format='%(asctime)s - %(levelname)s - %(message)s',datefmt='%d/%M/%Y %H:%M:%S', level=logging.DEBUG)
                logging.debug('There was an ERROR whit the .ini log to file option, please try again')
        except:
            logging.basicConfig(filename='log.txt', format='%(asctime)s - %(levelname)s - %(message)s',datefmt='%d/%M/%Y %H:%M:%S', level=logging.DEBUG)

    def create_log(self, message, option='info'):
        getattr(self.logger, option)(message)

if __name__ == '__main__':

    #c = conf()
    #log_to = c.read_ini('LOG').getboolean('log to file')
    log_to = False
    c = Logger(log_to_file=log_to)
    c.create_log('this is a test')
    c.create_log('this is a Error', 'error')
    # 'application' code
    c.logger.debug('debug message')
    c.logger.info('info message')
    c.logger.warn('warn message')
    c.logger.error('error message')
    c.logger.critical('critical message')

