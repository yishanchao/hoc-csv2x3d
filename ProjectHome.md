This project offers a Python script for converting Radiohead's House of Cards csv data to X3D.

The script can be extensively parameterized to convert to different X3D geometry types (standard and non-standard conform ones).

Directly get it here (or via the Source tab):
http://hoc-csv2x3d.googlecode.com/svn/trunk/hoc-csv2x3d.py

# Usage #

```
usage: hoc-csv2x3d.py [options] <action>

  Convert Radiohead's "House of Cards" csv data to X3D.

actions:
  convert
    Convert csv data to X3D.

  scene
    Build a X3D scene using the converted data. Using frames between STARTFRAME
    and ENDFRAME reading from DATA_DIR writing to TARGET_DIR

example usage:

  hoc-csv2x3d.py convert -s1 -e 500
    Converts the csv files 1-500 to X3D applying 4th param to color and size.

  hoc-csv2x3d.py convert -s1 -e 500 -f 5
    Converts the csv files 1-500 to X3D applying 4th param to color and size,
    scaling the size by factor 5.

  hoc-csv2x3d.py convert -s1 -e 500 --no-color --no-size
    Converts the csv files 1-500 to X3D without using the 4th param.

  hoc-csv2x3d.py scene -s1 -e 500
    Creates an X3D file containing all converted data via <Inline> elements and
    animating them.

options:
  -h, --help            show this help message and exit
  -d DATA_DIR, --dir=DATA_DIR
                        The directory containing the original csv data files
                        (default: csv).
  -x TARGET_DIR, --targetdir=TARGET_DIR
                        The target directory containing the converted X3D
                        files (default: x3d).
  -s START_FRAME, --startframe=START_FRAME
                        The index of the frame to start with (default: 1).
  -e END_FRAME, --endframe=END_FRAME
                        The index of the frame to end with (default: 90).
  --no-color            Prevent use the intensity data (4th parameter) as the
                        greyvalue of a point. This will omit the <Color>
                        element within the particle set.
  --no-size             Do not use the intensity data (4th parameter) as the
                        size of a point (uniform scaling). (default: True)
  -f INTENSITY_SIZEFACTOR, --sizefactor=INTENSITY_SIZEFACTOR
                        Intensity value (4th parameter) is multiplied by this
                        for scaling (default: 5).
  -t GEO_TYPE, --geotype=GEO_TYPE
                        The type of geometry to use as a container for the
                        converted data. Supported types are ParticleSet,
                        PointSet and LineSet. (default: ParticleSet).
  -b, --binary          When given the inline files will be written as x3db
                        (binary files). Requires aopt tool from
                        instantReality.
```