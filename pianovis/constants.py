#  ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import os
import pygame
pygame.init()


# General
PARENT = os.path.realpath(os.path.dirname(__file__))
try:
    LOGO = pygame.image.load(os.path.join(PARENT, "images", "logo.png"))
except:
    print("Could not load logo image.")
    LOGO = pygame.Surface((100, 100))


# Colors
BLACK = (0, 0, 0)
GRAY = (0, 0, 0.5)
WHITE = (0, 0, 1)

DARK_RED_1 = (0, 0, 0.5)
RED_1 = (0, 1, 1)
DARK_ORANGE = (0.083, 1, 1)
ORANGE = (0.083, 1, 1)
DARK_YELLOW = (0.166, 1, 0.5)
YELLOW = (0.166, 1, 1)
DARK_GREEN = (0.333, 1, 0.5)
GREEN = (0.333, 1, 1)
DARK_CYAN = (0.5, 1, 0.5)
CYAN = (0.5, 1, 1)
DARK_BLUE = (0.6, 1, 0.5)
BLUE = (0.6, 1, 1)
DARK_MAGENTA = (0.8, 1, 0.5)
MAGENTA = (0.8, 1, 1)
DARK_PINK = (0.9, 1, 0.5)
PINK = (0.9, 1, 1)
DARK_RED_2 = (1, 1, 0.5)
RED_2 = (1, 1, 1)


# Block presets
BLOCK_RAINBOW = (
    (0, RED_1),
    (1, RED_2),
)
BLOCK_RAINBOW_MIRROR = (
    (0, RED_1),
    (0.5, RED_2),
    (1, RED_1),
)
BLOCK_RAINBOW_DOUBLE = (
    (0, RED_1),
    (0.5, RED_2),
    (1, (2, 1, 1)),
)
BLOCK_CHRISTMAS_1 = (
    (0, RED_1), (0.199, RED_1),
    (0.2, GREEN), (0.399, GREEN),
    (0.4, WHITE), (0.599, WHITE),
    (0.6, RED_1), (0.799, RED_1),
    (0.8, GREEN), (1, GREEN),
)
BLOCK_CHRISTMAS_2 = (
    (0, GREEN), (0.099, GREEN),
    (0.1, RED_1), (0.199, RED_1),
    (0.2, WHITE), (0.299, WHITE),
    (0.3, GREEN), (0.399, GREEN),
    (0.4, RED_1), (0.499, RED_1),
    (0.5, WHITE), (0.599, WHITE),
    (0.6, GREEN), (0.699, GREEN),
    (0.7, RED_1), (0.799, RED_1),
    (0.8, WHITE), (0.899, WHITE),
    (0.9, GREEN), (1, GREEN),
)
