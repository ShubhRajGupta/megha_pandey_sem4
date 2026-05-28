"""
Tetris Game — Python OOP + Pygame
==================================
A fully-featured Tetris clone built with Object-Oriented Programming
principles. The game features classic Tetris gameplay with falling blocks,
line clearing, scoring, increasing difficulty, and a next-block preview.

Classes
-------
Block   – Represents a single falling tetromino (shape, color, rotation).
Tetris  – Manages the game board, scoring, collision, and line clearing.
Main    – Game loop, rendering, and event handling (controller).

Controls
--------
←  →        Move left / right
↑           Rotate
↓           Soft drop (move down faster)
SPACE       Hard drop (instant)
ESC         Restart after game over
P           Pause / unpause
"""

import pygame
import random
import sys
import math

# ─────────────────────────── CONSTANTS ───────────────────────────

# Window
WIN_WIDTH = 700
WIN_HEIGHT = 600

# Board (play-field)
BOARD_COLS = 10
BOARD_ROWS = 20
CELL_SIZE = 25

# Derived board pixel dimensions
BOARD_PX_W = BOARD_COLS * CELL_SIZE      # 250
BOARD_PX_H = BOARD_ROWS * CELL_SIZE      # 500

# Top-left corner of the board on the window
BOARD_X = 50
BOARD_Y = 50

# Preview / sidebar positions
SIDEBAR_X = BOARD_X + BOARD_PX_W + 40
SIDEBAR_Y = BOARD_Y

# Colors – rich palette
BLACK       = (15, 15, 26)
WHITE       = (235, 235, 245)
GRID_LINE   = (40, 42, 54)
BG_COLOR    = (22, 22, 38)
PANEL_BG    = (30, 30, 50)
ACCENT      = (130, 100, 255)

# Block colors (index 1–7 to match shape types)
BLOCK_COLORS = [
    (0, 0, 0),           # 0 – unused
    (0, 240, 240),       # 1 – Cyan   (I)
    (0, 100, 240),       # 2 – Blue   (J)
    (240, 160, 0),       # 3 – Orange (L)
    (240, 240, 0),       # 4 – Yellow (O)
    (0, 240, 0),         # 5 – Green  (S)
    (160, 0, 240),       # 6 – Purple (T)
    (240, 0, 0),         # 7 – Red    (Z)
]

# Brighter highlight versions for the block face
BLOCK_HIGHLIGHTS = [
    (0, 0, 0),
    (100, 255, 255),
    (100, 170, 255),
    (255, 200, 80),
    (255, 255, 100),
    (100, 255, 100),
    (210, 100, 255),
    (255, 100, 100),
]

# Shadow / darker versions for the block edge
BLOCK_SHADOWS = [
    (0, 0, 0),
    (0, 160, 160),
    (0, 60, 160),
    (160, 100, 0),
    (160, 160, 0),
    (0, 160, 0),
    (100, 0, 160),
    (160, 0, 0),
]

# ─── Shape definitions (4×4 grid, each rotation is a list of occupied cells) ───
# Each shape has a list of rotations; each rotation is a list of (row, col) in a 4×4 box.

SHAPES = [
    # 0 – I
    [
        [(1, 0), (1, 1), (1, 2), (1, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 1), (1, 1), (2, 1), (3, 1)],
    ],
    # 1 – J
    [
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 0), (2, 1)],
    ],
    # 2 – L
    [
        [(0, 2), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (1, 2), (2, 0)],
        [(0, 0), (0, 1), (1, 1), (2, 1)],
    ],
    # 3 – O
    [
        [(0, 1), (0, 2), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (1, 2)],
    ],
    # 4 – S
    [
        [(0, 1), (0, 2), (1, 0), (1, 1)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 1), (1, 2), (2, 0), (2, 1)],
        [(0, 0), (1, 0), (1, 1), (2, 1)],
    ],
    # 5 – T
    [
        [(0, 1), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 1)],
        [(0, 1), (1, 0), (1, 1), (2, 1)],
    ],
    # 6 – Z
    [
        [(0, 0), (0, 1), (1, 1), (1, 2)],
        [(0, 2), (1, 1), (1, 2), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(0, 1), (1, 0), (1, 1), (2, 0)],
    ],
]


# ══════════════════════════════════════════════════════════════════
#  BLOCK CLASS
# ══════════════════════════════════════════════════════════════════

