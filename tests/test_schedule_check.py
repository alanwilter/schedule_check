from functools import cmp_to_key
from subprocess import STDOUT, check_output

import pytest

from schedule_check import __version__
from schedule_check.report_meetings_clashes import Meeting, clashing_meetings, get_meetings_list, get_time_obj


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.parametrize(
    ("atime"),
    [
        ("2022-01-26.9:30 pm"),
        ("2022-01-26.9:30am"),
        ("2022-01-26.9:30 AM"),
        ("2022-01-26.9:30PM"),
        ("2022-01-26.18:30"),
    ],
)
def test_hour_format(atime):
    d = get_time_obj(atime)
    assert d


@pytest.mark.parametrize(
    ("atime"),
    [
        ("2022-01-26 8h00"),
        ("2022-01-26 9:30am"),
        ("2022-01-26.9:30 A"),
        ("2022-01-26.9:30P"),
        ("2022-01-26 18:30"),
    ],
)
def test_wrong_time_format(atime):
    with pytest.raises(ValueError) as e_info:
        get_time_obj(atime)
    assert "Invalid time string format:" in e_info.value.args[0]


def test_class_repr():
    m = Meeting("test", "7:00", "6:00pm")
    assert repr(m) == "test @ 07:00_18:00"


def test_comparator():
    m1 = Meeting("test1", "7:00", "8:00am")
    m2 = Meeting("test2", "7:00", "7:30")
    m3 = Meeting("test3", "7:30", "8:30am")
    m4 = Meeting("test4", "7:30", "9:30am")
    m5 = Meeting("test0", "7:00", "7:30am")  # clash m2, name diff
    m6 = Meeting("test3", "7:30", "8:30am")  # m6 = m3
    m7 = Meeting("test7", "7:00", "8:00am")  # m7 = m1
    mm = [m3, m1, m2, m4, m5, m6, m7]
    ms = sorted(mm, key=cmp_to_key(Meeting.comparator))
    assert ms == [m5, m2, m1, m7, m3, m6, m4]


def test_clashes():
    data = ["start,end", "9:00am,10:00am", "9:30am,10:30am", "1:30pm,3:00pm", "3:00pm,3:30pm"]
    m_list = get_meetings_list(data)
    assert (
        repr(m_list)
        == "[Meeting 1 @ 09:00_10:00, Meeting 2 @ 09:30_10:30, Meeting 3 @ 13:30_15:00, Meeting 4 @ 15:00_15:30]"
    )
    m_list.sort(key=cmp_to_key(Meeting.comparator))
    c = clashing_meetings(m_list)
    assert repr(c) == "[(Meeting 1 @ 09:00_10:00, Meeting 2 @ 09:30_10:30, 30)]"


def test_cli():
    msgs = [
        "Meetings conflict for 2021-12-25",
        "Meetings: <Meeting 2 @ 09:00_10:00> and <Meeting 3 @ 09:30_10:30> overlaps for 30 minutes (between 10:00",
        "Meetings: <Meeting 4 @ 10:45_13:00> and <Meeting 5 @ 12:00_13:00> overlaps for 60 minutes (between 13:00",
    ]
    cmd = "env python3 ./schedule_check/report_meetings_clashes.py -i tests/times -d '2021-12-25'"
    out = check_output(cmd, shell=True, stderr=STDOUT).decode()
    for msg in msgs:
        assert msg in out
