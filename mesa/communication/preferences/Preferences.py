#!/usr/bin/env python3

from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value
from communication.arguments.Argument import Argument


class Preferences:
    """Preferences class.
    This class implements the preferences of an agent.

    attr:
        criterion_name_list: the list of criterion name (ordered by importance)
        criterion_value_list: the list of criterion value
    """

    def __init__(self):
        """Creates a new Preferences object.
        """
        self.__criterion_name_list = []
        self.__criterion_value_list = []

    def get_criterion_name_list(self):
        """Returns the list of criterion name.
        """
        return self.__criterion_name_list

    def get_criterion_value_list(self):
        """Returns the list of criterion value.
        """
        return self.__criterion_value_list

    def set_criterion_name_list(self, criterion_name_list):
        """Sets the list of criterion name.
        """
        self.__criterion_name_list = criterion_name_list

    def add_criterion_value(self, criterion_value):
        """Adds a criterion value in the list.
        """
        self.__criterion_value_list.append(criterion_value)

    def get_value(self, item, criterion_name):
        """Gets the value for a given item and a given criterion name.
        """
        for value in self.__criterion_value_list:
            if value.get_item() == item and value.get_criterion_name() == criterion_name:
                return value.get_value()
        return None

    def is_preferred_criterion(self, criterion_name_1, criterion_name_2):
        """Returns if a criterion 1 is preferred to the criterion 2.
        """
        for criterion_name in self.__criterion_name_list:
            if criterion_name == criterion_name_2:
                return False
            if criterion_name == criterion_name_1:
                return True

    def is_preferred_item(self, item_1, item_2):
        """Returns if the item 1 is preferred to the item 2.
        """
        return item_1.get_score(self) > item_2.get_score(self)

    def most_preferred(self, item_list):
        """Returns the most preferred item from a list.
        """
        # To be completed
        best_item = item_list[0]
        for item in item_list[1:]:
            if self.is_preferred_item(item, best_item):
                #then current item is better than best item, update it
                best_item = item
                        
        return best_item

    def is_item_among_top_10_percent(self, item, items):
        """
        Return whether a given item is among the top 10 percent of the preferred items.

        :return: a boolean, True means that the item is among the favourite ones
        """
        #start at 0 as we will add 1 for the item itself
        item_position = 0
        for item2 in items:
            if self.is_preferred_item(item2,item):
                item_position += 1
        return item_position <= len(items)//10

    def list_supporting_proposal(self, item):
        """Generate a list of arguments which can be used to support an item
        :param item: Item - name of the item
        :return: list of all arguments PRO an item (sorted by order of importance based on agent's preferences)
        """
        couple_values =  [ (criterion,self.get_value(item,criterion)) for criterion in self.get_criterion_name_list()]
        arguments = []
        for criterion,value in couple_values:
            if value == Value.VERY_GOOD or value == Value.GOOD:
                argument = Argument(True,item)
                argument.add_premiss_couple_values(criterion,value)
                arguments.append(argument)
        return arguments

    def list_attacking_proposal(self, item):
        """Generate a list of arguments which can be used to attack an item
        :param item: Item - name of the item
        :return: list of all arguments CON an item (sorted by order of importance based on preferences)
        """
        couple_values =  [ (criterion,self.get_value(item,criterion)) for criterion in self.get_criterion_name_list()]
        for criterion,value in couple_values:
            arguments = []
            if value == Value.BAD or value == Value.VERY_BAD:
                argument = Argument(False,item)
                argument.add_premiss_couple_values(criterion,value)
                arguments.append(argument)
        return arguments


    def support_proposal(self, item):
        """
        Used when the agent recieves "ASK_WHY" after having proposed an item
        :param item: str - name of the item which was proposed
        :return: string - the strongest supportive argument
        """
        arguments = self.list_supporting_proposal(item)
        return arguments[0]

    def attack_cv_premiss(self,all_items,cv_premiss,argued_item,decision):
        criterion,value = cv_premiss.parse()
        #item with better value for criterion
        arguments = []
        if decision:
            for item in all_items:
                if self.get_value(item,criterion).value > value.value:
                    argument = Argument(True,item)
                    argument.add_premiss_couple_values(criterion,self.get_value(item,criterion))
                    arguments.append(argument)

        #item has worst or better (depending on decision) value for the criterion to the agent
        if (( decision and self.get_value(argued_item,criterion).value < value.value) or (not decision and self.get_value(argued_item,criterion).value> value.value)):
            argument = Argument(not decision,argued_item)
            argument.add_premiss_couple_values(criterion,self.get_value(argued_item,criterion))
            arguments.append(argument)
        
        for criterion2 in self.__criterion_name_list:
            if self.is_preferred_criterion(criterion2,criterion) and (
              (decision and self.get_value(argued_item,criterion2).value <=  Value.BAD.value)
              or (not decision and self.get_value(argued_item,criterion2).value >=  Value.GOOD.value )):
                argument = Argument(not decision,argued_item)
                argument.add_premiss_couple_values(criterion2,self.get_value(argued_item,criterion2))
                argument.add_premiss_comparison(criterion2,criterion)
                arguments.append(argument)
        
        return arguments

    def attack_composed_premiss(self,all_items,cv_premiss,crit_compare_premiss,argued_item,decision):
        criterion,value = cv_premiss.parse()
        criterion1,criterion2 = crit_compare_premiss.parse()
        assert criterion == criterion1
        arguments = []
        #item with better value for criterion
        if decision:
            for item in all_items:
                if self.get_value(item,criterion).value > value.value:
                    argument = Argument(True,item)
                    argument.add_premiss_couple_values(criterion,self.get_value(item,criterion))
                    arguments.append(argument)

        if self.is_preferred_criterion(criterion2,criterion1):
            argument = Argument(not decision,argued_item)
            argument.add_premiss_couple_values(criterion2,self.get_value(argued_item,criterion2))
            argument.add_premiss_comparison(criterion2,criterion1)
            arguments.append(argument)

        return arguments

    def get_attacking_arguments(self,all_items,argument):
        argued_item,decision,couple_value_premiss,criterion_comparison_premiss = argument.parse()
        if criterion_comparison_premiss is None:
            return self.attack_cv_premiss(all_items,couple_value_premiss,argued_item,decision)
        else:
           return self.attack_composed_premiss(all_items,couple_value_premiss,criterion_comparison_premiss,argued_item,decision)