class Block:
    """Represents a single falling tetromino piece.

    Attributes
    ----------
    x : int
        Horizontal grid position (column) of the block's top-left corner.
    y : int
        Vertical grid position (row) of the block's top-left corner.
    type : int
        Index into SHAPES (0–6) identifying this block's shape.
    color : int
        Index into BLOCK_COLORS (1–7).
    rotation : int
        Current rotation state (0–3).
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(SHAPES) - 1)
        self.color = self.type + 1  # colors are 1-indexed
        self.rotation = 0

    def image(self):
        """Return the list of (row, col) cells occupied in the current rotation."""
        return SHAPES[self.type][self.rotation]

    def rotate(self):
        """Advance to the next rotation state, wrapping around."""
        self.rotation = (self.rotation + 1) % len(SHAPES[self.type])


# ══════════════════════════════════════════════════════════════════
#  TETRIS CLASS
# ══════════════════════════════════════════════════════════════════

class Tetris:
    """Manages the game board, score, level, and all gameplay logic.

    Attributes
    ----------
    height : int   – Number of rows on the board.
    width : int    – Number of columns on the board.
    field : list   – 2-D list representing the board; 0 = empty, >0 = color.
    score : int    – Player's current score.
    level : int    – Current difficulty level (controls drop speed).
    state : str    – 'start' or 'gameover'.
    block : Block  – The currently falling block.
    next_block_obj : Block – Preview of the next block.
    lines_cleared : int – Total lines cleared (used for levelling up).
    """

    def __init__(self, height: int = BOARD_ROWS, width: int = BOARD_COLS):
        self.height = height
        self.width = width
        self.field = [[0] * width for _ in range(height)]
        self.score = 0
        self.level = 1
        self.state = "start"
        self.lines_cleared = 0
        self.block = None
        self.next_block_obj = None
        self.new_block()

    # ── Block generation ──────────────────────────────────────────

    def new_block(self):
        """Set the current block to the queued next block and generate a new next block."""
        if self.next_block_obj is None:
            # Very first block: create both
            self.block = Block(self.width // 2 - 2, 0)
            self.next_block_obj = Block(self.width // 2 - 2, 0)
        else:
            self.block = self.next_block_obj
            self.block.x = self.width // 2 - 2
            self.block.y = 0
            self.next_block_obj = Block(self.width // 2 - 2, 0)

        # If the new block immediately intersects, game over
        if self.intersects():
            self.state = "gameover"

    # ── Collision detection ───────────────────────────────────────

    def intersects(self):
        """Return True if the current block overlaps filled cells or is out of bounds."""
        for row, col in self.block.image():
            bx = self.block.x + col
            by = self.block.y + row
            if bx < 0 or bx >= self.width or by >= self.height:
                return True
            if by >= 0 and self.field[by][bx] != 0:
                return True
        return False

    # ── Line clearing ─────────────────────────────────────────────

    def break_lines(self):
        """Remove completed rows, shift everything above down, and update score."""
        cleared = 0
        row = self.height - 1
        while row >= 0:
            if all(self.field[row][c] != 0 for c in range(self.width)):
                del self.field[row]
                self.field.insert(0, [0] * self.width)
                cleared += 1
                # Don't decrement row — re-check same index after shift
            else:
                row -= 1

        if cleared > 0:
            self.score += cleared * cleared  # 1→1, 2→4, 3→9, 4→16
            self.lines_cleared += cleared
            # Level up every 10 lines
            self.level = 1 + self.lines_cleared // 10

    # ── Movement / rotation ───────────────────────────────────────

    def freeze(self):
        """Lock the current block into the field and handle line clears / game over."""
        for row, col in self.block.image():
            bx = self.block.x + col
            by = self.block.y + row
            if 0 <= by < self.height and 0 <= bx < self.width:
                self.field[by][bx] = self.block.color
        self.break_lines()
        self.new_block()

    def move_down(self):
        """Move block down by one row; freeze if it can't move further."""
        self.block.y += 1
        if self.intersects():
            self.block.y -= 1
            self.freeze()

    def move_horiz(self, dx: int):
        """Move block horizontally by *dx* columns (-1 = left, +1 = right)."""
        self.block.x += dx
        if self.intersects():
            self.block.x -= dx

    def rotate(self):
        """Rotate block; undo if the rotation causes a collision."""
        old_rotation = self.block.rotation
        self.block.rotate()
        if self.intersects():
            self.block.rotation = old_rotation

    def move_bottom(self):
        """Hard-drop: move the block to the lowest valid position instantly."""
        while not self.intersects():
            self.block.y += 1
        self.block.y -= 1
        self.freeze()

    def ghost_y(self):
        """Return the y-position where the block would land (for ghost preview)."""
        orig_y = self.block.y
        while not self.intersects():
            self.block.y += 1
        landing = self.block.y - 1
        self.block.y = orig_y
        return landing


# ══════════════════════════════════════════════════════════════════
#  GAME CONTROLLER (Main Loop)
# ══════════════════════════════════════════════════════════════════

