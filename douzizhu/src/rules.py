from __future__ import annotations

from collections import Counter

from cards import CHAIN_RANK_ORDER, CHAIN_RANKS, RANK_ORDER, Card, parse_card_input, sort_cards
from moves import Move


def identify_move(cards: list[Card] | tuple[Card, ...]) -> Move | None:
    ordered = tuple(sort_cards(cards))
    size = len(ordered)
    if size == 0 or len({card.code for card in ordered}) != size:
        return None

    counts = Counter(card.rank for card in ordered)
    count_values = sorted(counts.values(), reverse=True)

    if size == 1:
        return Move("S", ordered, ordered[0].value)

    if size == 2:
        ranks = {card.rank for card in ordered}
        if ranks == {"JokerB", "JokerR"}:
            return Move("JJ", ordered, RANK_ORDER["JokerR"])
        if count_values == [2]:
            return Move("D", ordered, ordered[0].value)
        return None

    if size == 3 and count_values == [3]:
        return Move("T", ordered, ordered[0].value)

    if size == 4:
        if count_values == [4]:
            return Move("Q", ordered, ordered[0].value)
        if count_values == [3, 1]:
            return Move("T1", ordered, _value_for_count(counts, 3))

    if size == 5:
        if count_values == [4, 1]:
            return Move("Q1", ordered, _value_for_count(counts, 4))
        if count_values == [3, 2]:
            return Move("T2", ordered, _value_for_count(counts, 3))

    if size in {5, 6, 7} and 4 in counts.values():
        return Move(f"Q{size - 4}", ordered, _value_for_count(counts, 4))

    straight = _single_straight_value(counts, size)
    if straight is not None:
        return Move("SOS", ordered, straight)

    pair_chain = _pair_chain_value(counts, size)
    if pair_chain is not None:
        return Move("SOD", ordered, pair_chain)

    triple_chain = _triple_chain_value(counts, size)
    if triple_chain is not None:
        return Move("SOT", ordered, triple_chain)

    airplane_singles = _airplane_single_value(counts, size)
    if airplane_singles is not None:
        return Move("SOT1", ordered, airplane_singles)

    airplane_pairs = _airplane_pair_value(counts, size)
    if airplane_pairs is not None:
        return Move("SOT2", ordered, airplane_pairs)

    return None


def can_beat(candidate: Move, current: Move | None) -> bool:
    if current is None:
        return True

    if candidate.kind == "JJ":
        return current.kind != "JJ"
    if current.kind == "JJ":
        return False

    if candidate.kind == "Q":
        if current.kind == "Q":
            return candidate.main_value > current.main_value
        return True
    if current.kind == "Q":
        return False

    return (
        candidate.kind == current.kind
        and candidate.size == current.size
        and candidate.main_value > current.main_value
    )


def parse_move(text: str) -> Move | None:
    return identify_move(parse_card_input(text))


def _value_for_count(counts: Counter[str], target_count: int) -> int:
    return max(RANK_ORDER[rank] for rank, count in counts.items() if count == target_count)


def _chain_values(ranks: list[str]) -> list[int] | None:
    if any(rank not in CHAIN_RANKS for rank in ranks):
        return None

    values = sorted(CHAIN_RANK_ORDER[rank] for rank in ranks)
    if any(values[index] + 1 != values[index + 1] for index in range(len(values) - 1)):
        return None

    return values


def _single_straight_value(counts: Counter[str], size: int) -> int | None:
    if size < 5 or any(count != 1 for count in counts.values()):
        return None
    values = _chain_values(list(counts))
    return max(values) if values is not None else None


def _pair_chain_value(counts: Counter[str], size: int) -> int | None:
    if size < 6 or size % 2 != 0 or any(count != 2 for count in counts.values()):
        return None
    if len(counts) < 3:
        return None
    values = _chain_values(list(counts))
    return max(values) if values is not None else None


