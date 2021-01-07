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