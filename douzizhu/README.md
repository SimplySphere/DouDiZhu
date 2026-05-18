# Dou Di Zhu

Create and activate a virtual environment named `gamble` from the project root:

```bash
python3 -m venv gamble
source gamble/bin/activate
python -m pip install --upgrade pip
python -m pip install pygame
```

Run the new version from the project root:

```bash
python src/main.py
```

The game opens fullscreen. Press `Esc` or `Q` to quit.

Run the internal rule and state checks:

```bash
python src/main.py --test
```

This is a custom Dou Dizhu implementation based on the old prototype. It uses the `poker_table.png` background and card images from `images/`, with fullscreen scaling and clickable controls. It is not a perfect standard-rule clone.

## Card Names

Normal cards use rank plus suit:

```text
3H, 10D, JS, QC, KH, AS, 2C
```

Suits are `H`, `C`, `D`, and `S`. Jokers are named:

```text
JokerB, JokerR
```

Card image files are loaded from `../images/` with the exact card code, such as `../images/10H.png` or `../images/JokerR.png`.

## Rank Order

Lowest to highest:

```text
3 < 4 < 5 < 6 < 7 < 8 < 9 < 10 < J < Q < K < A < 2 < JokerB < JokerR
```

Suits do not affect strength.

## Bidding

Valid bids are:

```text
0, 5, 10, 15
```

Each player gets one bid, starting from a random player. The highest bidder becomes the landlord and receives the three bonus cards. If everyone bids `0`, the game keeps the custom prototype behavior and assigns a landlord with a default bid of `5`.

## First Player

After bidding and landlord bonus cards are assigned, the player holding `3H` goes first.

## Controls

During bidding, click one of the bid buttons:

```text
0  5  10  15
```

During play, click cards in your hand to select or unselect them. Selected cards lift upward and get a gold outline. Click `PLAY` to submit the selected cards, or click `PASS` when there is an active play on the table.

When the round ends, the screen clears and shows the winning team, the ending message, and two buttons:

```text
PLAY AGAIN
QUIT
```

## Legal Hands

- `S`: single
- `D`: pair
- `T`: triple
- `JJ`: rocket, `JokerB, JokerR`
- `Q`: bomb, four of a kind
- `T1`: triple with single
- `T2`: triple with pair
- `Q1`: four with one
- `Q2`: four with two
- `Q3`: four with three
- `SOS`: straight of singles, at least 5 cards
- `SOD`: straight of pairs, at least 3 consecutive pairs
- `SOT`: sequence of triples, at least 2 consecutive triples
- `SOT1`: airplane with single wings
- `SOT2`: airplane with pair wings

In consecutive hands, `2` is allowed but is treated as low value `2` instead of its normal high value. Jokers still cannot be used in chains.

Examples:

```text
2H, 3D, 4S, 5C, 6H is a valid straight.
3H, 4D, 5S, 6C, 7H beats 2H, 3D, 4S, 5C, 6H.
2H, 2D, 2S, 3H, 3D, 3S is a valid triple chain.
3H, 3D, 3S, 4H, 4D, 4S beats 2H, 2D, 2S, 3H, 3D, 3S.
```

## Passing

When the table is clear, the current player is leading and must play a legal hand. Clicking `PASS` on a clear table shows:

```text
You must play because the table is clear.
```

When there is an active play, a player may pass with empty input. After two consecutive passes, the trick clears and the last player who successfully played becomes the next leader.

## Winning

The round ends immediately when a player empties their hand.

If the landlord empties their hand, the winning team is `Landlord` and the game shows a landlord victory message. If either non-landlord empties their hand, the winning team is `Peasants` and the game shows a peasant victory message.
