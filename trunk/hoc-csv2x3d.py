#!/usr/bin/env python

# Copyright (c) 2008, Peter Eschler [peschler [at] googlemail.com]
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

#    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#    * Neither the name of pyjax.net nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
from optparse import OptionParser
from os import system, listdir, remove #, getcwd, chdir, path, , waitpid, getenv, mkdir

X3D_TEMPLATE = """<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 3.0//EN" "http://www.web3d.org/specifications/x3d-3.0.dtd">
<X3D version='3.0'>
    <Scene DEF="Scene">
        
        <Appearance DEF='ap'>
            <BlendMode srcFactor='src_alpha' destFactor='one' colorTransparency='0.5' />
            <ImageTexture url='dot.png' envMode='MODULATE' />
        </Appearance>
        
        <Transform>
            <Switch DEF='sw' whichChoice='0'>                
                %(inline_switches)s
            </Switch>
        </Transform>
        
        <TimeSensor DEF='ts' loop='true' cycleInterval='0.03'/>
        <ROUTE fromNode='ts' fromField='cycleTime' toNode='sw' toField='next' />

    </Scene>
</X3D>
"""

X3D_PARTICLE_SET = "<ParticleSet drawOrder='any' lit='true' %(sizes)s>"
X3D_POINT_SET = "<PointSet>"
X3D_LINE_SET = "<LineSet vertexCount='%(vertexCount)s'>"

X3D_COORD_TEMPLATE = """<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 3.0//EN" "http://www.web3d.org/specifications/x3d-3.0.dtd">
<X3D version='3.0'>
    <Scene DEF="Scene">
        <Shape>
            <Appearance />            
            %(geotype_start)s
                <Coordinate DEF="coords" containerField='coord' point='%(points)s' />
                %(colors)s
            </%(geotype_end)s>
        </Shape>
    </Scene>
</X3D>
"""


def main():
    usage = \
"""%prog [options] <action>

  Convert Radiohead's "House of Cards" csv data to X3D.
  
actions:        
  convert
    Convert csv data to X3D. 
        
  scene
    Build a X3D scene using the converted data. Using frames between STARTFRAME 
    and ENDFRAME reading from DATA_DIR writing to TARGET_DIR
    
example usage:
        
  %prog convert -s1 -e 500 
    Converts the csv files 1-500 to X3D applying 4th param to color and size.
    
  %prog convert -s1 -e 500 -f 5
    Converts the csv files 1-500 to X3D applying 4th param to color and size,
    scaling the size by factor 5.   
    
  %prog convert -s1 -e 500 --no-color --no-size
    Converts the csv files 1-500 to X3D without using the 4th param.
  
  %prog scene -s1 -e 500 
    Creates an X3D file containing all converted data via <Inline> elements and
    animating them."""  
    
    parser = OptionParser(usage)
    parser.set_defaults(data_dir='csv', target_dir='x3d', start_frame=1, end_frame=90,
                        globalfile=False, intensity_color=True,
                        intensity_size=True, intensity_sizefactor=5.0,
                        geo_type='ParticleSet')

    parser.add_option("-d", "--dir", dest="data_dir",
                      help="The directory containing the original csv data files (default: csv).")
    parser.add_option("-x", "--targetdir", dest="target_dir",
                      help="The target directory containing the converted X3D files (default: x3d).")
    parser.add_option("-s", "--startframe",
                      type='int', dest="start_frame",
                      help="The index of the frame to start with (default: 1).")
    parser.add_option("-e", "--endframe",
                      type='int', dest="end_frame",
                      help="The index of the frame to end with (default: 90).")
                                                        
    parser.add_option("--no-color",
                      action="store_false", dest="intensity_color",
                      help="Prevent use the intensity data (4th parameter) as the grey"\
                           "value of a point. This will omit the <Color> "\
                           "element within the particle set.")
    parser.add_option("--no-size",
                      action="store_false", dest="intensity_size",
                      help="Do not use the intensity data (4th parameter) as " \
                           "the size of a point (uniform scaling). (default: True)")
                      
    parser.add_option("-f", "--sizefactor",
                      type='float', dest="intensity_sizefactor",
                      help="Intensity value (4th parameter) is multiplied by this for scaling (default: 5).")                      
                      
    parser.add_option("-t", "--geotype",
                      dest="geo_type",
                      help="The type of geometry to use as a container for the converted data. Supported types are ParticleSet, PointSet and LineSet. (default: ParticleSet).")
                      
    parser.add_option("-b", "--binary",
                      action="store_true", dest="binary",
                      help="When given the inline files will be written as x3db (binary files). Requires aopt tool from instantReality.")
                                            
    (options, args) = parser.parse_args()    
             
    if len(args) != 1:
        parser.print_help()       
        sys.exit()
        
    action = args[0]
    if action == 'convert':
        convert(options) 
    elif action == 'scene':
        create_scene(options)
    else:
        print "Invalid action '%s'. Exiting." % action
        parser.print_help()   
        sys.exit()
                          
          
