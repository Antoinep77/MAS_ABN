#!/usr/bin/env python3

from enum import Enum


class MessagePerformative(Enum):
    """MessagePerformative enum class.
    Enumeration containing the possible message performative.
    """
    PROPOSE = 101
    ACCEPT = 102
    COMMIT = 103
    ASK_WHY = 104
    ARGUE = 105
    QUERY_REF = 106
    INFORM_REF = 107
    TERMINATE = 108
    DONT_KNOW = 109



    def __str__(self):
        """Returns the name of the enum item.
        """
        color_codes = {
            MessagePerformative.PROPOSE:"\033[93m",
            MessagePerformative.ACCEPT:"\033[94m",
            MessagePerformative.ARGUE:"\033[31m",
            MessagePerformative.COMMIT:"\033[92m",
            MessagePerformative.ASK_WHY:"\033[95m",
            MessagePerformative.QUERY_REF:"\033[0m",
            MessagePerformative.INFORM_REF:"\033[0m",
            MessagePerformative.TERMINATE:"\033[0m",
            MessagePerformative.DONT_KNOW:"\033[0m",

        }
        return '{0}{1}\033[0m'.format(color_codes[self],self.name)
