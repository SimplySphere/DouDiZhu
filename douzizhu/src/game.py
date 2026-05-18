from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field

from cards import Card, build_deck, cards_to_text, parse_card_input, sort_cards
from messages import random_victory_message
from moves import Move
from rules import can_beat, identify_move, parse_move


VALID_BIDS = {0, 5, 10, 15}


@dataclass
class TrickState:
    currentMove: Move | None = None
    lastPlayer: int | None = None
    passCount: int = 0


@dataclass
class BiddingState:
    currentPlayer: int
    startPlayer: int
    highestBid: int = 0
    highestPlayer: int | None = None
    bidsTaken: int = 0
    done: bool = False

    def __post_init__(self) -> None:
        if self.highestPlayer is None:
            self.highestPlayer = self.startPlayer


@dataclass
class GameState:
    hands: list[list[Card]]
    bonus_cards: list[Card]
    bidding: BiddingState
    landlord: int | None = None
    highest_bid: int = 0
    turn: int = 0
    trick: TrickState = field(default_factory=TrickState)
    message: str = ""
    game_over: bool = False
    winning_team: str | None = None
    victory_message: str = ""
    rng: random.Random | None = field(default=None, repr=False)

    @classmethod
    def new(cls, seed: int | None = None) -> GameState:
        rng = random.Random(seed)
        deck = build_deck(shuffle=True, rng=rng)
        bonus_cards = sort_cards([deck.pop(0) for _ in range(3)])
        hands = [sort_cards([deck.pop(0) for _ in range(17)]) for _ in range(3)]
        start_player = rng.randint(0, 2)
        bidding = BiddingState(currentPlayer=start_player, startPlayer=start_player)
        return cls(
            hands=hands,
            bonus_cards=bonus_cards,
            bidding=bidding,
            turn=start_player,
            message=f"Player {start_player + 1} bids first!",
            rng=rng,
        )

    def submit_bid(self, text: str) -> bool:
        if self.landlord is not None:
            self.message = "Bidding is already finished."
            return False

        bid_text = text.strip()
        try:
            bid = int(bid_text)
        except ValueError:
            self.message = "Bid must be 0, 5, 10, or 15."
            return False

        if bid not in VALID_BIDS:
            self.message = "Bid must be 0, 5, 10, or 15."
            return False

        current_player = self.bidding.currentPlayer
        if bid > self.bidding.highestBid:
            self.bidding.highestBid = bid
            self.bidding.highestPlayer = current_player
            self.message = f"Player {current_player + 1} bids {bid}."
        else:
            self.message = f"Player {current_player + 1} bids {bid}."

        self.bidding.bidsTaken += 1
        if bid == 15 or self.bidding.bidsTaken >= 3:
            self.bidding.done = True
            self.finish_bidding()
            return True

        self.bidding.currentPlayer = (current_player + 1) % 3
        return True

    def finish_bidding(self) -> None:
        if self.landlord is not None:
            return

        if self.bidding.highestBid == 0:
            self.bidding.highestBid = 5
            self.bidding.highestPlayer = self.bidding.startPlayer

        landlord = self.bidding.highestPlayer
        if landlord is None:
            landlord = self.bidding.startPlayer

        self.landlord = landlord
        self.highest_bid = self.bidding.highestBid
        self.hands[landlord].extend(self.bonus_cards)
        self.hands[landlord] = sort_cards(self.hands[landlord])
        self.turn = self.find_card_holder("3H")
        self.trick = TrickState()
        self.message = (
            f"Landlord: Player {landlord + 1} with bid {self.highest_bid}. "
            f"Player {self.turn + 1} goes first!"
        )

    def find_card_holder(self, code: str) -> int:
        for player, hand in enumerate(self.hands):
            if any(card.code == code for card in hand):
                return player
        return 0

    def submit_play(self, text: str) -> bool:
        if self.landlord is None:
            self.message = "Finish bidding first."
            return False

        if self.game_over:
            return False

        if text.strip() == "":
            return self.pass_turn()

        player = self.turn
        try:
            cards = parse_card_input(text)
        except ValueError as exc:
            self.message = str(exc)
            return False

        move = identify_move(cards)
        if move is None:
            self.message = "That is not a legal hand."
            return False

        if not self.player_has_cards(player, cards):
            self.message = f"Player {player + 1} does not have those cards."
            return False

        if not can_beat(move, self.trick.currentMove):
            current_name = self.trick.currentMove.name if self.trick.currentMove else "clear table"
            self.message = f"{move.name} does not beat the current {current_name}."
            return False

        self.remove_cards(player, cards)
        self.trick.currentMove = move
        self.trick.lastPlayer = player
        self.trick.passCount = 0

        if not self.hands[player]:
            self.end_round(player)
            return True

        self.turn = (player + 1) % 3
        self.message = f"Player {player + 1} played {move.name}: {move.text()}"
        return True

    def pass_turn(self) -> bool:
        if self.trick.currentMove is None:
            self.message = "You must play because the table is clear."
            return False

        player = self.turn
        self.trick.passCount += 1
        if self.trick.passCount == 2:
            leader = self.trick.lastPlayer if self.trick.lastPlayer is not None else player
            self.trick.currentMove = None
            self.trick.passCount = 0
            self.turn = leader
            self.message = f"Player {player + 1} passes. Trick cleared. Player {leader + 1} leads."
            return True

        self.turn = (player + 1) % 3
        self.message = f"Player {player + 1} passes."
        return True

    def player_has_cards(self, player: int, cards: list[Card]) -> bool:
        hand_counts = Counter(card.code for card in self.hands[player])
        play_counts = Counter(card.code for card in cards)
        return all(hand_counts[code] >= count for code, count in play_counts.items())

    def remove_cards(self, player: int, cards: list[Card]) -> None:
        remaining_to_remove = Counter(card.code for card in cards)
        new_hand: list[Card] = []
        for card in self.hands[player]:
            if remaining_to_remove[card.code] > 0:
                remaining_to_remove[card.code] -= 1
            else:
                new_hand.append(card)
        self.hands[player] = new_hand

    def end_round(self, player: int) -> None:
        team = "Landlord" if player == self.landlord else "Peasants"
        self.game_over = True
        self.winning_team = team
        self.victory_message = random_victory_message(team, player + 1, self.rng)
        self.message = f"{team} Victory! {self.victory_message}"

    def current_hand(self) -> list[Card]:
        return self.hands[self.turn]

    def current_player_number(self) -> int:
        return self.turn + 1

    def table_text(self) -> str:
        if self.trick.currentMove is None:
            return ""
        return cards_to_text(self.trick.currentMove.cards)

    def player_role(self, player: int) -> str:
        return "Landlord" if player == self.landlord else "Peasant"


