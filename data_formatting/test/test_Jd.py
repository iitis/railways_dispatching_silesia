"""
    there sholud be tests for Jd
"""
import pandas as pd
from data_formatting import jd

def test_Jd():
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")

    # testing particular stations = fast
    Jd_s = jd(data, ["GLC", "MJ", "KZ"])
    assert Jd_s["GLC"]["CB"] == [[5312, 40150, 4500, 40628, 73000]]
    assert Jd_s["MJ"]["KL"] == [[44862]]
    assert Jd_s["MJ"]["Mi"] == [[44717]]
    assert Jd_s["KZ"]["KO(STM)"] == [[26103, 14006, 40673, 54101, 40675], [34319, 94317]]

    # testing all, slow
    Jd_all = jd(data)
    assert Jd_all["KO"]["CB"] == [[26103, 40673, 94317, 40675]]
    assert Jd_all["KO"]["KL"] == [[14006, 94611, 94113, 40477, 44717, 94717]]
    assert Jd_all["KO"]["KO(STM)"] == [[94766, 42100, 5312, 40518, 343199, 40150, 41004, 541019, 4500, 64350, 44862, 40628, 73000, 4120]]
    assert Jd_all["KO(KS)"]["KO"] == [[94611, 94113]]
    assert Jd_all["KO(STM)"]["KO(IC)"] == [[541019]]
    assert Jd_all["KO(IC)"]["KO(STM)"] == [[421009]]
