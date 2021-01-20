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
import shutil
import time
import threading
import multiprocessing
import pygame
import cv2
import mido
import colorsys
import colorama
from typing import Any, Tuple
from hashlib import sha256
from colorama import Fore
from .constants import *
from .utils import PreciseClock, print_process
pygame.init()
colorama.init()


class Video:
    """Video class that contains midis and export."""
    _key_subdivs = 50
    _block_glow_height = 20

    def __init__(self, resolution: Tuple[int, int], fps: int, offset: int, decor_surf: pygame.Surface = None) -> None:
        """
        Initializes video.
        :param resolution: Resolution (x, y) of video.
        :param fps: Frames per second of video.
        :param offset: Offset (frames) in start time of playing.
        :param decor_surf: Decoration surface, blitted under the piano.
        """
        self._res = resolution
        self._fps = fps
        self._offset = offset
        self._decor_surf = decor_surf
        self._midi_paths = []
        self._audio_path = None
        self._notes = []
        self._gen_info()

    def _gen_info(self):
        width, height = self._res
        x_size = width * 0.95
        x_offset = width * 0.025
        y_offset = height / 2
        key_width = x_size / 52

        self._options = {
            "keys.white.gap": 2,
            "keys.white.color": (215, 215, 210),
            "keys.black.width_fac": 0.6,
            "keys.black.height_fac": 0.65,
            "keys.black.color": (64, 64, 64),
            "blocks.speed": 180,
            "blocks.border": 0,
            "blocks.color_grad": BLOCK_RAINBOW,
            "blocks.color_hue": 0,
            "blocks.color_saturation": 0.9,
            "blocks.color_value": 1,
            "blocks.color_border": (255, 255, 255),
            "blocks.rounding": 5,
            "blocks.motion_blur": True,
            "blocks.light": False,
        }

        # Key positions
        self._key_width = key_width
        self._key_height = height / 4
        self._key_y_loc = y_offset
        self._key_locs = []
        for key in range(88):
            self._key_locs.append([key, self._is_white(key), self._find_x_loc(key)])

        self._key_locs = sorted(self._key_locs, key=(lambda x: 0 if x[1] else 1))

    def _is_white(self, key):
        return (key-3) % 12 not in (1, 3, 6, 8, 10)

    def _find_x_loc(self, key):
        width, height = self._res
        x_size = width * 0.95
        x_offset = width * 0.025
        key_width = x_size / 52

        num_white_before = 0
        for k in range(key):
            if self._is_white(k):
                num_white_before += 1

        loc = x_offset + key_width*num_white_before
        if not self._is_white(key):
            loc -= key_width * self._options["keys.black.width_fac"] / 2
        return loc

    def configure(self, path: str, value: Any) -> None:
        self._options[path] = value

    def add_midi(self, path: str) -> None:
        """Adds midi path to list."""
        self._midi_paths.append(path)

    def set_audio(self, path: str) -> None:
        """Sets audio file."""
        self._audio_path = path

    def _color_mix(self, col1, col2, fac):
        diff = [col2[i]-col1[i] for i in range(3)]
        color = [col1[i]+diff[i]*fac for i in range(3)]
        return color

    def _get_color(self, key):
        def convert(color):
            color = list(color)
            color[0] += self._options["blocks.color_hue"]
            color[0] = color[0] % 1
            color[1] *= self._options["blocks.color_saturation"]
            color[2] *= self._options["blocks.color_value"]
            color = [255*x for x in colorsys.hsv_to_rgb(*color)]
            return color

        grad = self._options["blocks.color_grad"]

        if len(grad) == 0:
            return convert(WHITE)
        elif len(grad) == 1:
            return convert(grad[0][1])

        fac = key / 88
        if fac <= grad[0][0]:
            return convert(grad[0][1])
        elif fac >= grad[-1][0]:
            return convert(grad[-1][1])

        below_ind = 0
        above_ind = 1
        for i, section in enumerate(grad):
            if fac >= section[0] and fac <= grad[i+1][0]:
                below_ind = i
                above_ind = i + 1
                break

        below_sec = grad[below_ind]
        above_sec = grad[above_ind]
        loc_fac = (fac - below_sec[0]) / (above_sec[0] - below_sec[0])
        color = self._color_mix(below_sec[1], above_sec[1], loc_fac)
        return convert(color)

    def _parse_midis(self):
        self._notes = []
        num_midis = len(self._midi_paths)

        for i, path in enumerate(self._midi_paths):
            print_msg = f"Parsing midi {i+1} of {num_midis}"
            print_process.write(print_msg)
            midi = mido.MidiFile(path)
            tpb = midi.ticks_per_beat

            starts = [None for i in range(88)]
            tempo = 500000
            curr_frame = self._offset
            for msg in midi.tracks[0]:
                curr_frame += msg.time / tpb * tempo / 1000000 * self._fps
                if msg.is_meta and msg.type == "set_tempo":
                    tempo = msg.tempo
                elif msg.type == "note_on":
                    note, velocity = msg.note-21, msg.velocity
                    if velocity == 0:
                        self._notes.append((note, starts[note], curr_frame))
                    else:
                        starts[note] = curr_frame

            print_process.clear(print_msg)

        print_process.finish(f"Finished parsing {num_midis} midis.")

    def _calc_num_frames(self):
        max_note = max(self._notes, key=(lambda x: x[2]))
        return int(max_note[2] + 30)

    def _prep_render(self):
        self._parse_midis()

    def _render_piano(self, keys):
        surface = pygame.Surface((1920, 1080), pygame.SRCALPHA)
        width_white = self._key_width - self._options["keys.white.gap"]
        width_black = self._key_width * self._options["keys.black.width_fac"]
        height_white = self._key_height
        height_black = self._key_height * self._options["keys.black.height_fac"]

        for index, white, x_loc in self._key_locs:
            playing = index in keys

            if playing:
                color = self._options["keys.white.color"] if white else self._options["keys.black.color"]
                width = width_white if white else width_black
                height = height_white if white else height_black
                height_inc = height / self._key_subdivs
                height /= self._key_subdivs
                height += 1
                for i in range(self._key_subdivs):
                    curr_col = self._color_mix(self._get_color(index), color, i/self._key_subdivs)
                    pygame.draw.rect(surface, curr_col, (x_loc, self._key_y_loc+i*height_inc, width, height))

            else:
                color = self._options["keys.white.color"] if white else self._options["keys.black.color"]
                if white:
                    pygame.draw.rect(surface, color, (x_loc, self._key_y_loc, width_white, height_white))
                else:
                    pygame.draw.rect(surface, color, (x_loc, self._key_y_loc, width_black, height_black))

        pygame.draw.rect(surface, (0, 0, 0), (0, self._res[1]/4*3, self._res[0], self._res[1]/4))
        return surface

    def _render_blocks(self, frame, playing):
        surface = pygame.Surface(self._res, pygame.SRCALPHA)
        width, height = self._res
        y_offset = height / 2
        white_width = width * 0.95 / 52
        black_width = white_width * self._options["keys.black.width_fac"]

        # Base blocks
        for key, start, end in self._notes:
            bottom_y = (frame-start)/self._fps*self._options["blocks.speed"] + y_offset
            top_y = bottom_y - (end-start)/self._fps*self._options["blocks.speed"]

            visible = bottom_y >= 0 and top_y <= y_offset
            if visible:
                x_loc = self._find_x_loc(key)
                width = white_width if self._is_white(key) else black_width
                height = bottom_y - top_y
                color = self._get_color(key)

                radius = self._options["blocks.rounding"]
                if self._options["blocks.motion_blur"]:
                    mb_dist = self._options["blocks.speed"] / self._fps / 3
                    pygame.draw.rect(surface, (*color, 92), (x_loc, top_y-mb_dist, width-1, height+mb_dist), border_radius=radius)
                pygame.draw.rect(surface, color, (x_loc, top_y, width-1, height), border_radius=radius)
                if (border := self._options["blocks.border"]) > 0:
                    pygame.draw.rect(surface, self._options["blocks.color_border"], (x_loc, top_y, width-1, height),
                        border, border_radius=radius)

        # Glowing
        if self._options["blocks.light"]:
            for key in playing:
                white = self._is_white(key)
                x_range = (self._find_x_loc(key), self._find_x_loc(key) + (white_width if white else black_width) + 5)
                x_range = list(map(int, x_range))

                for i in range(20):
                    curr_y = self._res[1] // 2 - i
                    for x in range(*x_range):
                        curr_loc = (x, curr_y)
                        color = surface.get_at(curr_loc)
                        if color[:3] != (0, 0, 0):
                            fac = i / 20
                            new_col = self._color_mix((255, 255, 255), self._get_color(key), fac)
                            surface.set_at(curr_loc, new_col)

        pygame.draw.rect(surface, (0, 0, 0), (0, y_offset, *self._res))
        return surface

    def _render(self, frame):
        surface = pygame.Surface(self._res)

        playing = []
        for note in self._notes:
            if note[1] <= frame <= note[2]:
                playing.append(note[0])
        playing = list(set(playing))

        surface.blit(self._render_blocks(frame, playing), (0, 0))
        surface.blit(self._render_piano(playing), (0, 0))

        if self._decor_surf is not None:
            width, height = self._decor_surf.get_size()
            x = (self._res[0]-width) // 2
            y = (self._res[1]//4-height) // 2
            y += self._res[1] * 3 // 4
            surface.blit(self._decor_surf, (x, y))

        return surface

    def preview(self, resolution: Tuple[int, int] = (1600, 900), show_meta: bool = True, audio: bool = True) -> None:
        """
        Previews the video with a Pygame window.
        :param resolution: Resolution of window.
        :param audio: Play with audio but no jumping forward or backward.
        """
        try:
            from playsound import playsound
        except ModuleNotFoundError:
            print("Module \"playsound\" not found. Install?")
            print("    These packages will be installed:")
            print("    * playsound")
            print("    * vext")
            print("    * vext.gi")
            result = input("Install? (y/n) ")
            if result.lower() == "y":
                os.system("pip install playsound")
                os.system("pip install vext")
                os.system("pip install vext.gi")
            else:
                return

        def get_note_info(frame):
            notes = self._notes
            info = {"played": 0, "playing": 0, "to_play": 0}
            for note in notes:
                start, end = note[1], note[2]
                if frame < start:
                    info["to_play"] += 1
                elif frame >= start:
                    info["played"] += 1
                    if frame <= end:
                        info["playing"] += 1

            return info

        def play_audio(path):
            time.sleep(0.03)
            playsound(path)

        self._prep_render()
        total_frames = self._calc_num_frames()

        pygame.display.set_caption("PianoVis - Preview")
        pygame.display.set_icon(LOGO)
        window = pygame.display.set_mode(resolution)
        font = pygame.font.SysFont("ubuntu", 14)

        clock = PreciseClock(self._fps)
        frame = 0
        fps = self._fps
        playing = True
        if audio and self._audio_path is not None:
            threading.Thread(target=play_audio, args=(self._audio_path,)).start()

        while True:
            start = time.time()
            clock.tick()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                elif event.type == pygame.KEYDOWN and not audio:
                    if event.key == pygame.K_LEFT:
                        frame -= 1
                    elif event.key == pygame.K_RIGHT:
                        frame += 1
                    elif event.key == pygame.K_DOWN:
                        frame -= 100
                    elif event.key == pygame.K_UP:
                        frame += 100
                    elif event.key == pygame.K_SPACE:
                        playing = not playing

                    frame = min(frame, total_frames-1)
                    frame = max(frame, 0)

            window.fill((0, 0, 0))
            rend_start = time.time()
            surface = self._render(frame)
            rend_time = str(time.time() - rend_start)[:6]
            idle_time = str((1/self._fps) - float(rend_time))[:6]

            surface = pygame.transform.scale(surface, resolution)
            window.blit(surface, (0, 0))

            if show_meta:
                note_info = get_note_info(frame)
                num_to_play = note_info["to_play"]
                num_playing = note_info["playing"]
                num_played = note_info["played"]

                window.blit(font.render(f"Frame: {frame}", 1, (255, 255, 255)), (20, 20))
                window.blit(font.render(f"Render time: {rend_time}", 1, (255, 255, 255)), (20, 40))
                window.blit(font.render(f"Idle time: {idle_time}", 1, (255, 255, 255)), (20, 60))
                window.blit(font.render(f"FPS: {fps}", 1, (255, 255, 255)), (20, 80))
                window.blit(font.render(f"Notes to play: {num_to_play}", 1, (255, 255, 255)), (20, 100))
                window.blit(font.render(f"Notes playing: {num_playing}", 1, (255, 255, 255)), (20, 120))
                window.blit(font.render(f"Notes played: {num_played}", 1, (255, 255, 255)), (20, 140))

            fps = str(1 / (time.time() - start))[:6]
            if playing and frame < total_frames:
                frame += 1

    def export(self, path: str, multicore: bool = False, max_cores: int = multiprocessing.cpu_count(), notify: bool = False) -> None:
        """
        Exports video to path.
        :param path: Path to export, must be .mp4
        :param multicore: Uses multiple cores to export video. This may be faster, but takes more power and uses more disk space.
        :param max_cores: Maximum cores to use when exporting.
        :param notify: Sends notification when done exporting (requres win10toast on Windows, does not work on Mac).
        """
        def multicore_video(path, frames):
            video = cv2.VideoWriter(tmp_vid_path, cv2.VideoWriter_fourcc(*"MPEG"), self._fps, self._res)
            start = time.time()
            for i in range(frames):
                msg = f"Encoding frame {i} of {frames}"
                elapse = time.time() - start
                left = (frames-i-1) * elapse / (i+1)
                percent = (i+1) / frames
                progress = int(percent * 50)
                progress_msg = "[{}{}] {}%".format("#"*int(progress), "-"*int(50-progress), int(percent*100))
                final_msg = "{}    Remaining: {}    {}".format(msg, str(left)[:6], progress_msg)
                print_process.write(final_msg)

                if os.path.isfile(curr_img_path := os.path.join(path, f"{i}.png")):
                    video.write(cv2.imread(curr_img_path))
                print_process.clear(final_msg)

            print_process.finish(f"Finished encoding {frames} frames.")
            video.release()

        def multicore_export(path, start, end):
            for frame in range(start, end+1):
                surface = self._render(frame)
                filepath = os.path.join(path, f"{frame}.png")
                pygame.image.save(surface, filepath)

        if not path.endswith(".mp4"):
            raise ValueError("Path must end with .mp4")

        print("-" * 50)
        print(f"Exporting video:")

        # Setup export
        get_hash = lambda: sha256(str(time.time()).encode()).hexdigest()[:20]
        parent = os.path.realpath(os.path.dirname(__file__))

        hash = get_hash()
        self._prep_render()
        frames = self._calc_num_frames()

        # Export frames
        if multicore:
            num_cores = min(multiprocessing.cpu_count(), max_cores)
            processes = []

            tmp_imgs_path = os.path.join(parent, hash)
            tmp_vid_path = os.path.join(parent, hash+".mp4")
            os.makedirs(tmp_imgs_path)

            try:
                curr_start = 0
                inc = frames / num_cores
                total_frames = 0
                for i in range(num_cores):
                    start = int(curr_start)
                    end = int(curr_start + inc)
                    total_frames += end - start + 1

                    process = multiprocessing.Process(target=multicore_export, args=(tmp_imgs_path, start, end))
                    process.start()
                    processes.append(process)

                    curr_start += inc + 1

                start = time.time()
                while True:
                    num_frames = len(os.listdir(tmp_imgs_path))
                    msg = f"Rendering frames, {num_frames}/{total_frames} finished."
                    elapse = time.time() - start
                    left = (total_frames-num_frames-1) * elapse / (num_frames+1)
                    percent = (num_frames+1) / total_frames
                    progress = int(percent * 50)
                    progress_msg = "[{}{}] {}%".format("#"*int(progress), "-"*int(50-progress), int(percent*100))
                    final_msg = "{}    Remaining: {}    {}".format(msg, str(left)[:6], progress_msg)
                    print_process.write(final_msg)

                    if num_frames >= total_frames:
                        print_process.clear(final_msg)
                        break

                    time.sleep(0.01)
                    print_process.clear(final_msg)

                for p in processes:
                    p.join()
                print_process.finish("Finished rendering frames.")

                video_process = multiprocessing.Process(target=multicore_video, args=(tmp_imgs_path, frames))
                video_process.start()
                processes.append(video_process)

                video_process.join()
                cv2.destroyAllWindows()

            except KeyboardInterrupt:
                for p in processes:
                    p.terminate()
                shutil.rmtree(tmp_imgs_path)
                if os.path.isfile(tmp_vid_path):
                    os.remove(tmp_vid_path)
                print(Fore.RED + "Keyboard Interrupt.")
                print(Fore.WHITE + "Removing temporary files.")
                return

            shutil.rmtree(tmp_imgs_path)

        else:
            tmp_img_path = os.path.join(parent, hash+".png")
            tmp_vid_path = os.path.join(parent, hash+".mp4")
            video = cv2.VideoWriter(tmp_vid_path, cv2.VideoWriter_fourcc(*"MPEG"), self._fps, self._res)

            try:
                start = time.time()
                for i in range(frames):
                    msg = f"Exporting frame {i} of {frames}"
                    elapse = time.time() - start
                    left = (frames-i-1) * elapse / (i+1)
                    percent = (i+1) / frames
                    progress = int(percent * 50)
                    progress_msg = "[{}{}] {}%".format("#"*int(progress), "-"*int(50-progress), int(percent*100))
                    final_msg = "{}    Remaining: {}    {}".format(msg, str(left)[:6], progress_msg)
                    print_process.write(final_msg)

                    surf = self._render(i)
                    pygame.image.save(surf, tmp_img_path)
                    video.write(cv2.imread(tmp_img_path))

                    print_process.clear(final_msg)

                print_process.finish(f"Finished exporting {frames} frames.")

                video.release()
                cv2.destroyAllWindows()

            except KeyboardInterrupt:
                print(Fore.RED + "Keyboard interrupt")
                os.remove(tmp_img_path)
                os.remove(tmp_vid_path)
                return

            os.remove(tmp_img_path)

        # Combine audio and video
        shutil.copy(tmp_vid_path, "no_audio_"+path)
        if self._audio_path is not None:
            print(Fore.WHITE + "Combining with audio")
            command = "ffmpeg -y -i {} -r {} -i {} -filter:a aresample=async=1 -c:a aac -c:v copy {}"
            command = command.format(self._audio_path, self._fps, tmp_vid_path, path)
            os.system(command)
        os.remove(tmp_vid_path)

        print_process.finish("Finished exporting animation.")
        print(Fore.WHITE + "-" * 50)

        if notify:
            if sys.platform == "linux":
                os.system("notify-send \"Piano Vis\" \"Finished exporting an animation!\"")
            elif sys.platform == "windows":
                try:
                    from win10toast import ToastNotifier
                    toast = ToastNotifier()
                    toast.show_toast("Piano Vis", "Finished exporting an animation!", duration=10)
                except ModuleNotFoundError:
                    print("win10toast not found. Install with \"pip install win10toast\" to show notifications.")
