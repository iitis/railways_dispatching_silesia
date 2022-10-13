<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#sec-1">1. Files</a>
<ul>
<li><a href="#sec-1-1">1.1. <code>data</code> subdirectory</a></li>
<li><a href="#sec-1-2">1.2. <code>data_formatting</code> subdirectory</a></li>
<li><a href="#sec-1-3">1.3. <code>railway_solvers</code> subdirectory</a></li>
</ul>
</li>
</ul>
</div>
</div>

This is just a brief, incomplete README with minor notes. To be
extended.

Please edit the org which is in [Emacs org markup](https://orgmode.org/guide/Markup.html). The md5 will be
generated from that.

# Files<a id="sec-1" name="sec-1"></a>

## `data` subdirectory<a id="sec-1-1" name="sec-1-1"></a>

These are the raw input data.

## `data_formatting` subdirectory<a id="sec-1-2" name="sec-1-2"></a>

Scripts to parse the input data and generate inputs in the required
format.


A test can be run like that:

    python3 -m pytest

in this directory. The `data_formatting` subdirectory (same name as
its parent) is the parser module.

## `railway_solvers` subdirectory<a id="sec-1-3" name="sec-1-3"></a>

These are the actual solvers. A test can be run like that:

    python3 -m pytest

in this directory. The `railway_solvers` subdirectory (same name as
its parent) is the solver module.

## main directory ##
The module '''solve_real_problem.py''' is used to solve real problem of railway dispatching.
Input:
```
    --stations path to '''npz''' file of important stations (dict Important_station: list of blocks),
    --p path to '''.ods''' file with all paths and passing times that can be realized on the network,
    --load path to dataframe dictionary of trains timetable
    --case it is particular case of railway dispatching problems
        build - subparser used to build the dataframes dictionary of train timetable with argument:
        -d path to '''.csv''' train dictionary if used without other arguments --load is not required
        -save - path to location where dataframe dictionary will be saved.
```


Example use:

```
python solve_real_problem.py --stations data/important_stations.npz --paths data/network_paths.ods build -d data/trains_schedules.csv

```


Ongoing work.