def _triple_chain_value(counts: Counter[str], size: int) -> int | None:
    if size < 6 or size % 3 != 0 or any(count != 3 for count in counts.values()):
        return None
    if len(counts) < 2:
        return None
    values = _chain_values(list(counts))
    return max(values) if values is not None else None


def _airplane_single_value(counts: Counter[str], size: int) -> int | None:
    if size < 8 or size % 4 != 0:
        return None

    chain_length = size // 4
    triple_ranks = [rank for rank, count in counts.items() if count == 3]
    if len(triple_ranks) != chain_length:
        return None

    values = _chain_values(triple_ranks)
    return max(values) if values is not None else None


def _airplane_pair_value(counts: Counter[str], size: int) -> int | None:
    if size < 10 or size % 5 != 0:
        return None

    chain_length = size // 5
    triple_ranks = [rank for rank, count in counts.items() if count == 3]
    pair_ranks = [rank for rank, count in counts.items() if count == 2]
    if len(triple_ranks) != chain_length or len(pair_ranks) != chain_length:
        return None

    values = _chain_values(triple_ranks)
    return max(values) if values is not None else None


def _cards(text: str) -> list[Card]:
    return parse_card_input(text)


def run_self_tests() -> None:
    jh = _cards("JH")[0]
    joker_b = _cards("JokerB")[0]
    assert jh.rank == "J"
    assert joker_b.rank == "JokerB"
    assert jh.rank != joker_b.rank
    assert identify_move(_cards("JH, JokerB")) is None
    assert identify_move(_cards("JokerB, JokerR")).kind == "JJ"

    assert identify_move(_cards("3H, 4D, 5S, 6C, 7H")).kind == "SOS"
    assert identify_move(_cards("10H, JD, QS, KC, AH")).kind == "SOS"
    assert identify_move(_cards("2H, 3D, 4S, 5C, 6H")).kind == "SOS"
    assert can_beat(
        parse_move("3H, 4D, 5S, 6C, 7H"),
        parse_move("2H, 3D, 4S, 5C, 6H"),
    )
    assert identify_move(_cards("3H, 3D, 4S, 4C, 5H, 5D")).kind == "SOD"
    assert identify_move(_cards("2H, 2D, 3S, 3C, 4H, 4D")).kind == "SOD"
    assert can_beat(
        parse_move("3H, 3D, 4S, 4C, 5H, 5D"),
        parse_move("2H, 2D, 3S, 3C, 4H, 4D"),
    )
    assert identify_move(_cards("3H, 3D, 3S, 4H, 4D, 4S")).kind == "SOT"
    assert identify_move(_cards("2H, 2D, 2S, 3H, 3D, 3S")).kind == "SOT"
    assert can_beat(
        parse_move("3H, 3D, 3S, 4H, 4D, 4S"),
        parse_move("2H, 2D, 2S, 3H, 3D, 3S"),
    )
    assert identify_move(_cards("2H, 2D, 2S, 3H, 3D, 3S, 8C, 9D")).kind == "SOT1"
    assert identify_move(_cards("2H, 2D, 2S, 3H, 3D, 3S, 8C, 8D, 9C, 9D")).kind == "SOT2"

    assert identify_move(_cards("JH, QD, KS, AC, 2H")) is None
    assert identify_move(_cards("QH, KD, AS, 2C, JokerB")) is None
    assert identify_move(_cards("QH, QD, KH, KD, AH, AD, 2H, 2D")) is None
    assert identify_move(_cards("QH, QD, QS, KH, KD, KS, AH, AD, AS, 2H, 2D, 2S")) is None

    assert can_beat(parse_move("4H"), parse_move("3H"))
    assert not can_beat(parse_move("3H"), parse_move("4H"))
    assert can_beat(parse_move("7H, 7D, 7S, 7C"), parse_move("AH"))
    assert can_beat(parse_move("JokerB, JokerR"), parse_move("7H, 7D, 7S, 7C"))
    assert not can_beat(parse_move("AH, AD, AS, AC"), parse_move("JokerB, JokerR"))


if __name__ == "__main__":
    run_self_tests()
    print("rules self-tests passed")
