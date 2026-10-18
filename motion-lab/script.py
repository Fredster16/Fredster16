"""Demo script used to compare style directions side by side.

Same story as the reference edit (Jamestown, 1607) so the styles can be compared
like for like. Beat starts stand in for where a voice line would land; once a real
voice line is supplied these come from its word timings instead.
"""
from engine import Timeline

BEATS = [
    dict(start=0.0, kicker="IT ALL STARTED IN", hero="1607", kind="year"),
    dict(start=1.5, kicker="LONDON TO VIRGINIA", hero="3 SHIPS", kind="ships",
         names=["Susan Constant", "Godspeed", "Discovery"]),
    dict(start=3.0, kicker="ON BOARD", hero="104 MEN", kind="count", n=104),
    dict(start=4.6, kicker="DEC 1606 → APR 1607", hero="4 MONTHS", kind="route"),
    dict(start=6.1, kicker="THE MISSION", hero="FIND GOLD", kind="gold"),
]
END = 8.0
HANDLE = "@FREDSTER16"

timeline = Timeline(BEATS, END)
