import os
import re
import csv
import subprocess
from pathlib import Path
import itertools

"""
## v1.0
## Get Grease pencil objects stats
## Recursively enter subdirectories at location defined at bottom of the script
## write a csv file

## Tested with Blender 3.3.1 and 3.4 on windows and linux 

Stat per GP objects:
    - Number of layers, frames, strokes, points
    - Average number of frames per layer and strokes/point per frames
    - Number of modifier used
    - Number of materials used
"""

def scanned_file_list(csv_output):
    import csv
    
    blend_stems = []
    
    # Open the CSV file
    with open(csv_output, 'r') as f:
        # Create a CSV reader object
        reader = csv.reader(f)
        
        # Skip the header row
        next(reader)
        
        for row in reader:
            # Retrieve the value in the first column
            value = row[0]
            if value and not value in blend_stems:          
                blend_stems.append(value)

        # The values in the first column are now stored in the list
    return blend_stems

def is_exclude(name, patterns) :
    from fnmatch import fnmatch

    if not isinstance(patterns, (list,tuple)) :
        patterns = [patterns]

    return any([fnmatch(name, p) for p in patterns])

def get_last_files(root, pattern=r'_v\d{3}\.\w+', only_matching=False, ex_file=None, ex_dir=None, keep=1, verbose=False) -> list:
    '''Recursively get last(s) file(s) (when there is multiple versions) in passed directory

    root -> str: Filepath of the folder to scan.
    pattern -> str: Regex pattern to group files.
    only_matching -> bool: Discard files that aren't matched by regex pattern.
    ex_file -> list : List of fn_match pattern to exclude files.
    ex_dir -> list : List of fn_match pattern of directory name to skip.
    keep -> int: Number of lasts versions to keep when there are mutliple versionned files (e.g: 1 keep only last).
    verbose -> bool: Print infos in console.
    '''

    files = []
    if ex_file is None:
        all_items = [f for f in os.scandir(root)]
    else:
        all_items = [f for f in os.scandir(root) if not is_exclude(f.name, ex_file)]

    allfiles = [f for f in all_items if f.is_file()]
    
    allfiles.sort(key=lambda x: x.name) # groupby fail to group if list is not sorted

    dirs = [f for f in all_items if f.is_dir()]

    for i in range(len(allfiles)-1,-1,-1):# fastest way to iterate on index in reverse
        if not re.search(pattern, allfiles[i].name):
            if only_matching:
                allfiles.pop(i)
            else:
                files.append(allfiles.pop(i).path)

    # separate remaining files in prefix grouped lists
    lilist = [list(v) for k, v in itertools.groupby(allfiles, key=lambda x: re.split(pattern, x.name)[0])]

    # get only item last of each sorted grouplist
    for l in lilist:
        versions = sorted(l, key=lambda x: x.name)[-keep:]  # exclude older
        for f in versions:
            files.append(f.path)

        if verbose and len(l) > 1:
            print(f'{root}: keep {str([x.name for x in versions])} out of {len(l)} elements')

    for d in dirs: # recursively treat all detected directory
        if ex_dir and is_exclude(d.name, ex_dir):
            # skip folder with excluded name 
            continue
        files += get_last_files(
            d.path, pattern=pattern, only_matching=only_matching, ex_file=ex_file, ex_dir=ex_dir, keep=keep)

    return sorted(files)


## -----------
## --- / INFOS
## -----------

# Path to blender executable (or just 'blender' if in PATH)
bin = 'blender'
# bin = '/opt/blender-3.4.0/blender'

# Directory to scan
dir_to_scan = r'/path/to/dorectory/to/scan'

# Output stat file
csv_output = str(Path(__file__).parent / 'stats.csv')

anonymous = False

# Path to script (should work as it)
gp_stat_script = str(Path(__file__).parent / 'get_gp_stat_script.py')

## -----------
## --- INFOS /
## -----------



assert Path(gp_stat_script).exists(), f'get_gp_stat_script.py is not found at: {gp_stat_script}'
assert Path(csv_output).parent.exists(), f'parent directory for ouptut stats not found: {Path(csv_output).parent}'

scanned_blend = []
if Path(csv_output).exists():
    # Get list of aldready scanned blend
    scanned_blend = scanned_file_list(csv_output)
    print('pre scanned blend: ', len(scanned_blend))
else:
    # Get list of scanned blend
    with Path(csv_output).open("w", newline="") as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(
            ['file', 'object', 'layers', 'strokes', 'points', ' avg frames per layer', 'avg strokes per frame', 'avg points per frames', 'nb_materials', 'nb_modifiers']
            )


# Recursively get blends file, when mutliple are versionned in a folder, get last only
blend_files = get_last_files(dir_to_scan, pattern=r'(\d*)(?!.*\d)\.blend$', only_matching=True)

print(f'{len(blend_files)} blends to check')


for blend in blend_files:
    if Path(blend).stem in scanned_blend:
        # avoid double scan (in case of rescan after crash, or scanning an upper directory)
        print('SKIP', blend)
        continue
    
    print('-', blend)
    cmd = [bin, '--background', '--factory-startup', blend, '--python', gp_stat_script, '--', '-o', csv_output, '-anon', str(anonymous)]
    subprocess.call(cmd)