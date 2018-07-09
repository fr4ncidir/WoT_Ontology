#!/usr/bin/python3

# global requirements
import logging


class BasicHandler:

    """A simple example of an Handler class"""
    
    # constructor
    def __init__(self, kp=None):

        """This is the constructor for the example handler"""

        # get a logger
        self.logger = logging.getLogger("sepaLogger")
        self.logger.debug("=== BasicHandler::__init__ invoked ===")
        
        # store the kp
        self.kp = kp


    # handle notifications
    def handle(self, added,removed):

        # print the notification
        self.logger.debug("=== BasicHandler::handle\nreceived the following added: {}\nand the following removed: {}".format(added,removed))
