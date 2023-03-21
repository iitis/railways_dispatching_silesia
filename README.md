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

There are following railway dispatching problems.

#### real railway problem

The module ```solve_real_problem.py``` is used to solve real problem of railway dispatching on the core of Silesian railway network.
The script solves the problem via classical linear programming, D-Wave quantum approach, D-Wave hybrid or simulation approach.

Input:

```
--case  particular case of railway dispatching problem (0 to 9 is supported, default 1)
--category the category of time variables "Integer" yields ILP problem "Continious" yields MLP problem (default "Integer")
--solve_lp  chose PuLp solver, e.g. 'PULP_CBC_CMD'  'GUROBI_CMD' 'CPLEX_CMD'"  
--solve_quantum   chose quantum or quantum inspired solver, "sim" - D-Wave simulation, "real" - D-Wave QPU, "hyb" - D-Wave hybrid bqm solver, "cqm" - D-Wave hybrid cqm solver
--min_t minimal time parameter for D-Wave hybrid solver in (rescalled) seconds (5 default)
--runs number of experiments (runs in the quantum case)
```


Output:

Solutions of quantum D-Wave approach (i.e. quantum, hybrid or simulation via ```--solve_quantum```) are saved in ```solutions_quantum``` subdirectory as pickle files. Solutions of linear programming approach are printed.


Example use:

- classical programming

```python solve_real_problem.py --case 0 --category Integer --solve_lp PULP_CBC_CMD ```

- D-Wave quantum or hybrid approach

```python solve_real_problem.py --case 0 --category Integer --solve_quantum cqm --min_t 5 -- runs 5```

Difficulty of dispatching problem grows with the case number. Case ```0```, no disturbances. In Cases ```1``` to ```3``` some trains are delayed, but they follow their original routes. Cases ```4``` to ```9``` concerns also a priory changes trains' routes e.g. due to some track failure.


#### Generic problem

The generic example concerns dense passenger traffic (generic) on the KO-GLC part of the Silesian railway network. For each case there are ```12``` instances of various delays of trains at start.

Input:

```
--case  particular case of railway dispatching problem (1 to 3 is supported)
--category the category of time variables "Integer" yields ILP problem "Continious" yields MLP problem (default "Integer")
--solve_lp  chose PuLp solver, e.g. 'PULP_CBC_CMD'  'GUROBI_CMD' 'CPLEX_CMD'"  
--solve_quantum   chose quantum or quantum inspired solver, "sim" - D-Wave simulation, "real" - D-Wave QPU, "hyb" - D-Wave hybrid bqm solver, "cqm" - D-Wave hybrid cqm solver
--min_t minimal time parameter for D-Wave hybrid solver in seconds (5 default)
```

Particular description of cases:

- case ```1```, there are no disruptions inside the analysed (double track) line, and we use cyclic timetable of ```3``` hours i.e. with ```59``` trains, particular instances concern delays of various trains at start;
- case ```2```, we assume that one track between ```RCB``` and ```ZZ``` is closed, hence the line becomes partially single track and additional  we use cyclic timetable of ```2``` hours i.e. with ```40``` trains, particular instances concern delays of various trains at start;
- case  ```3```, line is analysed as hypothetical single track line of ```3``` hours and ```21`` trains, particular instances concern delays of various trains at start.

Output:

Solutions of quantum and classical approaches are saved in ```results_KO_GLC``` subdirectory as pickle files. 

In ```results_KO_GLC``` there is the plotting script ```fast_plot.py```

Example use:

- clasical programming

```python3 solve_KO_GLC_problems.py --solve_lp PULP_CBC_CMD   --case 1 --category Integer```

- D-Wave quantum or hybrid approach

```python3 solve_KO_GLC_problems.py --solve_quantum cqm   --case 1 --category Integer --min_t 5```




#### Problem from "Quantum Annealing in the NISQ Era: Railway Conflict Management"
K. Domino, M. Koniorczyk,K. Krawiec, K. Jałowiecki, S. Deffner, B. Gardas [Entropy 2023, 25, 191.](https://doi.org/10.3390/e25020191)

The module:
```
wisla_problems.py 
```
is the test module for for case ```1``` problem from mentioned work.

Input:
```
--solve_lp  chose PuLp solver, e.g. 'PULP_CBC_CMD'  'GUROBI_CMD' 'CPLEX_CMD'"  
--solve_quantum   chose quantum or quantum inspired solver, "sim" - D-Wave simulation, "real" - D-Wave, "hyb" - D-Wave hybrid from QUBO, "cqm" - D-Wave hybrid cqm
--min_t minimal time parameter for D-Wave hybrid solver in seconds (5 default)
```


Output

Solutions of quantum approach (i.e. by -solve_quantum) are saved in ```solutions_quantum/wisla``` subdirectory as pikle files. Solutions of linear programming apprach are  printed.

Example use:

- linear programming

```python wisla_problems.py --solve_lp PULP_CBC_CMD```

- D-Wave quantum approach

```python wisla_problems.py --solve_quantum real```

- D-Wave hybrid (cqm) approach

```python wisla_problems.py --solve_quantum cqm --min_t 5```





