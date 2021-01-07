# PianoVis 0.1.5
A Python piano video exporter.

<br>

## Quick Start
1. Install PianoVis: `pip install piano-vis`
2. Follow this code format:
```
import pianovis

resolution = (1920, 1080)
fps = 30
offset = 1

vid = pianovis.Video(resolution, fps, offset)
vid.add_midi("midi1.mid")
vid.add_midi("midi2.mid")
vid.set_audio("audio.mp3")
vid.export("video.mp4")
```

<br>

## pianovis.Video
`pianovis.Video` is the main video class which stores all midi and audio files, and exports the final video.
* `Video.__init__(resolution: Tuple[int, int], fps: int, offset: int) -> None`
    * Initializes video.
    * `resolution`: (x, y) pixel resolution of video.
    * `fps`: FPS (frames per second) of video.
    * `offset`: Offset (frames) of video from audio. Usually, a value of 1 makes the video look lined up with the audio.
    * `return`: None
* `Video.configure(path: str, value: Any) -> None`
    * Sets an option for the video (read more in the Customization section).
    * `path`: Option path.
    * `value`: Value to set path to.
    * `return`: None
* `Video.add_midi(path: str) -> None`
    * Appends path to midi list.
    * `path`: Midi file path.
* `Video.set_audio(path: str) -> None`
    * Sets audio file to path.
    * `path`: Audio file path.
* `Video.preview(resolution: Tuple[int, int] = (1600, 900), show_meta: bool = True) -> None:`
    * Opens a pygame window to preview the animation.
    * `resolution`=(1600, 900): Resolution of pygame window.
    * `show_meta`=True: Show metadata in the corner of window.
* `Video.export(self, path: str, multicore: bool = False, max_cores: int = multiprocessing.cpu_count(), notify: bool = False) -> None:`
    * Exports video to path.
    * `path`: Path to export (mp4)
    * `multicore`=False: Use multiple cores to export. Can be faster, but will take more power.
    * `max_cores`=multiprocessing.cpu_count(): Maximum cores to use. Only relevant if using multicore.
    * `notify`=False: Sends notification when done exporting. Only works on linux.

<br>

## Customization
Run `Video.configure` to change options.
* `keys.white.gap`: Gap (pixels) between white keys.
* `keys.white.color`: Color (RGB) of white keys.
* `keys.black.width_fac`: Factor of white key width.
* `keys.black.height_fac`: Factor of white key height.
* `keys.black.color`: Color (RGB) of black keys.
* `blocks.speed`: Speed (pixels per second) of blocks.
* `blocks.color_grad`: Color gradient of blocks: ((fac1, hsv1), (fac2, hsv2)...)
* `blocks.rounding`: Rounding radius of blocks.
* `blocks.motion_blur`: Use motion blur in blocks.
