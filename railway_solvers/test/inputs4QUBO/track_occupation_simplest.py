"""
Test single track at station and swithes constrain, switches simplified

stations [A]

swith - c

tracks - ......


                                                  .
  1 ->                                          .
 0 ->                                         .
..........................................  c  .0-> ..  1->.....
 [ A ]                                           [  B  ]

                                simplifies swith condition at B

"""

taus = {"pass": {"0_A_B": 4, "1_A_B": 4},
        "stop": {"0_B": 1, "1_B": 1}, "res": 2}
timetable = {"tau": taus,
             "initial_conditions": {"0_A": 1, "1_A": 1},
             "penalty_weights": {"0_A": 2, "1_A": 0.5}}

train_sets = {
    "Paths": {0: ["A", "B"], 1: ["A", "B"]},
    "J": [0, 1],
    "Jd": {},
    "Josingle": {},
    "Jround": {},
    "Jtrack": {"B": [[0, 1]]},
    "Jswitch": {"B": [{0:"in", 1:"in"}, {0:"out", 1:"out"}]}
}

d_max = 10
