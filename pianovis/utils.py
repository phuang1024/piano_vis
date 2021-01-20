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
import time
import colorama
from colorama import Fore
colorama.init()


class PrintProcess:
    def write(self, msg):
        sys.stdout.write(msg)
        sys.stdout.flush()

    def clear(self, msg):
        sys.stdout.write("\r")
        sys.stdout.write(" "*len(msg))
        sys.stdout.write("\r")

    def finish(self, msg):
        print(Fore.GREEN + msg + Fore.WHITE)


class PreciseClock:
    def __init__(self, fps):
        self.pause_time = 1 / fps
        self.next_tick = time.time() + self.pause_time

    def tick(self):
        while time.time() < self.next_tick:
            time.sleep(0.001)
        self.next_tick += self.pause_time


print_process = PrintProcess()
