from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = ROOT / "images"

RANK_ORDER = {
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
    "2": 15,
    "JokerB": 16,
    "JokerR": 17,
}

CHAIN_RANK_ORDER = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}
CHAIN_RANKS = set(CHAIN_RANK_ORDER)

NORMAL_RANKS = {"A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"}
SUITS = {"H", "C", "D", "S"}
SUIT_ORDER = {"H": 0, "C": 1, "D": 2, "S": 3, None: 4}
DECK_RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK_SUITS = ["H", "C", "D", "S"]


@dataclass(frozen=True)
class Card:
    code: str
    rank: str
    suit: str | None
    value: int


def normalize_card_code(raw_code: str) -> str:
    code = raw_code.strip()
    if not code:
        raise ValueError("Empty card name.")

    joker_lookup = {"jokerb": "JokerB", "jokerr": "JokerR"}
    if code.lower() in joker_lookup:
        return joker_lookup[code.lower()]

    if len(code) < 2:
        raise ValueError(f"Invalid card name: {raw_code!r}")

    rank = code[:-1].upper()
    suit = code[-1].upper()
    if rank == "1":
        rank = "10"

    if rank not in NORMAL_RANKS or suit not in SUITS:
        raise ValueError(f"Invalid card name: {raw_code!r}")

    return f"{rank}{suit}"


def parse_card(raw_code: str) -> Card:
    code = normalize_card_code(raw_code)
    if code in {"JokerB", "JokerR"}:
        return Card(code=code, rank=code, suit=None, value=RANK_ORDER[code])

    rank = code[:-1]
    suit = code[-1]
    return Card(code=code, rank=rank, suit=suit, value=RANK_ORDER[rank])


def parse_card_input(text: str) -> list[Card]:
    if not text.strip():
        return []

    raw_parts = text.split(",")
    parts = [part.strip() for part in raw_parts]
    if any(part == "" for part in parts):
        raise ValueError("Card names must be separated by commas.")

    return [parse_card(part) for part in parts]


def build_deck(shuffle: bool = True, rng: random.Random | None = None) -> list[Card]:
    cards = [parse_card(f"{rank}{suit}") for suit in DECK_SUITS for rank in DECK_RANKS]
    cards.extend([parse_card("JokerB"), parse_card("JokerR")])
    if shuffle:
        (rng or random).shuffle(cards)
    return cards


def sort_cards(cards: list[Card] | tuple[Card, ...]) -> list[Card]:
    return sorted(cards, key=lambda card: (card.value, SUIT_ORDER[card.suit], card.code))


def cards_to_text(cards: list[Card] | tuple[Card, ...]) -> str:
    return ", ".join(card.code for card in cards)
