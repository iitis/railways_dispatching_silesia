"""
  Test single track at station and swithes constrain, switches simplified

  station [ A ]

  swith - c

  tracks - ......

                                                                                                   .
                       .............................
                      .                              .
  1 -> .. 0 -> ....  c ..............................  c  . 1 -> . ......
                                                         .
                                                           . ... 0 -> ...
          [ A  ]                                               [ B ]



  """

taus = {"pass": {"0_A_B": 6, "1_A_B": 2}, "stop": {"0_B": 1, "1_B": 1}, "res": 1}
timetable = {"tau": taus,
             "initial_conditions": {"0_A": 1, "1_A": 5},
             "penalty_weights": {"0_B": 1., "1_B": 2.}}

train_sets = {
      "Paths": {0: ["A", "B"], 1: ["A", "B"]},
      "J": [0, 1],
      "Jd": {"A":{"B": [[0], [1]]}},
      "Josingle": dict(),
      "Jround": dict(),
      "Jtrack": {"A": [[0, 1]]},
      "Jswitch": {"A": [{0:"out", 1:"out"}], "B": [{0:"in", 1:"in"}]}
}

d_max = 5
