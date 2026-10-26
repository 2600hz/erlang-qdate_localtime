#!/usr/bin/env python3
"""Compare the library with an independently compiled, pinned IANA release.

Run test/run.sh first, then provide the official tzdata2026e.tar.gz archive.
This check requires Python 3.12+, zic and escript; it does not fetch data.
"""

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import shutil
import subprocess
import tarfile
import tempfile
import zoneinfo


ARCHIVE_SHA256 = "b26882805f26aac59d5b222978e6580484b834ccdc98be89df2f05a6dc53a652"
ZONES = {
    "America/Vancouver": -420,
    "Canada/Pacific": -420,
    "America/Edmonton": -360,
    "Canada/Mountain": -360,
    "America/Yellowknife": -360,
    "America/Inuvik": -360,
    "America/Winnipeg": -300,
    "Canada/Central": -300,
    "America/Rainy_River": -300,
}


def datetime_term(value):
    return "{{%d,%d,%d},{%d,%d,%d}}" % (
        value.year, value.month, value.day, value.hour, value.minute, value.second
    )


def instants(offset):
    result = {
        dt.datetime(year, month, 15, 20, tzinfo=dt.timezone.utc)
        for year in range(2025, 2029) for month in range(1, 13)
    }
    transition = dt.datetime(2026, 11, 1, 2, tzinfo=dt.timezone.utc) - dt.timedelta(minutes=offset)
    for minute in range(-24 * 60, 24 * 60 + 1, 15):
        result.add(transition + dt.timedelta(minutes=minute))
    for second in range(-15, 16):
        result.add(transition + dt.timedelta(seconds=second))
    # No gap or overlap at the following year's former seasonal transitions.
    for date in [(2027, 3, 14), (2027, 11, 7)]:
        center = dt.datetime(*date, 2, tzinfo=dt.timezone.utc) - dt.timedelta(minutes=offset)
        for minute in range(-12 * 60, 12 * 60 + 1, 15):
            result.add(center + dt.timedelta(minutes=minute))
    return sorted(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tzdata_archive", type=pathlib.Path)
    parser.add_argument("--ebin", type=pathlib.Path, default=pathlib.Path("_build/manual-test/ebin"))
    args = parser.parse_args()
    archive = args.tzdata_archive.resolve()
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != ARCHIVE_SHA256:
        parser.error(f"expected IANA 2026e SHA256 {ARCHIVE_SHA256}; got {digest}")
    root = pathlib.Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory(prefix="qdate-iana-") as directory:
        temp = pathlib.Path(directory)
        sources, compiled = temp / "source", temp / "zoneinfo"
        sources.mkdir()
        with tarfile.open(archive) as source:
            source.extractall(sources, filter="data")
        if (sources / "version").read_text().strip() != "2026e":
            parser.error("archive version is not 2026e")
        files = ["africa", "antarctica", "asia", "australasia", "europe",
                 "northamerica", "southamerica", "etcetera", "backward"]
        subprocess.run([shutil.which("zic") or "/usr/sbin/zic", "-d", str(compiled)]
                       + [str(sources / name) for name in files], check=True)
        vectors = []
        for name, offset in ZONES.items():
            with (compiled / name).open("rb") as stream:
                zone = zoneinfo.ZoneInfo.from_file(stream, key=name)
            for utc in instants(offset):
                local = utc.astimezone(zone)
                dst = "is_in_dst" if local.dst() else "is_not_in_dst"
                shift = int(local.utcoffset().total_seconds() / 60)
                vectors.append("{%s,%s,%s,%s,%s,%d}" % (
                    datetime_term(utc), json.dumps(name), datetime_term(local),
                    json.dumps(local.tzname()), dst, shift))
        vectors_file = temp / "vectors.terms"
        vectors_file.write_text("[\n" + ",\n".join(vectors) + "\n].\n")
        subprocess.run(["escript", str(root / "test/iana_oracle.escript"),
                        str(args.ebin.resolve()), str(vectors_file)], check=True)
        print(f"IANA tzdata 2026e SHA256 {digest}", flush=True)


if __name__ == "__main__":
    main()
