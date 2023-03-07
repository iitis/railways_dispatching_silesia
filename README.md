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

#### Close to real life problem

The module ```solve_real_problem.py``` is used to solve real problem of railway dispatching.
Input:
```

--case it is particular case of railway dispatching problems
--category ("Integer" or "Continious") the category of time variables "Integer" yields ILP "Continious" yields MLP
--solve_lp   chose PuLp solver, e.g. 'PULP_CBC_CMD'  'GUROBI_CMD' 'CPLEX_CMD'"  
--solve_quantum   chose quantum or quantum inspired solver, "sim" - D-Wave simulation, "real" - D-Wave, "hyb" - D-Wave hybrid from QUBO, "cqm" - D-Wave hybrid cqm
--min_t minimal time parameter for hybrid solver in seconds (5 be default)
```
Output:

The script solves the problem via linear programming, D-Wave quantum, hybrid or simulator. Solutions
of quantum approach (i.e. by -solve_quantum) are saved in ```solutions_quantum``` subdirectory as pikle files. Solutions of linear programming apprach are only printed.


Example use:

- linear programming
```
python solve_real_problem.py --case 0 --category Integer --solve_lp PULP_CBC_CMD 
```
- quantum approach
```
python solve_real_problem.py --case 0 --category Integer --solve_quantum cqm --min_t 5
```

Dificulty grows with cases number. Cases ```1``` to case ```5``` only trains delays without rerouting. Cases ```6``` to ```9``` concers rerouting due to 
some track failure.


#### Generic problem

Here the part of the railway line i.e. KO - GLC is analysed. For each case there are '''12''' instances of various delays of trains at the beginning of their routes. 

- In case ```1``` delay_and_acctual_time there are no disruptions inside the line, and we use cyclic timetable of ```3``` hours i.e. with ```60``` trains. 
- In case ```2``` we assume one track between ```RCB``` and ```ZZ``` is closed, hence the line becomes partially ```1``` track and additional disruptions are as in case ```1``` we use cyclic timetable of ```2``` hours i.e. with ```40``` trains.
- In case  ```3``` we have a hypothetical single track traffic with feasible timetable of ```3``` hours with ```21`` trains.

Clasical 

```python3 solve_KO_GLC_problems.py --solve_lp PULP_CBC_CMD   --case 1 --category Integer```


Quantum (hybrid)

```python3 solve_KO_GLC_problems.py --solve_quantum cqm   --case 1 --category Integer --min_t 5```

#### Simple comparison example.

The module:
```
wisla_problems.py 
```
is the test module for the problem in K. Domino, M. Koniorczyk,K. Krawiec, K. Jałowiecki, S. Deffner, B. Gardas
"Quantum Annealing in the NISQ Era: Railway
Conflict Management" [Entropy 2023, 25, 191.](https://doi.org/10.3390/e25020191).
We demonstrate implementationf for case ```1``` from this work.

Input:
```
--solve_lp   chose PuLp solver, e.g. 'PULP_CBC_CMD'  'GUROBI_CMD' 'CPLEX_CMD'"  
--solve_quantum   chose quantum or quantum inspired solver, "sim" - D-Wave simulation, "real" - D-Wave, "hyb" - D-Wave hybrid from QUBO, "cqm" - D-Wave hybrid cqm
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

- hybrid approach
```
python wisla_problems.py --solve_quantum cqm --t_min 5
```
