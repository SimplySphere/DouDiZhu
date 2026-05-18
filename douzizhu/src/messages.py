from __future__ import annotations

import random


LANDLORD_VICTORY_MESSAGES = [
    "A new tax notice appears, signed by Landlord Player {player}.",
    "The estate granary is full, and Landlord Player {player} is taking credit.",
    "Landlord Player {player} just turned the final card into a land deed.",
    "By order of Landlord Player {player}, rent is due again.",
    "The valley somehow belongs to Landlord Player {player} now.",
    "Another wing rises on the manor after Player {player}'s landlord win.",
    "Player {player} has reached landlord status and already wants better curtains.",
    "The village square has been renamed for Landlord Player {player}.",
    "Landlord Player {player} celebrates with the first bowl from the harvest.",
    "The rent collector is smiling because Player {player} won as Landlord.",
    "A fresh red seal lands on the ledger from Landlord Player {player}.",
    "Player {player} has bought the hill, the road, and probably the signpost too.",
    "The manor gates open wide for Landlord Player {player}.",
    "Landlord Player {player} has made tax day suspiciously official.",
    "The harvest carts roll straight to Player {player}'s estate.",
    "No one knows how, but Landlord Player {player} owns the pond now.",
    "Player {player} just turned a card game into estate planning.",
    "A banquet begins at the manor for Landlord Player {player}.",
    "The village gets a new rulebook, written by Landlord Player {player}.",
    "Landlord Player {player} has filled the granary and raised the banners.",
]

PEASANT_VICTORY_MESSAGES = [
    "Because of Player {player}, the Peasants are eating first this season.",
    "Player {player} has turned tax day into a village holiday for the Peasants.",
    "The Peasants just opened the granary, and Player {player} gets the first cheer.",
    "After Player {player}'s final card, the Peasants are repainting the manor gate.",
    "The rent office is now a noodle shop thanks to Player {player}.",
    "Player {player} has won the round, and the Peasants are lighting lanterns early.",
    "The Peasants have declared a two-week harvest festival for Player {player}.",
    "The village bell will not stop ringing after Player {player}'s win for the Peasants.",
    "Player {player} just gave the Peasants a rent-free season and a reason to dance.",
    "The Peasants are turning the landlord's ledger into confetti for Player {player}.",
    "With Player {player}'s final play, the Peasants have upgraded tax day into feast day.",
    "The Peasants are serving the landlord's banquet to the whole village because of Player {player}.",
    "Player {player} has sent the Peasants from field work to festival work.",
    "The Peasants just renamed the village square after Player {player}'s final card.",
    "After Player {player}'s win, the harvest carts are rolling home with music.",
    "The Peasants are hanging lanterns from the tax office because Player {player} won.",
    "Player {player} has made the landlord's seal useful as a dumpling stamp.",
    "The Peasants are building a stage in the village square for Player {player}.",
    "Because Player {player} won, the rent collector is now judging the dumpling contest.",
    "The Peasants have turned the grain store into a celebration hall for Player {player}.",
    "Player {player} has given the Peasants enough rice, rest, and bragging rights.",
    "The Peasants are using the tax notice as a festival poster after Player {player}'s victory.",
    "After Player {player}'s final play, the village is louder than the manor.",
    "The Peasants have put Player {player}'s winning card on the town banner.",
    "Player {player} just made the Peasants the main guests at their own harvest feast.",
    "The Peasants are dancing through the fields after Player {player} sealed the round.",
    "Because of Player {player}, the landlord's courtyard is hosting a peasant parade.",
    "The Peasants just turned the debt ledger into a guestbook for Player {player}'s feast.",
    "Player {player} has won the round, and the Peasants are passing out sweet rice cakes.",
    "The Peasants are celebrating so loudly that even the manor windows are shaking for Player {player}.",
]


def random_victory_message(team: str, player: int, rng: random.Random | None = None) -> str:
    source = LANDLORD_VICTORY_MESSAGES if team == "Landlord" else PEASANT_VICTORY_MESSAGES
    return (rng or random).choice(source).format(player=player)