def create_scene(options):          
    
    print "Creating scene file..."
    main_filename = "main.x3d"
    main_file = open(main_filename, 'w')
    inline_line = ''
    for i in range(options.start_frame, options.end_frame+1):
        filename = '%s/%s.x3d' % (options.target_dir, i)
        if options.binary:
            filename += 'b'
        inline_line += '<Inline url="%s" />\n' % filename
        
    main_file.write( X3D_TEMPLATE % {'inline_switches': inline_line} )
    main_file.close()
    sys.exit()        

    
def convert(options):        
    print "Converting csv data start frame %s, end frame %s"\
          % (options.start_frame, options.end_frame)
          
    if options.intensity_size:
        print "Using 4th parameter as point/particle size (disable via --no-size)."
    if options.intensity_color:
        print "Using 4th parameter as greyscale value (disable via --no-color)."
        
    # Iterate over all csv files in the data dir
    csv_files = listdir(options.data_dir)
    for i in range(options.start_frame, options.end_frame+1):        
        # Build the filename
        filename = '%s/%s.csv' % (options.data_dir, i)
        x3d_filename = "%s/%s.x3d" % (options.target_dir, i)
        print "Converting csv file %s to %s ..." % (filename, x3d_filename)
        
        # Open the file
        csv_file = open(filename, 'r')
        
        # And read all lines
        lines = csv_file.readlines()
        csv_file.close()
        
        # Now write converted coords to X3D Coordinate file        
        x3d_file = open(x3d_filename, 'w')
        coord_str = color_str = size_str = ''        
        for line in lines:
            coords = line.split(',')
            coord_str += '%s, %s, %s,  ' % (coords[0], coords[1], coords[2])                      
            intensity = float(coords[3])
            norm_intensity = intensity / 255.0
            size = norm_intensity * options.intensity_sizefactor            
            
            # Calc a color from the intensity value. Adjust colors here...
            if options.intensity_color:    
                color_str += '%s, %s, %s,  ' % (norm_intensity, norm_intensity, norm_intensity)                            
            
            # Calc a size value from the intensity value (2/3 uniform scale)
            size_str += '%s %s %s, ' % (size, size, size)            
            
        if options.intensity_color:            
            color_elem_str = "<Color containerField='color' color='%s' />" % color_str 
        else:
            color_elem_str = ''
                
        if options.intensity_size:           
            size_attr_str = "size='%s'" % size_str
        else:
            size_attr_str = ''
            
        geotype_start = ''
        geotype_end = options.geo_type                        
        if options.geo_type == "ParticleSet":
            geotype_start = X3D_PARTICLE_SET % {'sizes': size_attr_str}            
        elif options.geo_type == "PointSet":
            geotype_start = X3D_POINT_SET             
        elif options.geo_type == "LineSet":
            geotype_start = X3D_LINE_SET % {'vertexCount': len(lines)}
        else:
            print "Unsupported geotype '%s'. Exiting()" % options.geo_type
            sys.exit(-1)                        
                                                
        x3d_file.write(X3D_COORD_TEMPLATE % {'points': coord_str, 
                                             'colors': color_elem_str, 
                                             'geotype_start': geotype_start,
                                             'geotype_end': geotype_end})
        x3d_file.close()    
        
        # Check if binary option was given. If so convert file from .x3d to .x3db
        if options.binary:
            x3db_filename = x3d_filename + 'b'
            cmd = 'aopt -i %s -b %s' % (x3d_filename, x3db_filename)
            system(cmd)
            remove(x3d_filename)
         
        
if __name__ == "__main__":
    main() 
            