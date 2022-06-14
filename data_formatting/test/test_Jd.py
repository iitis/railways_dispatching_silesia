"""
    there sholud be tests for Jd
"""
import pandas as pd
from data_formatting import jd

def test_Jd():
    data = pd.read_csv("../data/train_schedule.csv", sep = ";")

    # tests should be here
    jd(data)
    assert 1 == 1
