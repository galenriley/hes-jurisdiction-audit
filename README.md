hes-jurisdiction-audit, a quick and dirty utility for helping hot girlfriends check their shelterluv data vs GIS data from Hamilton County, TN

The application (and most of the logic) exists in /src/hes-jurisdiction-audit.py

Expecting these files at /data/
- FY23 Intake LRR.csv (shelterluv report, excluded for privacy reasons)
- FY24 Intake LRR.csv (ditto)
- GIS Data.csv (included, provided by the Hamilton County GIS office. Preprocessed by removing the apartment numbers and removing duplicate values)

constants.py contains various constants, as well as the config for which files to read. Insert a # character at the beginning of the first line and remove the one from line 9 to swap to the real data
```
"""
INTAKE_PATHS = ["data/FY23 Intake LRR.csv", "data/FY24 Intake LRR.csv"]
GIS_PATH = "data/GIS Data.csv"
DB_PATH = "data/hes_intake_jurisdiction.sqlite"
"""
INTAKE_PATHS = ["data/sample/Sample Intakes.csv"]
GIS_PATH = "data/sample/Sample GIS.csv"
DB_PATH = "data/sample/hes_intake_jurisdiction - sample.sqlite"
#"""
```
