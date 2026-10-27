## NOTE

This is a fork of the excellent library,
[erlang_localtime](https://github.com/dmitryme/erlang_localtime). The purpose
of this fork is specifically for compatibility with
[qdate](https://github.com/choptastic/qdate).  The two are mostly compatible,
but have diverged slightly over the years.  The qdate tests will not pass if the
original `erlang_localtime dependency` is used due to some subtle differences
to attempt to make qdate a little bit smarter.

#### Canadian rules effective in 2026

Version 1.2.3 includes upstream 1.2.2 and the dated Canadian corrections below.

The date being converted selects the timezone rules. For Vancouver, Edmonton,
Inuvik, Winnipeg and their retained aliases, conversions before the 2026 change
keep the existing seasonal rules. Conversions after the change use permanent
UTC-7, UTC-6, UTC-6 and UTC-5 respectively. This selection applies to UTC/local
conversion, offset/name lookup and direct `localtime_dst:check/2` calls.

The corrections follow [IANA tzdata 2026e](https://www.iana.org/time-zones/releases/2026e),
including its modeled abbreviation/DST transition at 02:00 local daylight time
on November 1, 2026. At that instant the UTC offset stays the same; the final
daylight names PDT/MDT/CDT become MST/CST/EST. The former 01:00 overlap is
cancelled. Earlier timestamps and unrelated zones retain the legacy snapshot;
this is a targeted correction, not a complete upgrade of that snapshot.

Run the existing and Canadian regression tests with the installed Erlang tools:

```sh
bash test/run.sh
```

An independent comparison compiles the official IANA archive with `zic` and
uses Python's `zoneinfo` to generate conversion, name, DST and offset vectors.
It requires Python 3.12+, `zic` and `escript`, and verifies the archive's SHA256:

```sh
python3 test/check_iana.py /path/to/tzdata2026e.tar.gz
```

#### Public exports

* `utc_to_local(DateTime, Timezone)` - converts UTC time to local according to specified Timezone
* `local_to_utc(DateTime, Timezone)` - converts local time to UTC
* `local_to_local(DateTime, TimezoneFrom, TimezoneTo)` - converts local time to local
* `tz_name(DateTime, Timezone)` - returns a timezone name (E.g. MSK, MSD, etc)
* `tz_shift(DateTime, Timezone)` - returns time difference between local datetime and GMT
* `tz_shift(DateTime, TimezoneFrom, TimezoneTo)` - returns time difference between local datetime and required timezone
Where
DateTime = {date(), time()}
TimeZone(To, From) = String(). E.g. “Europe/Moscow”, “America/NewYork”. Or abbreviations "MSK", "MSD", etc. Note:
abbreviation is just used to find appropriate timezone name. If you want to convert "MSK" -> "PDT", but source timezone
is not in daylight saving, it will be corrected by library and "MSK" -> "PST" conversion will be made.

#### Examples of usage

Converts UTC time to local one
>localtime:utc_to_local({{2010, 7, 22}, {17, 56, 23}, "Europe/Moscow").
>
>{{2010,10,10},{21,56,23}}

Converts local time to UTC one
>localtime:local_to_utc({{2010, 10, 10}, {21, 56, 23}}, "Europe/Moscow").
>
>{{2010,10,10},{17,56,23}}

Converts time from one local timezone to another local one
>localtime:local_to_local({{2010, 10, 10}, {21, 56, 23}}, "Europe/Moscow", "Australia/Sydney").
>
>{{2010,10,11},{3,56,23}}

Returns timezone name
>localtime:tz_name({{2010, 10, 10}, {21, 56, 23}}, "Europe/Moscow").
>
>{"MSK","MSK"}

>localtime:tz_name({{2010,10,11},{3,56,23}}, "Australia/Sydney").
>
>{"EST","EST"}

Calculates time difference between UTC and local one
>localtime:tz_shift({{2013, 01, 22}, {18, 17, 00}}, "Europe/Moscow").
>
>{'+',4,0}

>localtime:tz_shift({{2013, 01, 22}, {18, 17, 00}}, "America/New York").
>
>{'-',5,0}

Calculates time difference between two local timezones
>localtime:tz_shift({{2013, 01, 22}, {18, 17, 00}}, "America/New York", "Europe/Moscow").
>
>{'+',9,0}
