import numpy as np

important_stations = {


"KO":['"KO", "ST", 9, "(1)"',
'"KO", "ST", 7, "(1)"',
'"KO","ST", 3, "(2)"',
'"KO", "ST", 1, "(2)"',
'"KO", "ST", 2, "(3)"',
'"KO", "ST", 4, "(3)"',
'"KO", "ST", 8, "(4)"',
'"KO", "ST", 10, "(4)"'],


"CB":['"CB", "ST", 1, "(1)"',
'"CB", "ST", 2, "(1)"',
'"CB", "ST", 3, "(2)"',
'"CB", "ST", 4, "(2)"',
'"CB", "ST", 10, "(N/A)"'],

"GLC":['"GLC", "ST", 3, "(1)"',
'"GLC", "ST", 4, "(1)"',
'"GLC", "ST", 5, "(2)"',
'"GLC", "ST", 6, "(2)"',
'"GLC", "ST", 7, "(3)"',
'"GLC", "ST", 8, "(3)"',
'"GLC", "ST", 9, "(4)"',
'"GLC", "ST", 11, "(4)"']
}

aditional_stations = {"RCB":['"RCB", "ST", 1, "(1)"',
'"RCB", "ST", 2, "(1)"'],

"ZZ":['"ZZ", "ST", 1, "(1)"',
'"ZZ", "ST", 2, "(1)"'],
# branch junctions:

# KTC (for trains going KO -> CB):
"KTC":['"KTC-KO-1", "SBL+PO(Załęże)", 2, "1", "(2)"',
'"KO-KTC-2", "SBL+POGP", 1, "2", "(2)"']
}
np.savez('important_stations_KO_GLC',important_stations)


npzfile = np.load('important_stations_KO_GLC.npz')
print(npzfile.files)
