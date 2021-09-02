
#unavoidable delay on train 1 tU(j1, s1out), train 2 tU(j2, s1out), and train 3 tU(j3, s2out) (on station 2).

# model input

# proposed renumbering trains j_1 -> 0, j_2 -> 1, j_3 -> 2; stations s_1 -> 0, s_2 -> 1

#######  these are input ##########


# def tau(x = None, train = None, first_station = None, second_station = None):
#     #print(x, train, first_station, second_station)
#     t = -1
#     if x == 'pass' and train == 0 and first_station == 0 and second_station == 1:
#         t = 4
#     elif x == 'pass' and train == 1 and first_station == 0 and second_station == 1:
#         t = 8
#     elif x == 'pass' and train == 2 and first_station == 1 and second_station == 0:
#         t = 8
#     elif x == 'blocks' and train == 0 and first_station == 0 and second_station == 1:
#         t = 2
#     elif x == 'blocks' and train == 1 and first_station == 0 and second_station == 1:
#         t = 2
#     elif x == 'stop' and train == 0 and first_station == 1:
#         t = 1
#     elif x == 'stop' and train == 1 and first_station == 1:
#         t = 1
#     elif x == 'res':
#         t = 1
#     return t


def initial_conditions(train = None, station = None):
    t = -1
    if train == 0 and station == 0:
        t = 4
    elif train == 1 and station == 0:
        t = 1
    elif train == 2 and station == 1:
        t = 8
    return t


def penalty_weights(train = None, station = None):
    w = 0.
    if train == 0 and station == 0:
        w = 2.
    elif train == 1 and station == 0:
        w = 1.
    elif train == 2 and station == 1:
        w = 1.
    return w


##############################



#### just for toy approach
def small_timetable():
    taus = {"pass" : {"0_0_1" : 4, "1_0_1" : 8, "2_1_0" : 8}, "blocks" : {"0_0_1" : 2, "1_0_1" : 2}, "stop": {"0_1_none" : 1, "1_1_none" : 1}, "res": 1}
    input_data = {"tau": taus,
                  "initial_conditions" : {"0_0" : 4, "1_0" : 1, "2_1" : 8},
                  "penalty_weights" : {"0_0" : 2, "1_0" : 1, "2_1" : 1}}
    return input_data


# print(input_data["tau"]["pass"]["0_0_1"])

# input_data = small_timetable()

# for t in [0,1,2]:
#     for s1 in [0,1]:
#         for s2 in [0,1]:
#             if s1 != s2 and t + s2 != 0 and t + s1 != 2 and t + s2 != 3:
#                 print(t,s1,s2)
