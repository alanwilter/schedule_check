# Schedule Meetings Time Checker

For a supplied "times" data file containing a list of start/end times for a series of meetings scheduled during one day, it checks and reports which meetings conflict with one another.

```text
usage: report_schedule [-h] -i INFILE [-d DAY]

Report which meetings are clashing with one another.

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        input file with times
  -d DAY, --day DAY     optional day, in format YYYY-MM-DD, default is current day: 2022-01-27
```
