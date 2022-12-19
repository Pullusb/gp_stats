# Grease Pencil Stats

Python script - Export GP statistic from blend files.

<!-- Download latest -->

---

## description

Scan folder recursively, open found blends and write GP indos in a csv file.

If some subfolders contains multiple versionned blend only last one with be taken.

Outputed csv file has one row per object with following infos:

file, object, number of layers, number of strokes, number of points,  
average frames per layer, average strokes per frame, average points per frames,  
nb_materials, nb_modifiers  


## How to use

> /!\ it is recommanded to test with a folder containing few non-important files first !

Use script `list_blends_and_get_gp_stats.py`

look for variables wrapped with `-- INFO ---` at the bottom of this script and change as needed:

- `bin` : should point to blender executable (you can replace with `"blender"` if it's in PATH)

- `dir_to_scan` : The directory to scan recusrsively

- `csv_output` : Output of `stats.csv` file (by defaut, should be created aside scripts)

- `anonymous` : if passed to `True`, two first row (filename and object name) will be ommitted in output stat.  
Note: `False` is default and recommanded, as it avoid rescanning same blends twice if data was already stored

- `gp_stat_script` : path to the scripts to execute on blend (this should not be changed except if there is an error)


Execute the script in console or editor of your choice.


## Bonus: Good VScode extension to look at CSV files:

- [Rainbow CSV](https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv)

- [Excel Viewer](https://marketplace.visualstudio.com/items?itemName=GrapeCity.gc-excelviewer)

<!-- ## TODO

Might be interesting to separate line and fills material in count
 -> get an average line VS average Fills

-->