from enum import IntEnum
from random import randint


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
        return 1, 15
    elif kind == AntKind.SHARED_2:
        return 2, 14
    elif kind == AntKind.SHARED_3:
        return 3, 13
    elif kind == AntKind.SHARED_13:
        return 13, 3
    elif kind == AntKind.SHARED_14:
        return 14, 2
    elif kind == AntKind.SHARED_15:
        return 15, 1
    elif kind == AntKind.COMPETITIVE_4:
        return 4
    elif kind == AntKind.COMPETITIVE_5:
        return 5
    elif kind == AntKind.COMPETITIVE_6:
        return 6

