using Distributed
using LightGraphs
using NPZ

using SpinGlassMetropolisHastings

import SpinGlassMetropolisHastings: read_trains_qubos, Mat_qubo2ising, ising2bin


addprocs(19)
println("number of workers = ", nworkers())
eval(Expr(:toplevel, :(@everywhere using SpinGlassMetropolisHastings)))

p = MH_parameters(2.)

Qs = ["files/Qfile.npz", "files/Qfile_r.npz"]
solutions = ["files/solution.npz", "files/solution_r.npz"]

for i in 1:2
    x = npzread(Qs[i]);



    Q = x["Q"]

    println("Q mat size", size(Q))

    JJ = Mat_qubo2ising(Q);
    ig = M2graph(JJ; sgn = -1)

    t = 300

    @time sol = mh_solve(ig, p, t, sort = true);

    println("minimal energy", sol.energies[1])
    npzwrite(solutions[i] , sol.states[1])

end
