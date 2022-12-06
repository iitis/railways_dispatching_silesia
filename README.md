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
</li><a href="#sec-2">2. Main directory</a>
</ul>
</div>
</div>


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

There are pickles files containing results of D-Wave solutions via:
- simulations, 
- real annelaing,
- hybrid solvers

## Main directory<a id="sec-2" name="sec-2"></a>
The module ```solve_real_problem.py``` is used to solve real problem of railway dispatching.
Input:
```
--stations path to '''npz''' file of important stations (dict Important_station: list of blocks),
--p path to '''.ods''' file with all paths and passing times that can be realized on the network,
--load path to dataframe dictionary of trains timetable
--case it is particular case of railway dispatching problems
--category ("Integer" or "Continious") the category of time variables "Integer" yields ILP "Continious" yields MLP
--solve_lp   chose PuLp solver, e.g. 'PULP_CBC_CMD'  'GUROBI_CMD' 'CPLEX_CMD'"  
--solve_quantum   chose quantum or quantum inspired solver, "sim" - D-Wave simulation, "real" - D-Wave, "hyb" - D-Wave hybrid from QUBO, "cqm" - D-Wave hybrid cqm, "save_qubo" just save qubo to ./qubos
    build - subparser used to build the dataframes dictionary of train timetable with argument:
    -d path to '''.csv''' train dictionary if used without other arguments --load is not required
    -save - path to location where dataframe dictionary will be saved.
```
Output:

The script solves the problem via linear programming, D-Wave quantum, hybrid or simulator or saves qubo file to ```qubos``` directory. Solutions
of quantum approach (i.e. by -solve_quantum) are saved in ```solutions_quantum``` subdirectory as pikle files. Solutions of linear programming apprach are only printed.


Example use:

- linear programming
```
python solve_real_problem.py --stations data/important_stations.npz --case 0 --category Integer --solve_lp PULP_CBC_CMD --paths data/network_paths.ods build -d data/trains_schedules.csv
```
- quantum approach
```
python solve_real_problem.py --stations data/important_stations.npz --case 0 --category Integer --solve_quantum cqm --paths data/network_paths.ods build -d data/trains_schedules.csv
```

Case ```0``` or case ```6``` means no dosturptions. Then disturtions grow with cases number from case ```1``` to case ```5```. Disturbtions of case ```7``` ```8``` and ```9``` are the same as these of case ```5```.

#### Examples with rerouting

For accident cases, where trains are rerouted on the single track line ```KTC``` -  ```Gt``` - ```CB``` use following initial (conflicted) schedule in input file  ```data/trains_schedules_Gt.csv``` and the altered important station path in ``` data/important_stations_Gt.npz```. 
Please run:

```
python solve_real_problem.py --stations data/important_stations_Gt.npz --paths data/network_paths.ods --case 7 --category Integer --solve_lp PULP_CBC_CMD  build -d data/trains_schedules_Gt.csv
```


For cases with single track line between ```KZ``` - ```KO``` - ```KL``` - ```Ty``` use following (conflicted) schedule in ```data/trains_schedules_1track.csv``` and original important station path ```data/important_stations.npz```


```python solve_real_problem.py --stations data/important_stations.npz --case 8 --category Integer --solve_lp PULP_CBC_CMD  --paths data/network_paths.ods build -d data/trains_schedules_1track.csv
```

Here cases ```6``` and ```8``` are with no itinatial disturbtions, but cases ```7``` and ```9``` are with heavy disturptions as in case ```5```. 

The most dificult case is the merge of single track line between ```KZ``` - ```KO``` - ```KL``` - ```Ty``` the single track line ```KTC``` -  ```Gt``` - ```CB```. Then the initial (conflicted) schedule is in ```data/trains_schedules_1track_Gt.csv``` and the important station path is in ``` data/important_stations_Gt.npz```. Please run:

```
python solve_real_problem.py --stations data/important_stations_Gt.npz --case 9 --category Integer --solve_lp PULP_CBC_CMD  --paths data/network_paths.ods build -d data/trains_schedules_1track_Gt.csv

```


#### Simple comparison example.

The module:
```
wisla_problems.py 
```
is the test module for the problem in Krzysztof Domino, Mátyás Koniorczyk, Krzysztof Krawiec, Konrad Jałowiecki, Sebastian Deffner, Bartłomiej Gardas
Quantum annealing in the NISQ era: railway conflict management [arXiv preprint arXiv:2112.03674](https://arxiv.org/abs/2112.03674).
Case 1 therein is used.

Input:
```
--solve_lp   chose PuLp solver, e.g. 'PULP_CBC_CMD'  'GUROBI_CMD' 'CPLEX_CMD'"  
--solve_quantum   chose quantum or quantum inspired solver, "sim" - D-Wave simulation, "real" - D-Wave, "hyb" - D-Wave hybrid from QUBO, "cqm" - D-Wave hybrid cqm, "save_qubo" just save qubo to ./
```

Output, as before.

Example use:

- linear programming
```
python wisla_problems.py --solve_lp PULP_CBC_CMD
```
- quantum approach
```
python wisla_problems.py --solve_quantum real
```
