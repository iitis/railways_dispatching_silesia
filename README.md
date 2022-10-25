<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#sec-1">1. Files</a>
<ul>
<li><a href="#sec-1-1">1.1. <code>data</code> subdirectory</a></li>
<li><a href="#sec-1-2">1.2. <code>data_formatting</code> subdirectory</a></li>
<li><a href="#sec-1-3">1.3. <code>railway_solvers</code> subdirectory</a></li>
<li><a href="#sec-1-4">1.4. <code>qubos</code> subdirectory</a></li>
<li><a href="#sec-1-4">1.5. <code>solutions</code> subdirectory</a></li>
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


## `qubos` subdirectory<a id="sec-1-4" name="sec-1-4"></a>

There are pickles files containing QUBOs for particuler use cases. 

## `solutions` subdirectory<a id="sec-1-5" name="sec-1-5"></a>

Results from D-Wave simulations, real annelaing, and hybrid solvers are stored there.

## main directory ##
The module '''solve_real_problem.py''' is used to solve real problem of railway dispatching.
Input:
```
    --stations path to '''npz''' file of important stations (dict Important_station: list of blocks),
    --p path to '''.ods''' file with all paths and passing times that can be realized on the network,
    --load path to dataframe dictionary of trains timetable
    --case it is particular case of railway dispatching problems
    --category ("Integer" or "Continious") the category of time variables "Integer" yields ILP "Continious" yields MLP
    --solve  ("lp" - linear programming, "sim" - D-Wave simulation, "real" - D-Wave, "bqm" - D-Wave hybrid bqm, "cqm" - D-Wave hybrid cqm, "save_qubo" just save qubo to ```./qubos```)
        build - subparser used to build the dataframes dictionary of train timetable with argument:
        -d path to '''.csv''' train dictionary if used without other arguments --load is not required
        -save - path to location where dataframe dictionary will be saved.
```


The script solves the problem via linear programming, D-Wave quantum, hybrid or simulator or savers the qubo

Example use:

```
python solve_real_problem.py --stations data/important_stations.npz --paths data/network_paths.ods build -d data/trains_schedules.csv

```

For rerouted ```Gt``` example please run:

```
python solve_real_problem.py --stations data/important_stations_Gt.npz --paths data/network_paths.ods --case 6 --category Integer  build -d data/trains_schedules_Gt.csv
```

