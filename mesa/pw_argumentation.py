from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.Preferences import Preferences
from communication.preferences.Item import Item
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Value import Value






class ArgumentAgent(CommunicatingAgent):
    """ ArgumentAgent which inherit from CommunicatingAgent.
    """
    def __init__(self, unique_id, model, name,criterions):
        super().__init__(unique_id, model, name)
        self.preference = Preferences()
        self.preference.set_criterion_name_list(criterions)

    def step(self):
        super().step()

    def get_preference(self):
        return self.preference

    def generate_random_preferences(self, item):
        for criterion in self.preference.get_criterion_name_list():
            value = self.model.random.choice(list(Value))
            self.preference.add_criterion_value(CriterionValue(item,criterion,value))

class ArgumentModel(Model):
    """ ArgumentModel which inherit from Model.
    """
    def __init__(self,nb_items):
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)
        self.next_id = 0
        
        agent1 = ArgumentAgent(self.get_next_id(),self, "agent1",[ CriterionName.ENVIRONMENT_IMPACT, CriterionName.NOISE,
                                        CriterionName.CONSUMPTION, CriterionName.DURABILITY ])
        agent2 = ArgumentAgent(self.get_next_id(),self, "agent2",[CriterionName.PRODUCTION_COST,CriterionName.CONSUMPTION, CriterionName.NOISE])

        items = [Item("Item{}".format(self.get_next_id()), "Some random item") for _ in range(nb_items)]

        for item in items:
            agent1.generate_random_preferences(item)
            agent2.generate_random_preferences(item)

        
        self.schedule.add(agent1)
        self.schedule.add(agent2)


        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()

    def get_next_id(self):
        self.next_id += 1
        return self.next_id




if __name__ == "__main__":
    argument_model = ArgumentModel(20)

  # To be completed