def draw_cell(surface, x, y, color_index, size=CELL_SIZE, alpha=255):
    """Draw a single cell with a beveled 3-D look."""
    base = BLOCK_COLORS[color_index]
    highlight = BLOCK_HIGHLIGHTS[color_index]
    shadow = BLOCK_SHADOWS[color_index]

    # Base fill
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, base, rect)

    # Highlight (top + left edges)
    pygame.draw.line(surface, highlight, (x, y), (x + size - 1, y), 2)
    pygame.draw.line(surface, highlight, (x, y), (x, y + size - 1), 2)

    # Shadow (bottom + right edges)
    pygame.draw.line(surface, shadow, (x + size - 1, y), (x + size - 1, y + size - 1), 2)
    pygame.draw.line(surface, shadow, (x, y + size - 1), (x + size - 1, y + size - 1), 2)

    # Inner shine
    inner = pygame.Rect(x + 4, y + 4, size - 8, size - 8)
    shine = tuple(min(255, c + 30) for c in base)
    pygame.draw.rect(surface, shine, inner)


def draw_text_shadow(surface, text, font, color, x, y, shadow_color=(0, 0, 0)):
    """Render text with a subtle drop-shadow."""
    shadow_surf = font.render(text, True, shadow_color)
    surface.blit(shadow_surf, (x + 2, y + 2))
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, (x, y))


