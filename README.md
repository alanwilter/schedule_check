# Schedule Meetings Time Checker

For a supplied "times" data file containing a list of start/end times for a series of meetings scheduled during one day, it checks and reports which meetings conflict with one another.

## Installation

```bash
pip install git+https://github.com/alanwilter/schedule_check.git
```

## Usage

```text
usage: report_schedule [-h] -i INFILE [-d DAY]

Report which meetings are clashing with one another.

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        input file with times
  -d DAY, --day DAY     optional day, in format YYYY-MM-DD, default is current day: 2022-01-27
```

## Example

```text
$> report_schedule -i tests/times -d '2021-12-25'

Meetings conflict for 2021-12-25
Meetings: <Meeting 2 @ 09:00_10:00> and <Meeting 3 @ 09:30_10:30> overlaps for 30 minutes (between 10:00 and 10:30)
Meetings: <Meeting 4 @ 10:45_13:00> and <Meeting 5 @ 12:00_13:00> overlaps for 60 minutes (between 13:00 and 13:00)
```
