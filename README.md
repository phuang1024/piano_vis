# Piano Visualizer
## Version 0.1.3

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
    * Your system must have FFMpeg to be able to export with audio.
5. Export video
    * `video.export("path.mp4")`
    * The exporting process will take a while.

### Customization:
#### Note: Default parameters are optimized for (1920, 1080) resolution.
`video.configure(path, value)`
* `keys.white.gap`: Gap between each white key (pixels).
* `keys.white.color`: Color (RGB) of white keys.
* `keys.white.color_playing`: Color (RGB) of white keys when playing.
* `keys.black.width_fac`: Factor of white key width.
* `keys.black.height_fac`: Factor of white key height.
* `keys.black.color`: Color (RGB) of black keys.
* `keys.black.color_playing`: Color (RGB) of black keys when playing.
* `blocks.speed`: Speed of falling blocks (pixels per second).
* `blocks.color_type`: Type of block coloring.
* `blocks.color`: Color (RGB) of blocks.
* `blocks.rounding`: Pixel width of rounding corners.
* `blocks.motion_blur`: Use motion blur on blocks?

### Frequently Asked Questions (FAQs)
* How do I export a video?
    * Read the "How To Use" section above.
* Am I allowed to put exported videos online?
    * Yes. Piano-vis is licensed under GPL v3, which allows you to use it for any purpose without credit (though it is appreciated).
* Why does it say ffmpeg is not found?
    * Piano-vis uses ffmpeg to combine the video and audio. If you don't have ffmpeg installed, an error will be generated.