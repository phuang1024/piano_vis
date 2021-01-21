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

import pygame
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askopenfilenames
from ..video import Video
from ..utils import PreciseClock
pygame.init()
Tk().withdraw()

BLACK = (0, 0, 0)
GRAY_DARK = (64, 64, 64)
GRAY = (128, 128, 128)
GRAY_LIGHT = (192, 192, 192)
WHITE = (255, 255, 255)

FONT_SMALL = pygame.font.SysFont("ubuntu", 14)
FONT_MED = pygame.font.SysFont("ubuntu", 20)


class Text:
    def __init__(self, text):
        self.text = text

    def draw(self, window, loc):
        text_loc = [loc[i] - self.text.get_size()[i]//2 for i in range(2)]
        window.blit(self.text, text_loc)


class Button:
    def __init__(self, text):
        self.text = text

    def draw(self, window, events, loc, size):
        loc = list(loc)
        loc[0] -= size[0]//2

        clicked = self.clicked(events, loc, size)
        color = (GRAY_DARK if clicked else GRAY_LIGHT) if self.hovered(loc, size) else WHITE
        text_loc = [loc[i] + (size[i]-self.text.get_size()[i])//2 for i in range(2)]

        pygame.draw.rect(window, color, (*loc, *size))
        pygame.draw.rect(window, BLACK, (*loc, *size), 2)
        window.blit(self.text, text_loc)

        return clicked

    def hovered(self, loc, size):
        mouse = pygame.mouse.get_pos()
        if loc[0] <= mouse[0] <= loc[0]+size[0] and loc[1] <= mouse[1] <= loc[1]+size[1]:
            return True
        return False

    def clicked(self, events, loc, size):
        if self.hovered(loc, size):
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    return True
        return False


class VideoDisp:
    button_clear_midis = Button(FONT_MED.render("Clear MIDIs", 1, BLACK))
    button_load_midi = Button(FONT_MED.render("Load MIDIs", 1, BLACK))

    def __init__(self):
        self.video = Video((1920, 1080), 30, 1)
        self.time = 0
        self.frame = 0
        self.playing = False

        self.arrow_hold = 0

    def draw(self, window, events, loc, size):
        surface = pygame.transform.scale(self.video._render(self.frame), size)
        window.blit(surface, loc)
        pygame.draw.rect(window, WHITE, (*loc, *size), 1)

        window.blit(FONT_SMALL.render(f"Frame: {self.frame}", 1, WHITE), (loc[0]+10, loc[1]+10))


        if self.button_clear_midis.draw(window, events, (loc[0]+size[0]+100, loc[1]), (160, 40)):
            self.video._midi_paths = []
            self.video._prep_render()
        if self.button_load_midi.draw(window, events, (loc[0]+size[0]+100, loc[1]+50), (160, 40)):
            self.video._midi_paths.extend(askopenfilenames())
            self.video._prep_render()

        self.time += 1
        if self.playing:
            self.frame += 1

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.playing = not self.playing
                elif event.key == pygame.K_RIGHT and not self.playing:
                    self.frame += 1
                    self.arrow_hold = self.time
                elif event.key == pygame.K_LEFT and not self.playing:
                    self.frame -= 1
                    self.arrow_hold = self.time

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and self.time-self.arrow_hold > 20:
            self.frame += 1
        if keys[pygame.K_LEFT] and self.time-self.arrow_hold > 20:
            self.frame -= 1

        self.frame = max(self.frame, 0)


def launch(resizable=True):
    """
    Starts pianovis app.
    :param resizable: Make the window resizable?
    """
    pygame.display.set_caption("Piano Visualizer - App")
    if resizable:
        window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    else:
        window = pygame.display.set_mode((1600, 900))

    width, height = 1280, 720
    resized = False

    video = VideoDisp()

    clock = PreciseClock(30)
    while True:
        clock.tick()
        pygame.display.update()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            elif event.type == pygame.VIDEORESIZE:
                resized = True
                width, height = event.size

            elif event.type == pygame.ACTIVEEVENT and resized:
                window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                resized = False

        vid_loc = list(map(int, (50, 50)))
        vid_size = list(map(int, (width*3/4, width*27/64)))

        window.fill(BLACK)
        video.draw(window, events, vid_loc, vid_size)
