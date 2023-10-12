#!/bin/sh


#Please plot
#
#- case 4  138139KZTTY:
#     - ILP
#     - cqm realisation 1
#     - cqm realisation 2

#We have additional disturbances caused by non-perfect cqm. We can see
#these for various trains given various cases.
#Such quantum approach may be the generator of disturbances for
#stochastic scheduling.
#
#- case 7   137138GLYKZ:
#     -ILP,
#     -cqm realisation 1
#     -cqm realisation 2

touch tmp.gnuplot
rm tmp.gnuplot

#-----------------------------------------
./echo_gnuplot_file.py PULP_CBC_CMD_case4_Integer.pkl \
		       --segment 138139KZTY \
		       --epsfile figures_for_paper/case4_138139KZTY_ILP_color.eps \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot

./echo_gnuplot_file.py PULP_CBC_CMD_case4_Integer.pkl \
		       --segment 138139KZTY \
		       --epsfile figures_for_paper/case4_138139KZTY_ILP_bw.eps \
		       --epsbw \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot
#-----------------------------------------

#-----------------------------------------
./echo_gnuplot_file.py cqm5_case4_Integer.pkl \
		       --realisation 1 \
		       --segment 138139KZTY \
		       --epsfile figures_for_paper/case4_138139KZTY_cqm5_realisation1_color.eps \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot

./echo_gnuplot_file.py cqm5_case4_Integer.pkl \
		       --realisation 1 \
		       --segment 138139KZTY \
		       --epsfile figures_for_paper/case4_138139KZTY_cqm5_realisation_1_bw.eps \
		       --epsbw \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot
#-----------------------------------------

./echo_gnuplot_file.py cqm5_case4_Integer.pkl \
		       --realisation 2 \
		       --segment 138139KZTY \
		       --epsfile figures_for_paper/case4_138139KZTY_cqm5_realisation2_color.eps \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot

./echo_gnuplot_file.py cqm5_case4_Integer.pkl \
		       --realisation 2 \
		       --segment 138139KZTY \
		       --epsfile figures_for_paper/case4_138139KZTY_cqm5_realisation_2_bw.eps \
		       --epsbw \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot
#-----------------------------------------
#---------------------------------------------------------------case7
./echo_gnuplot_file.py PULP_CBC_CMD_case7_Integer.pkl \
		       --segment 137138GLYKZ \
		       --epsfile figures_for_paper/case7_137138GLYKZ_ILP_color.eps \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot

./echo_gnuplot_file.py PULP_CBC_CMD_case7_Integer.pkl \
		       --segment 137138GLYKZ \
		       --epsfile figures_for_paper/case7_137138GLYKZ_ILP_bw.eps \
		       --epsbw \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot
#-----------------------------------------

#-----------------------------------------
./echo_gnuplot_file.py cqm5_case7_Integer.pkl \
		       --realisation 1 \
		       --segment 137138GLYKZ \
		       --epsfile figures_for_paper/case7_137138GLYKZ_cqm5_realisation1_color.eps \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot

./echo_gnuplot_file.py cqm5_case7_Integer.pkl \
		       --realisation 1 \
		       --segment 137138GLYKZ \
		       --epsfile figures_for_paper/case7_137138GLYKZ_cqm5_realisation_1_bw.eps \
		       --epsbw \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot
#-----------------------------------------

./echo_gnuplot_file.py cqm5_case7_Integer.pkl \
		       --realisation 2 \
		       --segment 137138GLYKZ \
		       --epsfile figures_for_paper/case7_137138GLYKZ_cqm5_realisation2_color.eps \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot

./echo_gnuplot_file.py cqm5_case7_Integer.pkl \
		       --realisation 2 \
		       --segment 137138GLYKZ \
		       --epsfile figures_for_paper/case7_137138GLYKZ_cqm5_realisation_2_bw.eps \
		       --epsbw \
		       > tmp.gnuplot
gnuplot ./tmp.gnuplot
touch tmp.gnuplot
rm tmp.gnuplot

cd figures_for_paper
for i in *.eps;do
    epspdf $i 
done
cd ..
