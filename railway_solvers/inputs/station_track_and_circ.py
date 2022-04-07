"""
  test station track and circulation

  station [ A ]

  swith - c

  tracks - ......

                                  < -- 1
  .............................................
                                                .
  .. 0 -> ........................................   0  <--->  1  ...
     2 ->                                                [ B ]
   [ A  ]


  """

taus = {"pass": {"0_A_B": 4, "1_B_A": 4, "2_A_B": 4},
      "stop": {"0_B": 0, "1_A": 1, "2_B": 1}, "res": 1,
      "headway": {"0_2_A_B": 2, "2_0_A_B": 2},"prep": {"1_B": 10}}
timetable = {"tau": taus,
           "initial_conditions": {"0_A": 1, "1_B": 2, "2_A": 2},
           "penalty_weights": {"0_A": 1., "1_B": 1., "2_A": 1.}}

train_sets = {
  "Paths": {0: ["A", "B"], 1: ["B", "A"], 2: ["A", "B"]},
  "J": [0, 1, 2],
  "Jd": {"A": {"B": [[0, 2]]}, "B": {"A": [[1]]}},
  "Jtrack": {"B": [[0,1,2]]},
  "Jswitch": dict(),
  "Josingle": dict(),
  "Jround": {"B": [[0,1]]}
}


d_max = 20
