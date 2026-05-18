from __future__ import annotations

from dataclasses import dataclass

from cards import Card, cards_to_text


MOVE_NAMES = {
    "S": "single",
    "D": "pair",
    "T": "triple",
    "JJ": "rocket",
    "Q": "bomb",
    "T1": "triple with single",
    "T2": "triple with pair",
    "Q1": "four with one",
    "Q2": "four with two",
    "Q3": "four with three",
    "SOS": "straight",
    "SOD": "pair chain",
    "SOT": "triple chain",
    "SOT1": "airplane with single wings",
    "SOT2": "airplane with pair wings",
}


@dataclass(frozen=True)
class Move:
    kind: str
    cards: tuple[Card, ...]
    main_value: int

    @property
    def size(self) -> int:
        return len(self.cards)

    @property
    def name(self) -> str:
        return MOVE_NAMES.get(self.kind, self.kind)

    def text(self) -> str:
        return cards_to_text(self.cards)
