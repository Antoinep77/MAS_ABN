#!/usr/bin/env python3


class Comparison:
    """Comparison class.
    This class implements a comparison object used in argument object.

    attr:
        best_criterion_name:
        worst_criterion_name:
    """

    def __init__(self, best_criterion_name, worst_criterion_name):
        """Creates a new comparison.
        """
        self.__best_criterion_name = best_criterion_name
        self.__worst_criterion_name = worst_criterion_name

    def parse(self):
        return self.__best_criterion_name,self.__worst_criterion_name

    def __str__(self):
        """Returns Item as a String.
        """
        return str(self.__best_criterion_name) + " > " + str(self.__worst_criterion_name)
    
    def __eq__(self, other):
        return self.__best_criterion_name ==  other.__best_criterion_name and self.__worst_criterion_name ==  other.__worst_criterion_name
