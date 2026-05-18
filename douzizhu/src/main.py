from __future__ import annotations

import sys


def run_tests() -> None:
    from game import run_self_tests as run_game_tests
    from rules import run_self_tests as run_rule_tests

    run_rule_tests()
    run_game_tests()
    print("all self-tests passed")


def run_game() -> None:
    import pygame

    from game import GameState
    from renderer import Renderer

    pygame.init()
    pygame.font.init()

    state = GameState.new()
    renderer = Renderer(fullscreen=True)
    selected_codes: set[str] = set()
    last_turn = state.turn
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN and event.key in {pygame.K_ESCAPE, pygame.K_q}:
                running = False
                continue

            if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                continue

            if state.game_over:
                action = renderer.button_at(event.pos)
                if action == "play_again":
                    state = GameState.new()
                    selected_codes.clear()
                    last_turn = state.turn
                elif action == "quit":
                    running = False
                continue

            if state.landlord is None:
                action = renderer.button_at(event.pos)
                if action and action.startswith("bid:"):
                    state.submit_bid(action.split(":", 1)[1])
                    selected_codes.clear()
            else:
                card_code = renderer.card_at(event.pos)
                if card_code is not None:
                    if card_code in selected_codes:
                        selected_codes.remove(card_code)
                    else:
                        selected_codes.add(card_code)
                    continue

                action = renderer.button_at(event.pos)
                if action == "play":
                    if not selected_codes:
                        state.message = "Select one or more cards."
                    else:
                        play_text = ", ".join(card.code for card in state.current_hand() if card.code in selected_codes)
                        if state.submit_play(play_text):
                            selected_codes.clear()
                elif action == "pass":
                    if state.submit_play(""):
                        selected_codes.clear()

        if state.landlord is not None and state.turn != last_turn:
            selected_codes.clear()
        last_turn = state.turn

        if state.landlord is None:
            renderer.draw_bidding(state)
        else:
            renderer.draw_game(state, selected_codes)

    pygame.quit()


def main() -> None:
    if "--test" in sys.argv:
        run_tests()
        return
    run_game()


if __name__ == "__main__":
    main()
