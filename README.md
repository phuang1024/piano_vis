# Piano Visualizer
## Version 0.0.6

This version exports a piano video with the keys lighting up as the music plays.

### How to use:
1. Install the package:
    * `pip install piano-vis`
    * `pip install --upgrade piano-vis`, use this command if you have a previous version installed.
2. Import and define a video:
    * `import pianovis`
    * `video = pianovis.Video(resolution, fps, offset)`
3. Add midi files
    * `video.add_midi(path1)`
    * `video.add_midi(path2)`
    * ...
4. Optional: Add an audio file (will use the latest set audio)
    * `video.set_audio(path)`
5. Export video
    * `video.export("path.mp4")`
    * The exporting process will take a while.