from __future__ import annotations

import math
from pathlib import Path

import pygame

from cards import Card
from game import GameState


ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = ROOT / "images"

BASE_WIDTH = 960
BASE_HEIGHT = 648
BASE_CARD_SIZE = 96
BASE_CARD_SPACING = 36

WHITE = (255, 255, 255)
MUTED = (224, 238, 230)
DIM = (165, 188, 174)
GOLD = (255, 215, 120)
GREEN = (92, 211, 135)
BLUE = (113, 181, 255)
RED = (255, 112, 122)
BLACK = (0, 0, 0)

PANEL = (6, 13, 10, 158)
PANEL_DARK = (3, 8, 7, 205)
PANEL_LIGHT = (16, 30, 22, 128)
BORDER = (255, 255, 255, 42)


class Renderer:
    def __init__(self, fullscreen: bool = True) -> None:
        flags = pygame.FULLSCREEN if fullscreen else 0
        size = (0, 0) if fullscreen else (BASE_WIDTH, BASE_HEIGHT)
        self.screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption("Play Dou Di Zhu")

        self.width, self.height = self.screen.get_size()
        self.scale = min(self.width / BASE_WIDTH, self.height / BASE_HEIGHT)
        self.origin_x = (self.width - BASE_WIDTH * self.scale) / 2
        self.origin_y = (self.height - BASE_HEIGHT * self.scale) / 2

        self.font1 = self._font(38, bold=True)
        self.font2 = self._font(30, bold=True)
        self.font3 = self._font(23, bold=True)
        self.font4 = self._font(18, bold=True)
        self.font5 = self._font(15, bold=True)

        card_px = self._px(BASE_CARD_SIZE)
        self.card_size = (card_px, card_px)
        self.card_spacing = self._px(BASE_CARD_SPACING)
        self.card_cache: dict[str, pygame.Surface] = {}
        self.hand_card_rects: dict[str, pygame.Rect] = {}
        self.buttons: dict[str, pygame.Rect] = {}
        self.background = self._load_background()

    def draw_bidding(self, state: GameState) -> None:
        self._begin_frame()
        self._draw_status_row(state)

        self._draw_panel(self._rect(250, 82, 460, 112), PANEL)
        self._draw_centered_text("AUCTION", self.font5, 97, color=GOLD)
        self._draw_centered_text(f"Highest bid: {state.bidding.highestBid}", self.font2, 123)
        self._draw_centered_text(f"Player {state.bidding.currentPlayer + 1}", self.font4, 158, color=MUTED)

        self.draw_cards(state.bonus_cards, 216, spacing=self._px(82))
        self._draw_message_panel(state.message)
        self._draw_hand_label(f"Player {state.bidding.currentPlayer + 1}'s hand")
        self.draw_cards(state.hands[state.bidding.currentPlayer], 414)
        self._draw_bid_buttons(state)
        pygame.display.flip()

    def draw_game(self, state: GameState, selected_codes: set[str]) -> None:
        if state.game_over:
            self._begin_clear_frame()
            self._draw_end_screen(state)
            pygame.display.flip()
            return

        self._begin_frame()
        self._draw_status_row(state)
        self._draw_table_header(state)

        if state.trick.currentMove is not None:
            self.draw_cards(list(state.trick.currentMove.cards), 212)

        self._draw_message_panel(state.message)
        self._draw_turn_badge(state)
        self._draw_hand_label(f"Player {state.current_player_number()}'s hand")
        self.draw_cards(state.current_hand(), 414, selectable=True, selected_codes=selected_codes)
        self._draw_action_buttons(state, selected_count=len(selected_codes))
        pygame.display.flip()

    def card_at(self, pos: tuple[int, int]) -> str | None:
        for code, rect in reversed(list(self.hand_card_rects.items())):
            if rect.collidepoint(pos):
                return code
        return None

    def button_at(self, pos: tuple[int, int]) -> str | None:
        for action, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return action
        return None

    def draw_cards(
        self,
        cards: list[Card],
        base_y: int,
        spacing: int | None = None,
        selectable: bool = False,
        selected_codes: set[str] | None = None,
    ) -> None:
        if not cards:
            return

        selected_codes = selected_codes or set()
        spacing = spacing if spacing is not None else self.card_spacing
        total_width = self.card_size[0] + spacing * (len(cards) - 1)
        max_width = int(self.width * 0.88)
        if len(cards) > 1 and total_width > max_width:
            spacing = max(self._px(18), int((max_width - self.card_size[0]) / (len(cards) - 1)))
            total_width = self.card_size[0] + spacing * (len(cards) - 1)

        x = (self.width - total_width) // 2
        y = self._y(base_y)
        lift = self._px(18)

        shadow = pygame.Surface(self.card_size, pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 96), shadow.get_rect(), border_radius=self._px(4))

        for index, card in enumerate(cards):
            card_x = int(x + index * spacing)
            is_selected = card.code in selected_codes
            card_y = y - lift if is_selected else y

            if selectable:
                hit_rect = pygame.Rect(card_x, y - lift, self.card_size[0], self.card_size[1] + lift)
                self.hand_card_rects[card.code] = hit_rect

            self.screen.blit(shadow, (card_x + self._px(3), card_y + self._px(5)))
            if is_selected:
                glow_rect = pygame.Rect(
                    card_x - self._px(5),
                    card_y - self._px(5),
                    self.card_size[0] + self._px(10),
                    self.card_size[1] + self._px(10),
                )
                pygame.draw.rect(self.screen, GOLD, glow_rect, width=self._px(3), border_radius=self._px(6))
            self.screen.blit(self.card_image(card), (card_x, card_y))

    def card_image(self, card: Card) -> pygame.Surface:
        if card.code not in self.card_cache:
            path = IMAGE_DIR / f"{card.code}.png"
            image = pygame.image.load(str(path)).convert_alpha()
            self.card_cache[card.code] = pygame.transform.smoothscale(image, self.card_size)
        return self.card_cache[card.code]

    def _begin_frame(self) -> None:
        self.hand_card_rects.clear()
        self.buttons.clear()
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (0, 0))

    def _begin_clear_frame(self) -> None:
        self.hand_card_rects.clear()
        self.buttons.clear()
        self.screen.fill(BLACK)

    def _draw_status_row(self, state: GameState) -> None:
        badge_width = 210
        gap = 18
        total = badge_width * 3 + gap * 2
        start_x = (BASE_WIDTH - total) / 2
        for index, hand in enumerate(state.hands):
            rect = self._rect(start_x + index * (badge_width + gap), 18, badge_width, 48)
            active = state.landlord is not None and index == state.turn and not state.game_over
            role = state.player_role(index) if state.landlord is not None else "Bidding"
            accent = GOLD if role == "Landlord" else BLUE
            if active:
                accent = GREEN

            self._draw_panel(rect, PANEL_LIGHT if active else PANEL, border=(255, 255, 255, 50), radius=8)
            pygame.draw.rect(self.screen, accent, pygame.Rect(rect.x, rect.y, self._px(5), rect.height), border_radius=self._px(4))
            self._draw_text(f"Player {index + 1}", self.font4, rect.x + self._px(18), rect.y + self._px(7))
            self._draw_text(f"{role}  {len(hand)} cards", self.font5, rect.x + self._px(18), rect.y + self._px(28), color=MUTED)

    def _draw_table_header(self, state: GameState) -> None:
        rect = self._rect(258, 82, 444, 112)
        self._draw_panel(rect, PANEL)

        landlord_text = "LANDLORD  not assigned"
        if state.landlord is not None:
            landlord_text = f"LANDLORD  Player {state.landlord + 1}    BID {state.highest_bid}"
        self._draw_centered_text(landlord_text, self.font5, 98, color=GOLD)

        table_title = "TABLE CLEAR"
        table_subtitle = "Lead any legal hand"
        if state.trick.currentMove is not None:
            table_title = state.trick.currentMove.name.upper()
            holder = state.trick.lastPlayer + 1 if state.trick.lastPlayer is not None else state.current_player_number()
            table_subtitle = f"Player {holder} holds the table"

        self._draw_centered_text(table_title, self.font2, 124)
        self._draw_centered_text(table_subtitle, self.font5, 160, color=MUTED)

    def _draw_message_panel(self, message: str) -> None:
        rect = self._rect(228, 318, 504, 64)
        self._draw_panel(rect, PANEL, border=(255, 255, 255, 34), radius=8)
        lines = self._wrap_text(message, self.font4, rect.width - self._px(34))
        start_y = rect.y + self._px(10) if len(lines) > 1 else rect.y + self._px(20)
        for offset, line in enumerate(lines[:2]):
            self._draw_centered_text(line, self.font4, self._base_y(start_y) + offset * 22, color=MUTED)

    def _draw_turn_badge(self, state: GameState) -> None:
        rect = self._rect(380, 386, 200, 34)
        self._draw_panel(rect, (8, 18, 13, 184), border=(92, 211, 135, 108), radius=17)
        self._draw_centered_text(f"Player {state.current_player_number()}'s turn", self.font4, 393, color=GREEN)

    def _draw_hand_label(self, text: str) -> None:
        self._draw_centered_text(text, self.font5, 532, color=DIM)

    def _draw_end_screen(self, state: GameState) -> None:
        title = "Landlord Wins!" if state.winning_team == "Landlord" else "Peasants Win!"
        accent = GOLD if state.winning_team == "Landlord" else GREEN
        self._draw_centered_text(title, self.font1, 188, color=accent)
        self._draw_wrapped_centered_text(state.victory_message, self.font3, 278, self._px(700), line_height=32)

        play_again_rect = self._rect(295, 426, 170, 54)
        quit_rect = self._rect(495, 426, 170, 54)
        self._draw_button(
            "play_again",
            play_again_rect,
            "PLAY AGAIN",
            fill=(16, 31, 23, 225),
            border=(*GREEN, 140),
        )
        self._draw_button(
            "quit",
            quit_rect,
            "QUIT",
            fill=PANEL_DARK,
            border=(*RED, 120),
        )

    def _draw_bid_buttons(self, state: GameState) -> None:
        values = [0, 5, 10, 15]
        button_width = 104
        gap = 16
        total = button_width * len(values) + gap * (len(values) - 1)
        start_x = (BASE_WIDTH - total) / 2
        for index, bid in enumerate(values):
            rect = self._rect(start_x + index * (button_width + gap), 562, button_width, 50)
            highlighted = bid > state.bidding.highestBid
            fill = (16, 31, 23, 214) if highlighted else PANEL_DARK
            border = (*GOLD, 125) if highlighted else BORDER
            self._draw_button(f"bid:{bid}", rect, str(bid), fill=fill, border=border)

    def _draw_action_buttons(self, state: GameState, selected_count: int) -> None:
        play_rect = self._rect(315, 562, 150, 50)
        pass_rect = self._rect(495, 562, 150, 50)
        play_label = f"PLAY {selected_count}" if selected_count else "PLAY"
        pass_disabled = state.trick.currentMove is None

        self._draw_button(
            "play",
            play_rect,
            play_label,
            fill=(16, 31, 23, 220) if selected_count else PANEL_DARK,
            border=(*GREEN, 130) if selected_count else BORDER,
        )
        self._draw_button(
            "pass",
            pass_rect,
            "PASS",
            fill=PANEL_DARK if not pass_disabled else (4, 8, 7, 145),
            border=(*RED, 105) if not pass_disabled else (255, 255, 255, 28),
            color=WHITE if not pass_disabled else DIM,
        )

    def _draw_button(
        self,
        action: str,
        rect: pygame.Rect,
        label: str,
        fill: tuple[int, int, int, int],
        border: tuple[int, int, int, int],
        color: tuple[int, int, int] = WHITE,
    ) -> None:
        self.buttons[action] = rect
        self._draw_panel(rect, fill, border=border, radius=10)
        surface = self.font3.render(label, True, color)
        x = rect.x + (rect.width - surface.get_width()) // 2
        y = rect.y + (rect.height - surface.get_height()) // 2 - self._px(1)
        self._draw_text(label, self.font3, x, y, color=color)

    def _draw_centered_text(
        self,
        text: str,
        font: pygame.font.Font,
        base_y: float,
        color: tuple[int, int, int] = WHITE,
    ) -> None:
        surface = font.render(text, True, color)
        x = (self.width - surface.get_width()) // 2
        self._draw_text(text, font, x, self._y(base_y), color=color)

    def _draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        x: int,
        y: int,
        color: tuple[int, int, int] = WHITE,
    ) -> None:
        shadow = font.render(text, True, (0, 0, 0))
        shadow.set_alpha(150)
        self.screen.blit(shadow, (x + self._px(2), y + self._px(2)))
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def _draw_panel(
        self,
        rect: pygame.Rect,
        fill: tuple[int, int, int, int],
        border: tuple[int, int, int, int] = BORDER,
        radius: int = 8,
    ) -> None:
        radius_px = self._px(radius)
        shadow = pygame.Surface((rect.width + self._px(8), rect.height + self._px(8)), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 92), shadow.get_rect(), border_radius=radius_px + self._px(3))
        self.screen.blit(shadow, (rect.x + self._px(3), rect.y + self._px(4)))

        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, fill, panel.get_rect(), border_radius=radius_px)
        pygame.draw.rect(panel, border, panel.get_rect(), width=max(1, self._px(1)), border_radius=radius_px)
        self.screen.blit(panel, rect.topleft)

    def _draw_wrapped_centered_text(
        self,
        text: str,
        font: pygame.font.Font,
        base_y: int,
        max_width: int,
        line_height: int,
    ) -> None:
        for offset, line in enumerate(self._wrap_text(text, font, max_width)):
            self._draw_centered_text(line, font, base_y + offset * line_height)

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split()
        if not words:
            return [""]

        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def _font(self, base_size: int, bold: bool = False) -> pygame.font.Font:
        size = max(12, self._px(base_size))
        return pygame.font.SysFont(["Avenir Next", "Helvetica Neue", "Arial", "San Francisco"], size, bold=bold)

    def _load_background(self) -> pygame.Surface:
        raw = pygame.image.load(str(IMAGE_DIR / "poker_table.png")).convert()
        scale = max(self.width / raw.get_width(), self.height / raw.get_height())
        scaled_size = (math.ceil(raw.get_width() * scale), math.ceil(raw.get_height() * scale))
        scaled = pygame.transform.smoothscale(raw, scaled_size)
        background = pygame.Surface((self.width, self.height)).convert()
        background.blit(scaled, ((self.width - scaled_size[0]) // 2, (self.height - scaled_size[1]) // 2))
        return background

    def _rect(self, x: float, y: float, width: float, height: float) -> pygame.Rect:
        return pygame.Rect(self._x(x), self._y(y), self._px(width), self._px(height))

    def _x(self, x: float) -> int:
        return round(self.origin_x + x * self.scale)

    def _y(self, y: float) -> int:
        return round(self.origin_y + y * self.scale)

    def _base_y(self, screen_y: int) -> float:
        return (screen_y - self.origin_y) / self.scale

    def _px(self, value: float) -> int:
        return max(1, round(value * self.scale))
