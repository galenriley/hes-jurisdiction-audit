"""
INTAKE_PATHS = ["data/FY23 Intake LRR.csv", "data/FY24 Intake LRR.csv"]
GIS_PATH = "data/GIS Data.csv"
DB_PATH = "data/hes_intake_jurisdiction.sqlite"
OUTPUT_PATH = "data/output.csv"
"""
INTAKE_PATHS = ["data/sample/Sample Intakes.csv"]
GIS_PATH = "data/sample/Sample GIS.csv"
DB_PATH = "data/sample/hes_intake_jurisdiction - sample.sqlite"
OUTPUT_PATH = "data/sample/Sample Output.csv"

VERBOSE = False

INIT = "Initial Status"
GIS_NOT_FOUND = "GIS Not Found"
GIS_DUPLICATE = "Duplicate GIS Match"
OUTSIDE_AREA = "Outside Area"
MATCH_NORMALIZED = "Normalized"
MATCH_NORMALIZED_WITHOUT_ZIP = "Normalized without Zip"
MATCH_STRIPPED = "Stripped"
MATCH_STRIPPED_WITHOUT_ZIP = "Stripped without Zip"

INTAKE_INSERT_QTY = 1000
INTAKE_SEARCH_QTY = 1000
OUTPUT_WRITE_QTY = 1000
GIS_INSERT_QTY = 10000