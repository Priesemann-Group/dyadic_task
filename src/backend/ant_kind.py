from enum import IntEnum
from random import randint
import configuration.conf as conf

_high_coop = int(conf.coop_reward * (1 - conf.coop_split))
_low_coop = int(conf.coop_reward * conf.coop_split)


class AntKind(IntEnum):
    SHARED_1 = 0
    SHARED_2 = 1
    SHARED_3 = 2
    SHARED_13 = 3
    SHARED_14 = 4
    SHARED_15 = 5
    COMPETITIVE_4 = 6
    COMPETITIVE_5 = 7
    COMPETITIVE_6 = 8


def ant_from_same_category(ant_kind):
    if ant_kind < 3:
        return AntKind(randint(0, 2))
    elif ant_kind < 6:
        return AntKind(randint(3, 5))
    else:
        return AntKind(randint(6, 8))


def is_shared(ant_kind):
    return ant_kind < 6


def get_score(kind):
    if kind == AntKind.SHARED_1:
        return _low_coop - 1, _high_coop + 1
    elif kind == AntKind.SHARED_2:
        return _low_coop, _high_coop
    elif kind == AntKind.SHARED_3:
        return _low_coop + 1, _high_coop - 1
    elif kind == AntKind.SHARED_13:
        return _high_coop + 1, _low_coop - 1
    elif kind == AntKind.SHARED_14:
        return _high_coop, _low_coop
    elif kind == AntKind.SHARED_15:
        return _high_coop - 1, _low_coop + 1
    elif kind == AntKind.COMPETITIVE_4:
        return conf.comp_reward - 1
    elif kind == AntKind.COMPETITIVE_5:
        return conf.comp_reward
    elif kind == AntKind.COMPETITIVE_6:
        return conf.comp_reward + 1

