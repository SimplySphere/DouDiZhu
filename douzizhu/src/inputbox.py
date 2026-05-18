from __future__ import annotations

import pygame


class InputBox:
    def __init__(self, max_chars: int = 120) -> None:
        self.text = ""
        self.max_chars = max_chars

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type != pygame.KEYDOWN:
            return None

        if event.key in {pygame.K_RETURN, pygame.K_KP_ENTER}:
            submitted = self.text
            self.text = ""
            return submitted

        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return None

        if event.key == pygame.K_ESCAPE:
            self.text = ""
            return None

        if event.unicode and event.unicode.isprintable() and len(self.text) < self.max_chars:
            self.text += event.unicode

        return None
