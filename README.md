# garmin-tilemapper

A command line tool that helps developers build tile-mapped anti-aliased graphics for Garmin wearables.

### About

The purpose of this tool is to showcase a rendering technique I developed using fonts as a tilemap. This is a more storage-friendly method than images, and allows developers to efficiently pack many frames of bitmapped animation in a 26kb font. Also, the great thing about fonts, its that they do alpha blending with the existing framebuffer on the canvas. So, you get anti-aliasing as a nice by-product.

### Quickstart

`tilemapper.py` requires Python 3.x, and the Pillow library. Install this using the python package manager:

```
pip install -r requirements.txt
```

### Usage

A full description of all the command line arguments are available with the `--help` flag.

```
usage: tilemapper.py [-h] -i INPUT [INPUT ...] -o OUTPUT [-m {static,rotate}]
                     [-r RESOLUTION] [-d [DEBUG]] [-u ANGLE_BEGIN]
                     [-v ANGLE_END] [-s ANGLE_STEP]

arguments:
  -h, --help            show this help message and exit
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        input png file(s)
  -o OUTPUT, --output OUTPUT
                        output file (png,fnt,json)
  -m {static,rotate}, --mode {static,rotate}
                        'static' will process one or more static frames.
                        'rotate' will rotate a frame
  -r RESOLUTION, --resolution RESOLUTION
                        resolution of target device
  -d [DEBUG], --debug [DEBUG]
                        turn debug mode on
  -u ANGLE_BEGIN, --angle-begin ANGLE_BEGIN
                        begin angle (rotate mode)
  -v ANGLE_END, --angle-end ANGLE_END
                        end angle (rotate mode)
  -s ANGLE_STEP, --angle-step ANGLE_STEP
                        step between angles (rotate mode)
```

The tool has two modes, **static** and **rotate**, toggled using the `-m` or `--mode` flag. The default mode is `static`.

#### Static mode

This mode generates a tilemap from one or more input files, as follows:

```
tilemapper.py -i source.png -o output
```

This will generate three output files — corresponding to the font files, `fnt` and `png`, and a `json` jsonDataResources  file:

```
output.png, output.fnt, output.json
```

**Multiple source files** are also supported as follows:

```
tilemapper.py -i source1.png source2.png source3.png -o output
tilemapper.py -i source*.png  -o output
```

This combines all three source files into a single tilemap, with three frames in the `json` file.


#### Rotate mode

Rotate will automatically rotate your source image given a number of steps. This is handy when developing elements that rotate around a centerpoint, such as the hands of a watchface.

The `-m` or `--mode` flag should be set with `rotate`. You will need to define the beginning and end angles, and number of degree steps in-between. The `--angle-begin`, `--angle-end`, `--angle-step` flags set these values as follows:

```
tilemapper.py -i source.png -o output -m rotate --angle-begin 0 --angle-end 90 --angle-step 6
```

This will rotate the source image counter-clockwise from 0 degrees to 90 degrees in 6 degree steps, and generate 15 frames in the `json` file.

#### Device resolution

`tilemapper` supports a target device resolution, with `240` pixels being the default resolution.

Define this with the `--resolution` flag:

```
tilemapper.py -i source.png -o output --resolution 280
```

Right now, all resolutions are supported. I can't keep up with all the different resolutions Garmin devices have, so this is an unrestricted field.

#### Using the generated tilemaps

See the sample watchface code in the `samples` directory.

## Troubleshooting

As an early release tool, there are heaps of bugs. Here are some key rules to follow that will help you get great results:

* All input files must be one or more `png` files.
* Only **greyscale** `png` files will work correctly.
* Only **square source images** (ratio 1:1) will work correctly.
* All input files should be the **same size** and aspect ratio.
* Source images should be greater than the target resolution. Try starting with a 1000x1000 image.
* See the `samples` folder for examples of images that work.

#### Contact me

Have some useful feedback, or need help? Contact me by contributing to this thread in the [Garmin Developer Forum](https://forums.garmin.com/developer/connect-iq/f/discussion/195648/tilemapper-tool-for-tile-mapped-anti-aliased-graphics).