def _state(hands: list[str], landlord: int, turn: int) -> GameState:
    return GameState(
        hands=[sort_cards(parse_card_input(hand)) for hand in hands],
        bonus_cards=[],
        bidding=BiddingState(currentPlayer=0, startPlayer=0, done=True),
        landlord=landlord,
        highest_bid=5,
        turn=turn,
        rng=random.Random(0),
    )


def run_self_tests() -> None:
    state = _state(["3H", "4H", "5H"], landlord=0, turn=0)
    assert not state.submit_play("")
    assert state.message == "You must play because the table is clear."

    current = parse_move("3H")
    assert current is not None
    state.trick.currentMove = current
    state.trick.lastPlayer = 0
    state.turn = 1
    assert state.submit_play("")
    assert state.trick.currentMove is current
    assert state.trick.passCount == 1
    assert state.turn == 2
    assert state.submit_play("")
    assert state.trick.currentMove is None
    assert state.trick.passCount == 0
    assert state.turn == 0

    landlord_state = _state(["3H", "4H", "5H"], landlord=0, turn=0)
    assert landlord_state.submit_play("3H")
    assert landlord_state.game_over
    assert landlord_state.winning_team == "Landlord"
    assert landlord_state.message.startswith("Landlord Victory!")

    peasant_state = _state(["3H", "4H", "5H"], landlord=0, turn=1)
    assert peasant_state.submit_play("4H")
    assert peasant_state.game_over
    assert peasant_state.winning_team == "Peasants"
    assert peasant_state.message.startswith("Peasants Victory!")


if __name__ == "__main__":
    run_self_tests()
    print("game self-tests passed")
