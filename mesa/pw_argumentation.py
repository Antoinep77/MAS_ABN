from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
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
        self.items = set()
        self.committed_items = set()


    def handle_propose_message(self,m):
        if self.preference.is_item_among_top_10_percent(m.get_content(),self.items):
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.ACCEPT,m.get_content()))
        else:
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.ASK_WHY,m.get_content()))

    def handle_accept_message(self,m):
        if True:
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.COMMIT,m.get_content()))
            self.committed_items.add(m.get_content())
        else:
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.ARGUE,m.get_content()))

    def handle_commit_message(self,m):
        if m.get_content() not in self.committed_items:
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.COMMIT,m.get_content()))
            self.committed_items.add(m.get_content())

    def handle_ask_why_message(self,m):
        pass


    def step(self):
        super().step()
        messages = self.get_new_messages()
        handlers={
                MessagePerformative.PROPOSE:self.handle_propose_message,
                MessagePerformative.ASK_WHY:self.handle_ask_why_message,
                MessagePerformative.ACCEPT: self.handle_accept_message,
                MessagePerformative.COMMIT: self.handle_commit_message,
            }
        for m in messages:
            handlers[m.get_performative()](m)


    def get_preference(self):
        return self.preference

    def generate_random_preferences(self, item):
        self.items.add(item)
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

        agent1.send_message(Message("agent1","agent2",MessagePerformative.PROPOSE,items[0]))

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()

    def get_next_id(self):
        self.next_id += 1
        return self.next_id

    def run_n_steps(self,n):
        for _ in range(n):
            self.step()




if __name__ == "__main__":
    argument_model = ArgumentModel(20)
    argument_model.run_n_steps(50)
  # To be completed
