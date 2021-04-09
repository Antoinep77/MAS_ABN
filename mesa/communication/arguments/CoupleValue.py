#!/usr/bin/env python3


class CoupleValue:
    """CoupleValue class.
    This class implements a couple value used in argument object.

    attr:
        criterion_name:
        value:
    """

    def __init__(self, criterion_name, value):
        """Creates a new couple value.
        """
        self.__criterion_name = criterion_name
        self.__value = value

    def __str__(self):
        """Returns Item as a String.
        """
        return str(self.__criterion_name) + ": " + str(self.__value)
    
    def __eq__(self, other):
        return self.__criterion_name ==  other.__criterion_name and self.__value ==  other.__value


    def parse(self):
        return self.__criterion_name,self.__value