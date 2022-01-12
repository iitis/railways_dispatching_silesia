/* A module for solving QUBO problems */

/* Written and converted to GNU MathProg
 * by NASZVADI, Peter and KONIORCZYK, Matyas, 2021-2022.
 * vuk -AT- math.bme.hu, koniorczyk.matyas -AT- wigner.hu
 * during a project supported by the
 * Ministry of Innovation and Technology and the
 * National Research, Development and Innovation Office within the
 * Quantum Information National Laboratory of Hungary */

/* A Quadratic Unconstrained Binary Optimization (QUBO) problem reads
 *
 * min x Q x^T
 *
 * where x is a binary vector and Q is a matrix,
 * c.f.
 * https://en.wikipedia.org/wiki/Quadratic_unconstrained_binary_optimization
 *
 * Such problems are relevant also because they can be also solved
 * with quantum annealers.
 *
 * The Q matrix is assumed to be sparse and is stored in a csv file
 * with the structure
 *
 * i,j,Q_{i,j}
 *
 * The present model implements the linearization of the problem, c.f.
 * Fortet, R., Revue Francaise de Recherche Operationelle 4, pp. 17-26. (1960).
 * and solves the so-obtained MILP.
 *
 * The Q matrix is specified in a CSV file with the header
 *
 * ICOORD,JCOORD,QVALUE
 *
 * where ICOORD and JCOORD are the coordinates (i.e. indices)
 * of the element of Q, and QVALUE is the value of the matrix element.
 *
 * The attached example in qubo.csv comes from
 * Glover, F., Kochenberger, G. & Du, 4OR-Q J Oper Res 17, 335-371. (2019).
 * (Also available as https://arxiv.org/pdf/1811.11538.pdf);
 * a QUBO formulation of a quadratic assignment problem instance
 * in Section 5.4
 *
 * Random examples of such a CSV file can be generated
 * in bash e.g. like this:
 *
 * $ printf '%s\n' ICOORD,JCOORD,QVALUE {1..8},{1..8},$[RANDOM%3-1] | grep -v ',0$' > qubo.csv
 *
 * To invoke the invoke solver to solve the problem with the matrix
 * in the file "qubo.csv", do
 *
 * $ glpsol -m qubo.mod
 *
 * To get the solution for a problem stored in a file named
 * differently from the default "qubo.csv" the following bashism
 * oneliner can be used:
 *
 * $ glpsol -m qubo.mod -d <( echo 'param CSVFILE:="yourCSVfile.csv";' )
 *
 * To change objective sense to maximization
 * from the default minimization, do
 *
 * $ glpsol -m qubo.mod -d <( echo 'param OBJSENSE:=-1;' )
 *
 */

set IJ dimen 2;
/* set the read index pairs; the subset of the cartesian product of
the following K set */

set K := (setof{(i,j) in IJ} i) union (setof{(i,j) in IJ} j);
/* onedimensinal projection and union of all indices */

set WIDX := (setof{(i,j) in IJ: (i<j)} (i,j)) union
            (setof{(i,j) in IJ: (i>j)} (j,i));
/* ordered pairs of off-diagonal nonzero elements */

param OBJSENSE integer >=-1, <=1, != 0, default 1;
/* changing the sign of this parameter changes the model to a
maximization problem instead of the default minimization */

param CSVFILE symbolic default 'qubo.csv';
/* The csv file to read the QUBO matrix from */

param QUBO{(i,j) in IJ};
/* QUBO matrix elements */

table data IN "CSV" CSVFILE: IJ <- [ICOORD,JCOORD], QUBO~QVALUE;
/* reading and processing the CSV file, constructing the
   necessary structures */

var x{i in K}, binary;
/* main variable vector */

var w{(i,j) in WIDX}, >=0;
/* helper variables for all strictly ordered coordinate pairs:
   their value is exactly one iff both x_i and x_j equal to one */

var objvalue;
/* objective value */

s.t. c1{k in K, (i,j) in WIDX: (k==i) or (k==j)}: x[k] >= w[i,j];
/* sets the helper variable to zero if at least one the
   corresponding main variable's coordinate is 0 */

s.t. c2{k in K, l in K, (i,j) in WIDX:
   (k==i) and (l==j)}: x[k] + x[l] <= 1 + w[i,j];
/* forces 1 otherwise */

s.t. objc: (sum{(k,j) in IJ: k==j} (QUBO[k,k] * x[k])) +
   sum{(i,j) in IJ: i!=j} (QUBO[i,j] * w[min(i,j),max(i,j)]) =
   OBJSENSE * objvalue;
/* objective function */

minimize obj: objvalue;
/* Also 'objc' could be used directly instead of 'obj', for
   experimentation, however, it is useful to set up additional
   constraints for introduced objvalue variable */

solve;
/* Pretty printing the nonzero elements of the solution vector x */

printf '\nCSV sparse QUBO solver\n';

printf 'Optimal solution, objective function value is: %s\n\n',
   OBJSENSE * objvalue.val;
for{k in K: x[k].val != 0}{
   printf 'x[%s] = 1\n', k;
   }
printf '\n';

end;
