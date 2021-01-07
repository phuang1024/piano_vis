# PianoVis 0.1.4
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
    * resolution: (x, y) pixel resolution of video.
    * fps: FPS (frames per second) of video.
    * offset: Offset (frames) of video from audio. Usually, a value of 1 makes the video look lined up with the audio.
    * return: None
* `Video.configure(path: str, value: Any) -> None`
    * Sets an option for the video (read more in the Customization section).
    * path: Option path.
    * value: Value to set path to.
    * return: None

<br>

## Customization
