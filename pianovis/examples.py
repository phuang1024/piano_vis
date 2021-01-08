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
from .constants import *
from .video import Video


def grieg():
    """Grieg Papillon example."""
    video = Video((1920, 1080), 30, 0)
    video.add_midi(os.path.join(PARENT, "examples", "grieg1.mid"))
    video.add_midi(os.path.join(PARENT, "examples", "grieg2.mid"))
    video.set_audio(os.path.join(PARENT, "examples", "grieg.mp3"))
    video.preview()