def main():
    """Run the Tetris game."""
    pygame.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Tetris — Python OOP + Pygame")
    clock = pygame.time.Clock()

    # Fonts
    font_large = pygame.font.SysFont("Segoe UI", 42, bold=True)
    font_medium = pygame.font.SysFont("Segoe UI", 24)
    font_small = pygame.font.SysFont("Segoe UI", 18)
    font_title = pygame.font.SysFont("Segoe UI", 56, bold=True)

    # ── Initialise game ──
    game = Tetris()
    paused = False

    # Gravity timer
    fall_event = pygame.USEREVENT + 1
    base_interval = 500  # ms at level 1
    pygame.time.set_timer(fall_event, base_interval)

    # Key repeat for smooth sideways movement
    pygame.key.set_repeat(170, 50)

    # Particle effects list for line clears
    particles = []

    running = True
    while running:
        # ── Events ────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == fall_event:
                if game.state == "start" and not paused:
                    game.move_down()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.state == "gameover":
                        game = Tetris()
                        paused = False
                        particles.clear()
                    else:
                        running = False

                if event.key == pygame.K_p:
                    paused = not paused

                if game.state == "start" and not paused:
                    if event.key == pygame.K_LEFT:
                        game.move_horiz(-1)
                    elif event.key == pygame.K_RIGHT:
                        game.move_horiz(1)
                    elif event.key == pygame.K_DOWN:
                        game.move_down()
                    elif event.key == pygame.K_UP:
                        game.rotate()
                    elif event.key == pygame.K_SPACE:
                        game.move_bottom()

        # Update timer speed according to level
        interval = max(100, base_interval - (game.level - 1) * 40)
        pygame.time.set_timer(fall_event, interval)

        # ── Update particles ──────────────────────────────────────
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.15  # gravity
            p["life"] -= 1
            if p["life"] <= 0:
                particles.remove(p)

        # ── Drawing ───────────────────────────────────────────────
        screen.fill(BG_COLOR)

        # ── Board background + grid ──
        board_rect = pygame.Rect(BOARD_X - 2, BOARD_Y - 2, BOARD_PX_W + 4, BOARD_PX_H + 4)
        pygame.draw.rect(screen, PANEL_BG, board_rect, border_radius=4)
        pygame.draw.rect(screen, ACCENT, board_rect, 2, border_radius=4)

        # Grid lines
        for r in range(BOARD_ROWS + 1):
            y = BOARD_Y + r * CELL_SIZE
            pygame.draw.line(screen, GRID_LINE, (BOARD_X, y), (BOARD_X + BOARD_PX_W, y))
        for c in range(BOARD_COLS + 1):
            x = BOARD_X + c * CELL_SIZE
            pygame.draw.line(screen, GRID_LINE, (x, BOARD_Y), (x, BOARD_Y + BOARD_PX_H))

        # ── Placed blocks on the field ──
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                val = game.field[r][c]
                if val:
                    px = BOARD_X + c * CELL_SIZE
                    py = BOARD_Y + r * CELL_SIZE
                    draw_cell(screen, px, py, val)

        # ── Ghost piece (translucent preview of where the block will land) ──
        if game.state == "start" and game.block:
            ghost_y = game.ghost_y()
            for row, col in game.block.image():
                bx = game.block.x + col
                by = ghost_y + row
                if 0 <= by < BOARD_ROWS and 0 <= bx < BOARD_COLS:
                    px = BOARD_X + bx * CELL_SIZE
                    py = BOARD_Y + by * CELL_SIZE
                    ghost_rect = pygame.Rect(px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2)
                    color = BLOCK_COLORS[game.block.color]
                    ghost_surf = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2), pygame.SRCALPHA)
                    ghost_surf.fill((*color, 50))
                    screen.blit(ghost_surf, (px + 1, py + 1))
                    pygame.draw.rect(screen, (*color, 100), ghost_rect, 1)

        # ── Current falling block ──
        if game.state == "start" and game.block:
            for row, col in game.block.image():
                bx = game.block.x + col
                by = game.block.y + row
                if by >= 0:
                    px = BOARD_X + bx * CELL_SIZE
                    py = BOARD_Y + by * CELL_SIZE
                    draw_cell(screen, px, py, game.block.color)

        # ── Particles ──
        for p in particles:
            alpha = max(0, min(255, int(255 * p["life"] / p["max_life"])))
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            s.fill((*p["color"], alpha))
            screen.blit(s, (int(p["x"]), int(p["y"])))

        # ── Sidebar ──
        sidebar_panel = pygame.Rect(SIDEBAR_X - 10, SIDEBAR_Y - 10, 310, BOARD_PX_H + 20)
        pygame.draw.rect(screen, PANEL_BG, sidebar_panel, border_radius=8)
        pygame.draw.rect(screen, ACCENT, sidebar_panel, 2, border_radius=8)

        # Title
        draw_text_shadow(screen, "TETRIS", font_title, ACCENT, SIDEBAR_X + 10, SIDEBAR_Y)

        # Score
        draw_text_shadow(screen, "SCORE", font_medium, WHITE, SIDEBAR_X + 10, SIDEBAR_Y + 80)
        draw_text_shadow(screen, str(game.score), font_large, (255, 220, 100), SIDEBAR_X + 10, SIDEBAR_Y + 108)

        # Level
        draw_text_shadow(screen, "LEVEL", font_medium, WHITE, SIDEBAR_X + 10, SIDEBAR_Y + 170)
        draw_text_shadow(screen, str(game.level), font_large, (100, 220, 255), SIDEBAR_X + 10, SIDEBAR_Y + 198)

        # Lines
        draw_text_shadow(screen, "LINES", font_medium, WHITE, SIDEBAR_X + 10, SIDEBAR_Y + 260)
        draw_text_shadow(screen, str(game.lines_cleared), font_large, (100, 255, 180), SIDEBAR_X + 10, SIDEBAR_Y + 288)

        # Next block preview
        draw_text_shadow(screen, "NEXT", font_medium, WHITE, SIDEBAR_X + 10, SIDEBAR_Y + 360)
        preview_box = pygame.Rect(SIDEBAR_X + 10, SIDEBAR_Y + 392, 120, 100)
        pygame.draw.rect(screen, (20, 20, 36), preview_box, border_radius=6)
        pygame.draw.rect(screen, GRID_LINE, preview_box, 1, border_radius=6)

        if game.next_block_obj:
            preview_cell = 20
            for row, col in game.next_block_obj.image():
                px = SIDEBAR_X + 20 + col * preview_cell
                py = SIDEBAR_Y + 402 + row * preview_cell
                draw_cell(screen, px, py, game.next_block_obj.color, size=preview_cell)

        # Controls help
        controls_y = SIDEBAR_Y + 510
        controls = [
            "← →  Move",
            "↑    Rotate",
            "↓    Soft Drop",
            "SPC  Hard Drop",
            "P    Pause",
            "ESC  Quit / Restart",
        ]
        for i, line in enumerate(controls):
            draw_text_shadow(screen, line, font_small, (150, 150, 180), SIDEBAR_X + 10, controls_y + i * 22)

        # ── Pause overlay ──
        if paused and game.state == "start":
            overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            draw_text_shadow(screen, "PAUSED", font_title, WHITE, WIN_WIDTH // 2 - 110, WIN_HEIGHT // 2 - 40)
            draw_text_shadow(screen, "Press P to resume", font_medium, (180, 180, 200),
                             WIN_WIDTH // 2 - 100, WIN_HEIGHT // 2 + 30)

        # ── Game Over overlay ──
        if game.state == "gameover":
            overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_text_shadow(screen, "GAME OVER", font_title, (255, 80, 80),
                             WIN_WIDTH // 2 - 160, WIN_HEIGHT // 2 - 60)
            draw_text_shadow(screen, f"Score: {game.score}", font_large, WHITE,
                             WIN_WIDTH // 2 - 80, WIN_HEIGHT // 2 + 10)
            draw_text_shadow(screen, "Press ESC to restart", font_medium, (180, 180, 200),
                             WIN_WIDTH // 2 - 120, WIN_HEIGHT // 2 + 60)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
