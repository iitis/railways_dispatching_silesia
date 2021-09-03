
#unavoidable delay on train 1 tU(j1, s1out), train 2 tU(j2, s1out), and train 3 tU(j3, s2out) (on station 2).

# model input

# proposed renumbering trains j_1 -> 0, j_2 -> 1, j_3 -> 2; stations s_1 -> 0, s_2 -> 1

#######  these are input ##########



#### for toy approach
def small_timetable():
    taus = {"pass" : {"0_0_1" : 4, "1_0_1" : 8, "2_1_0" : 8}, "blocks" : {"0_0_1" : 2, "1_0_1" : 2}, "stop": {"0_1_None" : 1, "1_1_None" : 1}, "res": 1}
    input_data = {"tau": taus,
                  "initial_conditions" : {"0_0" : 4, "1_0" : 1, "2_1" : 8},
                  "penalty_weights" : {"0_0" : 2, "1_0" : 1, "2_1" : 1}}
    return input_data
