#!/usr/bin/env python3
"""
Report which meetings are clashing with one another.
"""
import argparse
import re
from datetime import datetime, timedelta
from functools import cmp_to_key
from typing import List, Optional, Tuple

fmt_day = "%Y-%m-%d"
fmt_12 = f"{fmt_day}.%I:%M%p"
fmt_24 = f"{fmt_day}.%H:%M"

today = datetime.today()
str_today = today.strftime(fmt_day)

H12 = re.compile(r"\d+-\d+-\d+\.\d+:\d+\s?(am|pm)", re.IGNORECASE)
H24 = re.compile(r"\b\d+-\d+-\d+\.\d+:\d+\b", re.IGNORECASE)


class Meeting:
    """
    Class to define a meeting.

    Attributes:
        name (str)             : Meeting name
        start (datetime)       : Meeting starting time
        end (datetime)         : Meeting ending time
        str_day (str, optional): Day of the meeting. Defaults to current day.
        day_start              : Working hours start
        day_end                : Working hours end
    """

    def __init__(self, name: str, start: str, end: str, day: Optional[str] = None):
        """
        Args:
            name (str): Meeting name
            start (str): Meeting starting time in string
            end (str): Meeting ending time in string
            day (Optional[str], optional): Day of the meeting. Defaults to None -> current day.
        """
        self.name = name
        if not day:
            day = str_today
        self.str_day = day
        start = f"{day}.{start}"
        end = f"{day}.{end}"
        self.start = get_time_obj(start)
        self.end = get_time_obj(end)
        self.is_valid = True  # until proved not

    def check_validity(self, day_start: str, day_end: str) -> bool:
        """
        Check if a Meeting is within working hours

        Args:
            day_start (str): Day starting time in string
            day_end (str): Day ending time in string

        Returns:
            bool: True or false
        """
        self.day_start = get_time_obj(f"{self.str_day}.{day_start}")
        self.day_end = get_time_obj(f"{self.str_day}.{day_end}")
        if self.start < self.day_start:
            self.is_valid = False
        if self.end > self.day_end:
            self.is_valid = False
        return self.is_valid

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
        if "24:00" in d.group():  # next day
            return datetime.strptime(d.group().replace("24:00", "00:00"), fmt_24) + timedelta(days=1)
        return datetime.strptime(d.group(), fmt_24)

    raise ValueError("Invalid time string format: it must be HH:MM or HH:MM AM or HH:MMpm (case insensitive)")


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


def _clashing_meetings(alist: List[Meeting]) -> List[Tuple[Meeting, Meeting, int, str, str]]:
    """
    Find out the clashing Meetings.

    Args:
        alist (List[Meeting]): list of Meetings objects

    Returns:
        List[Tuple[Meeting, Meeting, int, str, str]]:
            clashing meetings and overlapping time (with start and end) in minutes
    """
    overlaps: List[Tuple[Meeting, Meeting, int, str, str]] = []
    for i in range(len(alist) - 1):
        a_i = alist[i]
        for j in range(i + 1, len(alist)):
            a_j = alist[j]
            l_start = max(a_i.start, a_j.start)
            e_end = min(a_i.end, a_j.end)
            if e_end > l_start:
                clash_minutes = (e_end - l_start).seconds // 60
                begin = l_start.strftime("%H:%M")
                end = e_end.strftime("%H:%M")
                overlaps.append(
                    (
                        a_i,
                        a_j,
                        clash_minutes,
                        begin,
                        end,
                    )
                )
    return overlaps


def get_meetings_list(data: List[str], day: Optional[str] = None) -> Tuple[List[Meeting], List[Meeting]]:
    """
    Generate a list of instantiated Meeting objects from the input data.

    Args:
        data (List[str]): list of strings e.g. ["8:15am,8:30am",...]
        day (Optional[str], optional): [description]. Defaults None.

    Returns:
        Tuple[List[Meeting], List[Meeting]]: a tuple of lists of valid and invalid sorted instanciated Meeting objects
    """
    meetings_list: List[Meeting] = []
    # 12am = 00:00, 12pm = 12:00
    day_start = "0:00"
    day_end = "24:00"
    for n, row in enumerate(data[1:]):  # skip header
        start, end = row.strip().split(",")

        # parse single input, optional, defines the day work schedule, otherwise
        # otherwise any meeting in 24 h is valid
        if not end:
            day_start = start
        if not start:
            day_end = end

        if start and end:
            meeting = Meeting(f"Meeting {n+1}", start, end, day)
            meetings_list.append(meeting)

    # sort meeting_list by starting time, shorter first if same starting time
    meetings_list.sort(key=cmp_to_key(Meeting.comparator))

    valid_meetings = []
    invalid_meetings = []
    for m in meetings_list:
        if m.check_validity(day_start, day_end):
            valid_meetings.append(m)
        else:
            invalid_meetings.append(m)

    return (valid_meetings, invalid_meetings)


def process_args() -> Tuple[List[str], str]:
    opt = parse_cmdline()
    with open(opt.infile) as f:
        data_times = f.readlines()
    return data_times, opt.day


def get_clashes() -> Tuple[List[Tuple[Meeting, Meeting, int, str, str]], List[Meeting]]:
    """
    Take input arguments and process it.

    Returns:
        Tuple[List[Tuple[Meeting, Meeting, int, str, str]], List[Meeting]]:
            clashing meetings and overlapping time (with start and end) in minutes plus invalid meetings
    """
    data_times, day = process_args()
    m_valid, m_invalid = get_meetings_list(data_times, day)

    return (_clashing_meetings(m_valid), m_invalid)


def main() -> None:
    """
    Prints out the overlapping meetings.
    """
    valid_tuple, invalid_list = get_clashes()
    if valid_tuple:
        day = valid_tuple[0][0].start.strftime(fmt_day)
        print(f">>>Meetings conflict for {day}")
    for clash in valid_tuple:
        m1, m2, t_min, begin, end = clash
        print(f"Meetings: <{m1}> and <{m2}> overlaps for {t_min} min ({begin} to {end})")
    if invalid_list:
        if valid_tuple:
            print()
        day_start = invalid_list[0].day_start.strftime("%H:%M")
        day_end = invalid_list[0].day_end.strftime("%H:%M")
        print(f">>>Invalid Meetings, outside working hours for {day}: {day_start} to {day_end}")
    for inv in invalid_list:
        print(inv)


if __name__ == "__main__":
    main()
