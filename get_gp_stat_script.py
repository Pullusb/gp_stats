
import bpy
import sys
import csv
from pathlib import Path
import argparse

def write_stats(csv_path, anonymous=False):
    csv_path = Path(csv_path)

    # Get the file name without extension
    file_name = Path(bpy.data.filepath).stem
    if anonymous:
        file_name = ' '

    # Loop through GP objects
    gp_datas = []
    for ob in bpy.data.objects:
        if ob.type != 'GPENCIL':
            continue
        
        ## Avoid scanning same data multiple times ?
        if ob.data in gp_datas:
            continue
        gp_datas.append(ob.data)


        # Object name
        name = ob.name
        gp = ob.data

        # -- Stats --

        # number of layers in the object
        nb_layers = len(gp.layers)
        nb_strokes = 0
        nb_points = 0

        strokes_per_frames = []
        points_per_frames = []

        frames_per_layer = []
        for layer in gp.layers:
            frames_per_layer.append(len(layer.frames))
            
            
            for frame in layer.frames:
                strokes_per_frames.append(len(frame.strokes))
                nb_strokes += len(frame.strokes)

                frame_points = 0
                for stroke in frame.strokes:
                    frame_points += len(stroke.points)
                    nb_points += len(stroke.points)
                
                points_per_frames.append(frame_points)       
                

        nb_frames = sum(frames_per_layer)
        avg_frames = round(nb_frames / len(frames_per_layer))

        avg_strokes = round(sum(strokes_per_frames) / len(strokes_per_frames))
        avg_points = round(sum(points_per_frames) / len(points_per_frames))

        # number of materials
        nb_materials = len(ob.material_slots)
        # number of modifiers
        nb_modifiers = len(ob.modifiers)

        if anonymous:
            name = ' '

        # Add csv row with blend name and gp stats
        data = [file_name, name,
                nb_layers, nb_strokes, nb_points, 
                avg_frames, avg_strokes, avg_points,
                nb_materials, nb_modifiers]

        with csv_path.open("a", newline="") as f:
            writer = csv.writer(f)

            # Write the data to the csv file
            writer.writerow(data)
            
            ## Write an empty line ?
            # writer.writerow([])

    # Close blend file
    # bpy.ops.wm.quit_blender()


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if '--' in sys.argv:
    argv = sys.argv[sys.argv.index('--') + 1:]
    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output_csv', type=str, required=True)
    parser.add_argument('-anon', '--anonymous', type=str2bool, nargs='?',
                        default=False,
                        help="anonymous mode, do not store any name")

    args = parser.parse_known_args(argv)[0]
    

    # print('-', bpy.data.filepath, '->', args.output_csv)
    
    print('> ', bpy.data.filepath)
    write_stats(args.output_csv, anonymous=args.anonymous)
