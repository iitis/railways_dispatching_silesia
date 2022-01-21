import numpy as np

important_stations = {

"KZ":['"KZ", "ST", 1, "(1)"',
'"KZ", "ST", 2, "(1)"',
'"KZ", "ST", 3, "(2)"',
'"KZ", "ST", 4, "(2)"'],

"KO":['"KO", "ST", 9, "(1)"',
'"KO", "ST", 7, "(1)"',
'"KO","ST", 3, "(2)"',
'"KO", "ST", 1, "(2)"',
'"KO", "ST", 2, "(3)"',
'"KO", "ST", 4, "(3)"',
'"KO", "ST", 8, "(4)"',
'"KO", "ST", 10, "(4)"'],

'KO(STM)':['"KO", "ST", 117, "(N/A)"',
'"KO", "ST", 115, "(N/A)"',
'"KO", "ST", 113, "(N/A)"',
'"KO", "ST", 118, "(N/A)"',
'"KO", "ST", 116, "(N/A)"',
'"KO", "ST", 114, "(N/A)"',
'"KO", "ST-M", 1114, "(N/A)"',
'"KO", "ST-M", 1113, "(N/A)"',
'"KO", "ST-M", 1118, "(N/A)"',
'"KO", "ST", 120, "(5)"'],

"KO(KS)":['"Rac(KS)", "B-M", 200, "(N/A)"'],

"KO(IC)":['"KO(IC)", "B-M", 500, "(N/A)"'],

"CB":['"CB", "ST", 1, "(1)"',
'"CB", "ST", 2, "(1)"',
'"CB", "ST", 3, "(2)"',
'"CB", "ST", 4, "(2)"'],

"GLC":['"GLC", "ST", 3, "(1)"',
'"GLC", "ST", 4, "(1)"',
'"GLC", "ST", 5, "(2)"',
'"GLC", "ST", 6, "(2)"',
'"GLC", "ST", 7, "(3)"',
'"GLC", "ST", 8, "(3)"',
'"GLC", "ST", 9, "(4)"',
'"GLC", "ST", 11, "(4)"'],

"CM":['"CM", "ST", 1, "(1)"',
'"CM", "ST", 2, "(1)"'],

"KL":['"KL", "ST", 1, "(2)"',
'"KL", "ST", 2, "(2)"',
'"KL", "ST", 3, "(1)"'],

"Ty":['"Ty", "ST", 1, "(2)"',
'"Ty", "ST", 2, "(2)"',
'"Ty", "ST", 8, "(1)"',
'"Ty", "ST", 7, "(3)"',
'"Ty", "ST", 9, "(3)"'],

"Mi":['"Mi", "ST", 1, "(2)"',
'"Mi", "ST", 2, "(1)"'],

"MJ":['"MJ", "ST", 2, "(1)"',
'"MJ", "ST", 1, "(1)"']
}

aditional_stations = {"RCB":['"RCB", "ST", 1, "(1)"',
'"RCB", "ST", 2, "(1)"'],

"ZZ":['"ZZ", "ST", 1, "(1)"',
'"ZZ", "ST", 2, "(1)"'],
# branch junctions:
# Mc for trains going KL-> Ty
"Mc":['"Mc", "PODG", 1, "(N/A)"',
'"Mc", "PODG", 2, "(N/A)"',
'"Mc", "PODG", 3, "(N/A)"'],

# KTC (for trains going KO -> CB):
"KTC":['"KTC-KO-1", "SBL+PO(Załęże)", 2, "1", "(2)"',
'"KO-KTC-2", "SBL+POGP", 1, "2", "(2)"'],
# Bry (for trains going KL -> KO):
"Bry":['"KL-Bry-2", "SBL+Sem(PODG)", 2, "2", "(2)"',
'"Bry-KL-1", "SBL+POGP", 1, "1", "(2)"']
}
np.savez('important_stations',important_stations)
np.savez('aditional_stations',aditional_stations)

npzfile = np.load('./important_stations.npz')
print(npzfile.files)
