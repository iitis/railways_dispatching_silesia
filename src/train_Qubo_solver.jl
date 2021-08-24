using Distributed
using LightGraphs
using NPZ

using SpinGlassMetropolisHastings

import SpinGlassMetropolisHastings: read_trains_qubos, Mat_qubo2ising, ising2bin


addprocs(19)
println("number of workers = ", nworkers())
eval(Expr(:toplevel, :(@everywhere using SpinGlassMetropolisHastings)))

p = MH_parameters(2.5)

Qs = ["Qfile.npz", "Qfile_r.npz"]
solutions = ["solution.npz", "solution_r.npz"]

for i in 1:2
    x = npzread(Qs[i]);



    Q = x["Q"]

    #display(Q[1:4, 1:4])

    println("Q mat size", size(Q))

    JJ = Mat_qubo2ising(Q);
    ig = M2graph(JJ; sgn = -1)

    t = 100_000

    @time sol = mh_solve(ig, p, t, sort = true);

    println("minimal energy", sol.energies[1])
    npzwrite(solutions[i] , sol.states[1])

end