if __name__ == '__main__':
    """Testing the Preferences class.
    """
    agent_pref = Preferences()
    agent_pref.set_criterion_name_list([CriterionName.PRODUCTION_COST, CriterionName.ENVIRONMENT_IMPACT,
                                        CriterionName.CONSUMPTION, CriterionName.DURABILITY,
                                        CriterionName.NOISE])

    diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
    agent_pref.add_criterion_value(CriterionValue(diesel_engine, CriterionName.PRODUCTION_COST,
                                                  Value.VERY_GOOD))
    agent_pref.add_criterion_value(CriterionValue(diesel_engine, CriterionName.CONSUMPTION,
                                                  Value.GOOD))
    agent_pref.add_criterion_value(CriterionValue(diesel_engine, CriterionName.DURABILITY,
                                                  Value.VERY_GOOD))
    agent_pref.add_criterion_value(CriterionValue(diesel_engine, CriterionName.ENVIRONMENT_IMPACT,
                                                  Value.VERY_BAD))
    agent_pref.add_criterion_value(CriterionValue(diesel_engine, CriterionName.NOISE,
                                                  Value.VERY_BAD))

    electric_engine = Item("Electric Engine", "A very quiet engine")
    agent_pref.add_criterion_value(CriterionValue(electric_engine, CriterionName.PRODUCTION_COST,
                                                  Value.BAD))
    agent_pref.add_criterion_value(CriterionValue(electric_engine, CriterionName.CONSUMPTION,
                                                  Value.VERY_BAD))
    agent_pref.add_criterion_value(CriterionValue(electric_engine, CriterionName.DURABILITY,
                                                  Value.GOOD))
    agent_pref.add_criterion_value(CriterionValue(electric_engine, CriterionName.ENVIRONMENT_IMPACT,
                                                  Value.VERY_GOOD))
    agent_pref.add_criterion_value(CriterionValue(electric_engine, CriterionName.NOISE,
                                                  Value.VERY_GOOD))

    """test list of preferences"""
    print(diesel_engine)
    print(electric_engine)
    print(diesel_engine.get_value(agent_pref, CriterionName.PRODUCTION_COST))
    print(agent_pref.is_preferred_criterion(CriterionName.CONSUMPTION, CriterionName.NOISE))
    print('Electric Engine > Diesel Engine : {}'.format(agent_pref.is_preferred_item(electric_engine, diesel_engine)))
    print('Diesel Engine > Electric Engine : {}'.format(agent_pref.is_preferred_item(diesel_engine, electric_engine)))
    print('Electric Engine (for agent 1) = {}'.format(electric_engine.get_score(agent_pref)))
    print('Diesel Engine (for agent 1) = {}'.format(diesel_engine.get_score(agent_pref)))
    print('Most preferred item is : {}'.format(agent_pref.most_preferred([diesel_engine, electric_engine]).get_name()))
    print('Is Electric Engine in top 10%: {}'.format(agent_pref.is_item_among_top_10_percent(electric_engine,[diesel_engine, electric_engine])))
    print('Is Diesel Engine in top 10%: {}'.format(agent_pref.is_item_among_top_10_percent(diesel_engine,[diesel_engine, electric_engine])))
