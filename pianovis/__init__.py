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

import sys
import os
import time
import pygame
import cv2
import mido
import colorama
from colorama import Fore
from typing import Dict, List, Tuple
from hashlib import sha256
pygame.init()
colorama.init()


class Video:
    """Video class that contains midis and export."""

    def __init__(self, resolution: Tuple[int, int], fps: int) -> None:
        """Initializes video."""
        self._res = resolution
        self._fps = fps
        self._midi_paths = []
        self._gen_info()

    def _gen_info(self):
        width, height = self._res
        x_size = width * 0.95
        x_offset = width * 0.025
        y_offset = height / 2
        key_width = x_size / 52

        self._options = {
            "keys.white.gap": 2,
            "keys.white.color": (255, 255, 255),
            "keys.black.width_fac": 0.6,
            "keys.black.height_fac": 0.7,
            "keys.black.color": (64, 64, 64),
        }

        # Key positions
        self._key_width = key_width
        self._key_height = height / 4
        self._key_y_loc = y_offset
        self._key_locs = []
        for key in range(88):
            white = False if (key-3) % 12 in (1, 3, 6, 8, 10) else True
            num_white_before = 0
            for k in range(key):
                curr_white = False if (k-3) % 12 in (1, 3, 6, 8, 10) else True
                if curr_white:
                    num_white_before += 1

            info = [key, white, x_offset + key_width*num_white_before]
            if not white:
                info[2] -= key_width * self._options["keys.black.width_fac"] / 2
            self._key_locs.append(info)

        self._key_locs = sorted(self._key_locs, key=(lambda x: 0 if x[1] else 1))

    def configure(self, path, value):
        self._options[path] = value

    def add_midi(self, path: str) -> None:
        """Adds midi path to list."""
        self._midi_paths.append(path)

    def _calc_num_frames(self):
        return 100

    def _render_piano(self, keys):
        surface = pygame.Surface((1920, 1080), pygame.SRCALPHA)
        width_white = self._key_width - self._options["keys.white.gap"]
        width_black = self._key_width * self._options["keys.black.width_fac"]
        height_white = self._key_height
        height_black = self._key_height * self._options["keys.black.height_fac"]

        for index, white, x_loc in self._key_locs:
            playing = index in keys
            if white:
                pygame.draw.rect(surface, self._options["keys.white.color"], (x_loc, self._key_y_loc, width_white, height_white))
            else:
                pygame.draw.rect(surface, self._options["keys.black.color"], (x_loc, self._key_y_loc, width_black, height_black))

        return surface

    def _render(self, frame):
        surface = pygame.Surface(self._res)
        surface.blit(self._render_piano([]), (0, 0))
        return surface

    def export(self, path: str) -> None:
        """
        Exports video to path.
        :param path: Path to export, must be .mp4
        """
        if not path.endswith(".mp4"):
            raise ValueError("Path must end with .mp4")

        get_hash = lambda: sha256(str(time.time()).encode()).hexdigest()[:20]
        parent = os.path.realpath(os.path.dirname(__file__))
        frames = self._calc_num_frames()

        hash = get_hash()
        while os.path.isfile(os.path.join(parent, hash)):
            hash = get_hash()

        tmp_path = os.path.join(parent, hash+".png")
        video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MPEG"), self._fps, self._res)

        print("-" * 50)
        print(f"Exporting video containing {frames} frames:")
        try:
            for frame in range(frames):
                msg = f"Exporting frame {frame} of {frames}"
                sys.stdout.write(msg)
                sys.stdout.flush()
                sys.stdout.write("{0}{1}{0}".format("\b"*len(msg), " "*len(msg)))

                surface = self._render(frame)
                pygame.image.save(surface, tmp_path)
                video.write(cv2.imread(tmp_path))

            print(Fore.GREEN + f"Finished exporting {frames} frames.")

            video.release()
            cv2.destroyAllWindows()

        except KeyboardInterrupt:
            print(Fore.RED + "Keyboard interrupt")

        os.remove(tmp_path)
        print(Fore.WHITE + "-" * 50)
