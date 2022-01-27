#!/usr/bin/env python3
"""
Report which meetings are clashing with one another.
"""
import argparse
import re
from datetime import datetime
from functools import cmp_to_key
from typing import List, Optional, Tuple

fmt_day = "%Y-%m-%d"
fmt_12 = f"{fmt_day}.%I:%M%p"
fmt_24 = f"{fmt_day}.%H:%M"

today = datetime.today()
str_today = today.strftime(fmt_day)

H12 = re.compile(r"\d+-\d+-\d+\.\d+:\d+\s?(am|pm)", re.IGNORECASE)
H24 = re.compile(r"\b\d+-\d+-\d+\.\d+:\d+\b", re.IGNORECASE)


def _sort_names(alist: List[str]) -> int:
    """
    Helps Meeting.comparator to sort by name
    fully clashing meetings.
    """
    if alist[0] == alist[1]:
        return 0
    n_list = alist[:]
    n_list.sort()
    if n_list == alist:
        return -1
    else:
        return 1


def get_time_obj(atime: str) -> datetime:
    """
    Normalise and return a datetime object.

    Args:
        atime (str): 'YYYY-MM-DD HH:MM[am| PM]'

    Raises:
        ValueError: case input time string is bad formatted

    Returns:
        datetime: datetime obj
    """
    d = H12.match(atime)
    if d:
        # remove space before AM|pm
        res = d.group().replace(" ", "")
        return datetime.strptime(res, fmt_12)
    d = H24.fullmatch(atime)
    if d:
        return datetime.strptime(d.group(), fmt_24)
    raise ValueError("Invalid time string format: it must be HH:MM or HH:MM AM or HH:MMpm (case insensitive)")


class Meeting:
    """
    Class to define a meeting.

    Attributes:
        name (str): meeting name
        start (str): meeting starting time
        end (str): meeting ending time
        day (str, optional): day of the meeting. Defaults to None.
    """

    def __init__(self, name: str, start: str, end: str, day: Optional[str] = None):
        self.name = name
        if not day:
            day = str_today
        start = f"{day}.{start}"
        end = f"{day}.{end}"
        self.start = get_time_obj(start)
        self.end = get_time_obj(end)

    @staticmethod
    def comparator(a, b) -> int:
        """Used to sort a list of Meetings."""
        res = 0
        if a.start < b.start:
            res = -1
        elif a.start > b.start:
            res = 1
        elif a.start == b.start:
            if a.end > b.end:
                res = 1
            elif a.end < b.end:
                res = -1
            elif a.end == b.end:
                res = _sort_names([a.name, b.name])
        return res

    def __repr__(self) -> str:
        return f"{self.name} @ {self.start.strftime('%H:%M')}_{self.end.strftime('%H:%M')}"


def parse_cmdline() -> argparse.Namespace:
    """
    Input arguments and options.

    Returns:
        argparse.Namespace: opt
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=__doc__)
    parser.add_argument("-i", "--infile", action="store", dest="infile", help="input file with times", required=True)
    parser.add_argument(
        "-d",
        "--day",
        action="store",
        dest="day",
        help=f"optional day, in format YYYY-MM-DD, default is current day: {str_today}",
        default=str_today,
    )
    opt = parser.parse_args()

    return opt


def clashing_meetings(alist: List[Meeting]) -> List[Tuple[Meeting, Meeting, int]]:
    """
    Find out the clashing Meetings.

    Args:
        alist (List[Meeting]): list of Meetings objects

    Returns:
        List[Tuple[Meeting, Meeting, int]]: a list of Meeting objects
    """
    overlaps: List[Tuple[Meeting, Meeting, int]] = []
    for i in range(len(alist) - 1):
        a_i = alist[i]
        for j in range(i + 1, len(alist)):
            a_j = alist[j]
            l_start = max(a_i.start, a_j.start)
            e_end = min(a_i.end, a_j.end)
            if e_end > l_start:
                clash_minutes = (e_end - l_start).seconds // 60
                overlaps.append((a_i, a_j, clash_minutes))
    return overlaps


def get_meetings_list(data: List[str], day: Optional[str] = None) -> List[Meeting]:

    """
    Generate a list of instantiated Meeting objects from the input data.

    Args:
        data (List[str]): list of strings e.g. ["8:15am,8:30am",...]

    Returns:
        List[Meeting]: a list of instanciated Meeting objects
    """
    meetings_list = []
    for n, row in enumerate(data[1:]):  # skip header
        start, end = row.strip().split(",")
        meeting = Meeting(f"Meeting {n+1}", start, end, day)
        meetings_list.append(meeting)

    return meetings_list


def get_clashes() -> List[Tuple[Meeting, Meeting, int]]:
    """
    Take input arguments and process it.

    Returns:
        List[Tuple[Meeting, Meeting, int]]: clashing meetings and overlapping time in minutes
    """
    opt = parse_cmdline()
    with open(opt.infile) as f:
        data_times = f.readlines()

    meetings_list = get_meetings_list(data_times, opt.day)
    # sort meeting_list by starting time, shorter first if same starting time
    meetings_list.sort(key=cmp_to_key(Meeting.comparator))

    return clashing_meetings(meetings_list)


def main() -> None:
    """
    Prints out the overlapping meetings.
    """
    report = get_clashes()
    if report:
        day = report[0][0].start.strftime(fmt_day)
        print(f"Meetings conflict for {day}")
    for clash in report:
        m1, m2, t_min = clash
        c_start = m1.end.strftime("%H:%M")
        c_end = m2.end.strftime("%H:%M")
        print(f"Meetings: <{m1}> and <{m2}> overlaps for {t_min} minutes (between {c_start} and {c_end})")


if __name__ == "__main__":
    main()
