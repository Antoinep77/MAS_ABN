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

import numpy as np





class ArgumentAgent(CommunicatingAgent):
    """ ArgumentAgent which inherit from CommunicatingAgent.
    """
    def __init__(self, unique_id, model, name,criterions):
        super().__init__(unique_id, model, name)
        self.preference = Preferences()
        self.preference.set_criterion_name_list(criterions)
        self.items = set()
        self.committed_items = []
        self.rejected_items = set()
        self.arguments_used = []
        self.victory_count = 0
        self.propositions = 0
        self.accepted_propositions = 0
        self.is_proposed_by_me = False
        self.vote_to_halt = False

    
    def propose_preferred_item(self,exp):
        selectable_items = list(self.items.difference(set(self.committed_items)).difference(self.rejected_items))
        if len(selectable_items) > 0:
            preferred_item = self.preference.most_preferred(selectable_items)      
            self.send_message(Message(self.get_name(),exp,MessagePerformative.PROPOSE,preferred_item))
            self.is_proposed_by_me = True
            self.propositions +=1
        else:
            self.send_message(Message(self.get_name(),exp,MessagePerformative.TERMINATE,self.committed_items))
            self.vote_to_halt = True

    def handle_propose_message(self,m):
        self.is_proposed_by_me = False
        if self.preference.is_item_among_top_10_percent(m.get_content(),self.items):
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.ACCEPT,m.get_content()))
        else:
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.ASK_WHY,m.get_content()))

    def handle_accept_message(self,m):
        self.victory_count += 1
        self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.COMMIT,m.get_content()))
        self.committed_items.append(m.get_content())

    def handle_commit_message(self,m):
        if self.is_proposed_by_me:
            self.accepted_propositions += 1
        if m.get_content() not in self.committed_items:
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.COMMIT,m.get_content()))
            self.committed_items.append(m.get_content())
        else:
            self.propose_preferred_item(m.get_exp())


    def handle_ask_why_message(self,m):
        argument = self.preference.support_proposal(m.get_content())
        if argument:
            self.arguments_used.append(argument)
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.ARGUE,argument))
        else:
            self.rejected_items.add(m.get_content())
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.DONT_KNOW,m.get_content()))


    def handle_argue_message(self,m):
        incoming_argument = m.get_content()
        selectable_items = list(self.items.difference(set(self.committed_items)).difference(self.rejected_items))
        arguments = self.preference.get_attacking_arguments(selectable_items, incoming_argument)
        arguments = list(filter(lambda arg: arg not in self.arguments_used,arguments))
        if len(arguments) > 0:
            argument = self.model.random.choice(arguments)
            self.arguments_used.append(argument)
            self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.ARGUE,argument ))
        else:
            item, decision,_,_ = incoming_argument.parse()
            if decision: #no argument against item 
                self.send_message(Message(self.get_name(),m.get_exp(),MessagePerformative.ACCEPT,item))
            else: #no argument pro item
                self.rejected_items.add(item)
                self.propose_preferred_item(m.get_exp())

    def handle_terminate_message(self,m):
        self.vote_to_halt = True
        if m.get_content()!=self.committed_items:
            raise Exception("Differents commit items")
    
    def handle_dont_know_message(self,m):
        self.propose_preferred_item(m.get_exp())

    def step(self):
        super().step()
        messages = self.get_new_messages()
        handlers={
                MessagePerformative.PROPOSE:self.handle_propose_message,
                MessagePerformative.ASK_WHY:self.handle_ask_why_message,
                MessagePerformative.ACCEPT: self.handle_accept_message,
                MessagePerformative.COMMIT: self.handle_commit_message,
                MessagePerformative.ARGUE: self.handle_argue_message,
                MessagePerformative.TERMINATE: self.handle_terminate_message,
                  MessagePerformative.DONT_KNOW: self.handle_dont_know_message,
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
        self.step_index = 0
        criterions = [CriterionName.ENVIRONMENT_IMPACT, CriterionName.NOISE, CriterionName.CONSUMPTION, CriterionName.DURABILITY,CriterionName.PRODUCTION_COST ]
        self.random.shuffle(criterions)
        self.agent1 = ArgumentAgent(self.get_next_id(),self, "agent1",criterions)
        self.random.shuffle(criterions)
        self.agent2 = ArgumentAgent(self.get_next_id(),self, "agent2",criterions)

        items = [Item("Item{}".format(self.get_next_id()), "Some random item") for _ in range(nb_items)]

        for item in items:
            self.agent1.generate_random_preferences(item)
            self.agent2.generate_random_preferences(item)
        
        self.schedule.add(self.agent1)
        self.schedule.add(self.agent2)
        self.running = True

        self.agent1.propose_preferred_item("agent2")

    def step(self):
        self.step_index += 1
        self.__messages_service.dispatch_messages()
        self.schedule.step()

    def get_next_id(self):
        self.next_id += 1
        return self.next_id

    def run_n_steps(self,n):
        for _ in range(n):
            self.step()
    
    def run(self):
        while not self.agent1.vote_to_halt or not self.agent2.vote_to_halt:
            self.step()

    def show_stats(self):
        print()
        print("Number of steps to converge: {0} for {1} items".format(self.step_index,len(self.agent1.items)))
        print()
        for agent in [self.agent1,self.agent2]: 
            print("Stats for: ",agent.get_name())
            print("Victories: ", agent.victory_count)
            print("Acceptation rate: ", agent.accepted_propositions/agent.propositions)
            mean_scores_ratio = np.mean([item.get_score(agent.preference) for item in agent.committed_items])/np.mean([item.get_score(agent.preference) for item in agent.items])
            print("Committed items mean score ratio: ",mean_scores_ratio)
            print()




if __name__ == "__main__":
    argument_model = ArgumentModel(100)
    argument_model.run()
    argument_model.show_stats()

  # To be completed
