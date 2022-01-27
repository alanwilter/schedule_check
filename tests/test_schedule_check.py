from functools import cmp_to_key

import pytest

from schedule_check import __version__
from schedule_check.report_meetings_clashes import (
    Meeting,
    clashing_meetings,
    get_clashes,
    get_meetings_list,
    get_time_obj,
)


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
    mm = [m3, m1, m2]
    ms = sorted(mm, key=cmp_to_key(Meeting.comparator))
    assert ms == [m2, m1, m3]


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
