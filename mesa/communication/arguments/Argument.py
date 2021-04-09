#!/usr/bin/env python3

from communication.arguments.Comparison import Comparison
from communication.arguments.CoupleValue import CoupleValue


class Argument:
    """Argument class.
    This class implements an argument used in the negotiation.

    attr:
        decision:
        item:
        comparison_list:
        couple_values_list:
    """

    def __init__(self, boolean_decision, item):
        """Creates a new Argument.
        """
        self.__decision = boolean_decision
        self.__item = item
        self.__comparison_list = []
        self.__couple_values_list = []

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        """Adds a premiss comparison in the comparison list.
        """
        self.__comparison_list.append(Comparison(criterion_name_1, criterion_name_2))

    def add_premiss_couple_values(self, criterion_name, value):
        """Add a premiss couple values in the couple values list.
        """
        self.__couple_values_list.append(CoupleValue(criterion_name, value))


    def parse(self):
        if len(self.__comparison_list) == 0:
            return (self.__item,self.__decision,self.__couple_values_list[0],None)
        return (self.__item,self.__decision,self.__couple_values_list[0],self.__comparison_list[0])

    def __str__(self):
        """Returns Item as a String.
        """
        if len(self.__comparison_list) == 0:
            return  ("not " if  not self.__decision else "") + str(self.__item.get_name()) + ": " + str(self.__couple_values_list[0])
        return ("not " if not self.__decision else "") + str(self.__item.get_name()) + ": " + str(self.__comparison_list[0])+ " and " + str(self.__couple_values_list[0])

    def __eq__(self, other):
        item, decision, cv_prem, comp_prem = self.parse() 
        item2, decision2, cv_prem2, comp_prem2 = other.parse()
        comp_prem_eq = (comp_prem is None and comp_prem2 is None)  or ((comp_prem is not None and comp_prem2 is not None) and comp_prem == comp_prem2)
        return decision == decision2 and item.get_name() == item2.get_name() and cv_prem == cv_prem2 and comp_prem_eq
