	    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
	     FIGURES FOR THE EXTENDED VERSION OF THE PAPER

			   Koniorczyk et al.
	    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


Table of Contents
─────────────────

1 What I have so far
.. 1.1 List all train path in a quantum solution
2 Line segments
3 Figures
4 Next step


• WORK IN PROGRESS, v 0.3

• DO NOT EDIT README.txt, it is for compatibility.  The README is
  README.org


1 What I have so far
════════════════════

1.1 List all train path in a quantum solution
─────────────────────────────────────────────

  e.g. realisation 1 in `cqm5_case3_Integer.pkl'

  ┌────
  │ ./read_quantum_pickle.py cqm5_case3_Integer.pkl 1
  └────

  Assumptions:

  • The `arrive' and `departure' fields reflect the *resolved* train
    paths from the optimization.
  • The *conflicted* train paths come from the `conflicted_arrive' and
    `conflicted_departure' fields.
  • The original timetables are still to be added


2 Line segments
═══════════════

  Railway line segments are defined in `railway_lines.py'. (There is a
  variable for railway lines, but we rather use segments which are ad
  hoc sequences of stations.) New ones can be defined by adding them
  properly to the `RAILWAYSEGMENTS' dictionary.

  The current plan is to draw diagrams for 2 line segments, containing
  the following stations each:

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GLC      Gliwice                   
   ZZ       Zabrze                    
   RŚl      Ruda Śląska               
   RCB      Ruda Chebzie              
            Świętochłowice            
   CB       Chorzów Batory            
   KTC      Katowice Towarowa KTC     
   KO       Katowice                  
   KO(STM)  Katowice Stacja Manewrowa 
   KZ       Katowice Zawodzie         
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  and

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   KZ       Katowice Zawodzie         
   KO(STM)  Katowice Stacja Manewrowa 
   KO       Katowice                  
   Bry      Katowice Brynów           
   KL       Katowice Ligota           
   KtP      Katowice Piotrowice       
            Katowice Podlesie         
   Mc       Mąkołowiec                
   Ty       Tychy                     
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  In the two figures, only the part of the train paths fitting to these
  segments will appear.


3 Figures
═════════

  Figures can be produced as follows:
  ┌────
  │ ./echo_gnuplot_file.py cqm5_case5_Integer.pkl --segment 138139KZTY --realisation 2 > tmp.gnuplot
  └────
  The positional argument is the input file (classical or quantum),
  `--segment' is line segment (the currently meaningful ones are:
  `137138GLYKZ' (default), and `138139KZTY'.  In case of quantum files,
  `--realisation' is the sample number, defaults to 1 if not
  specified. The script outputs a gnuplot script, which can be displayed
  with gnuplot like this:
  ┌────
  │ gnuplot script.gnuplot
  └────

  The trains are filtered for the segment (to be documented). It is
  possible to provide a list of trains that are displayed even if the
  filter would not select them with the `--fixedtrains' option, e.g.

  ┌────
  │ ./echo_gnuplot_file.py PULP_CBC_CMD_case3_Integer.pkl --segment 138139KZTY --fixedtrains="44862,44717" > script.gnuplot
  └────

  See also
  ┌────
  │ ./echo_gnuplot_file.py --help
  └────

  The current version is for displaying; there will be a version
  producing publication-quality vector pdfs.


4 Next step
═══════════

  • Add train numbers to paths (in progress, to be improved)
  • Fine-tune conflicted-resolved figures (bw version to be made)
  • Choose the right figures (in progress)
  • Create vector pdf figures.
  • Add orignal timetables (postponed)
