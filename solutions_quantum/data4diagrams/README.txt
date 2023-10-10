	    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
	     FIGURES FOR THE EXTENDED VERSION OF THE PAPER

			   Koniorczyk et al.
	    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


Table of Contents
─────────────────

1 What I have so far
.. 1.1 List all train path in a quantum solution
2 Demonstrate space (horizontal) axis
3 Line segments
4 Next step


• WORK IN PROGRESS

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

  *Krzysziek, please verify if this is correct!*

  • The `arrive' and `departure' fields reflect the *modified* train
    paths from the optimization.
  • The *original*, i.e. originally planned train paths are obtained by
    substracting the `secondary_delay' field values in minutes from the
    `arrive' and `departure' fields' contents.
  • The *conflicted* train paths come from the `conflicted_arrive' and
    `conflicted_departure' fields.


2 Demonstrate space (horizontal) axis
═════════════════════════════════════

  ┌────
  │ ./tmp_echo_xaxis_gnuplot.py > tmp.gnuplot
  │ gnuplot tmp.gnuplot
  └────


3 Line segments
═══════════════

  My plan is to draw diagrams for 2 line segments, containing the
  following stations each:

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


4 Next step
═══════════

  • Do the first figures
