using Distributed
using LightGraphs
using NPZ

using SpinGlassMetropolisHastings

import SpinGlassMetropolisHastings: read_trains_qubos, Mat_qubo2ising, ising2bin


addprocs(15)
println("number of workers = ", nworkers())
eval(Expr(:toplevel, :(@everywhere using SpinGlassMetropolisHastings)))

p = MH_parameters(3.)


x = npzread("Qfile.npz");

Q = x["Q"]

JJ = Mat_qubo2ising(Q);
ig = M2graph(JJ; sgn = -1)

t = 100_000

sol = mh_solve(ig, p, t, sort = true);


npzwrite("solution.npz", sol.states[1])
