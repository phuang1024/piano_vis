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
from typing import List, Tuple
from hashlib import sha256
pygame.init()
colorama.init()


class Video:
    """Video class that contains midis and export."""

    res: Tuple[int, int]
    fps: int
    midi_paths: List[str]

    def __init__(self, resolution: Tuple[int, int], fps: int) -> None:
        """Initializes video."""
        self.res = resolution
        self.fps = fps
        self.midi_paths = []
        self.gen_info()

    def gen_info(self):
        width, height = self.res
        x_size = width * 0.95
        x_offset = width * 0.025
        y_offset = height / 2
        key_width = x_size / 52

        # Key positions
        self.key_locs = []
        for key in range(88):
            white = False if (key-3) % 12 in (1, 3, 6, 8, 10) else True
            num_white_before = 0
            for k in range(key):
                curr_white = False if (k-3) % 12 in (1, 3, 6, 8, 10) else True
                if curr_white:
                    num_white_before += 1

            info = [key, white, x_offset + key_width*num_white_before, y_offset]
            if not white:
                info[1] += key_width / 2
            self.key_locs.append(info)

        self.key_locs = sorted(self.key_locs, key=(lambda x: 0 if x[1] else 1))

    def add_midi(self, path: str) -> None:
        """Adds midi path to list."""
        self.midi_paths.append(path)

    def calc_num_frames(self):
        return 100

    def render_piano(self, keys):
        pass

    def render(self, frame):
        surface = pygame.Surface(self.res)
        pygame.draw.rect(surface, (255, 255, 255), (10, 10, 100, 100))
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
        frames = self.calc_num_frames()

        hash = get_hash()
        while os.path.isfile(os.path.join(parent, hash)):
            hash = get_hash()

        tmp_path = os.path.join(parent, hash+".png")
        video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MPEG"), self.fps, self.res)

        print("-" * 50)
        print(f"Exporting video containing {frames} frames:")
        try:
            for frame in range(frames):
                msg = f"Exporting frame {frame} of {frames}"
                sys.stdout.write(msg)
                sys.stdout.flush()
                sys.stdout.write("{0}{1}{0}".format("\b"*len(msg), " "*len(msg)))

                surface = self.render(frame)
                pygame.image.save(surface, tmp_path)
                video.write(cv2.imread(tmp_path))

            print(Fore.GREEN + f"Finished exporting {frames} frames.")

            video.release()
            cv2.destroyAllWindows()

        except KeyboardInterrupt:
            print(Fore.RED + "Keyboard interrupt")

        os.remove(tmp_path)
        print(Fore.WHITE + "-" * 50)
