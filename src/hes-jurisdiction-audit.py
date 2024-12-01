import csv
import datetime
import os
import sqlite3
import time

import constants
import normalize
import intake
import hamilton_address

intake_paths = constants.INTAKE_PATHS
gis_path = constants.GIS_PATH
db_path = constants.DB_PATH
output_path = constants.OUTPUT_PATH

def print_intro():
    print()
    print("# HES Intake Jurisdiction Audit Cleanup Util Thingy #")
    print("\tGalen made this (badly and in a hurry)")
    print()
    print("Current settings (from constants.py): ")
    print("intake_paths=" + str(intake_paths))
    print("gis_path=" + str(gis_path))
    print("db_path=" + str(db_path))
    print("output_path=" + str(output_path))
    print()

def check_database():
    if not os.path.isfile(db_path):
        print("Local database not found, recreating at: " + db_path)
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        create_schema_queries = list()
        create_intake_query = """
            CREATE TABLE "hes_intake" (
                "id"	INTEGER,
                "source_file"	TEXT,
                "source_row"	INTEGER,
                "animal_id"	TEXT,
                "animal_name"	TEXT,
                "intake_date"	TEXT,
                "intake_type"	TEXT,
                "intake_subtype"	TEXT,
                "intake_transfer_from"	TEXT,
                "source_jurisdiction"	TEXT,
                "source_address"	TEXT,
                "zip"	TEXT,
                "normalized_address"	TEXT,
                "stripped_address"	TEXT,
                "match_gis_id"	NUMERIC,
                "computed_jurisdiction"	TEXT,
                "match_type"	TEXT,
                "zip_suggestion"	TEXT,
                "mismatch"	TEXT,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
        """
        create_gis_query = """
            CREATE TABLE "hamilton_address" (
                "id"	INTEGER,
                "address"	TEXT,
                "jurisdiction"	TEXT,
                "zip"	TEXT,
                "normalized_address"	TEXT,
                "stripped_address"	TEXT,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
        """

        create_schema_queries.append(create_intake_query)
        create_schema_queries.append(create_gis_query)

        for query in create_schema_queries:
            cursor.execute(query)
            connection.commit()

        cursor.close()
        connection.close()
        print("Database creation complete")

def show_menu():
    print("1. Clear database table import both Intake and GIS data")
    print("2. Clear Intake database table and import Intake data")
    print("3. Clear GIS database table and import GIS data")
    print("4. Recompute normalization for Intake data")
    print("5. Recompute normalization for GIS data")
    print("6. Recompute normalization for both Intake and GIS data")
    print("7. Process the data!")
    print("8. Export the data!")
    print("9. Clear database, import both Intake and GIS data, process the data, and export the data")
    print("T. Test stuff!")
    print("X. Exit")
    print(">> ", end="")
    menu_selection = input().upper()
    
    start_time = time.time()

    match menu_selection:
        case "1":
            import_intakes(intake_paths, db_path)
            runtime = time.time() - start_time
            print("import_intakes() runtime " + str(datetime.timedelta(seconds=runtime)))
            import_gis(gis_path, db_path)
            runtime = time.time() - start_time
            print("import_gis() runtime " + str(datetime.timedelta(seconds=runtime)))
        case "2":
            import_intakes(intake_paths, db_path)
            runtime = time.time() - start_time
            print("import_intakes() runtime " + str(datetime.timedelta(seconds=runtime)))
        case "3":
            import_gis(gis_path, db_path)
            runtime = time.time() - start_time
            print("import_gis() runtime " + str(datetime.timedelta(seconds=runtime)))
        case "4":
            recompute_intakes()
            runtime = time.time() - start_time
            print("recompute_intakes() runtime " + str(datetime.timedelta(seconds=runtime)))
        case "5":
            recompute_gis()
            runtime = time.time() - start_time
            print("recompute_gis() runtime " + str(datetime.timedelta(seconds=runtime)))
        case "6":
            recompute_intakes()
            runtime = time.time() - start_time
            print("recompute_intakes() runtime " + str(datetime.timedelta(seconds=runtime)))
            recompute_gis()
            runtime = time.time() - start_time
            print("recompute_gis() runtime " + str(datetime.timedelta(seconds=runtime)))
        case "7":
            process_data()
            runtime = time.time() - start_time
            print("process_data() runtime " + str(datetime.timedelta(seconds=runtime)))
        case "8":
            write_output()
            runtime = time.time() - start_time
            print("write_output() runtime " + str(datetime.timedelta(seconds=runtime)))
        case "9":
            import_intakes(intake_paths, db_path)
            runtime = time.time() - start_time
            print("import_intakes() runtime " + str(datetime.timedelta(seconds=runtime)))
            import_gis(gis_path, db_path)
            runtime = time.time() - start_time
            print("import_gis() runtime " + str(datetime.timedelta(seconds=runtime)))
            process_data()
            runtime = time.time() - start_time
            print("process_data() runtime " + str(datetime.timedelta(seconds=runtime)))
            write_output()
            runtime = time.time() - start_time
            print("write_output() runtime " + str(datetime.timedelta(seconds=runtime)))
        case "T":
            test_stuff()
        case "X":
            exit(0)
        case _:
            print("Invalid input")

    print()

def test_stuff():
    normalize.test_normalize_address("8634 TN-58")
    normalize.test_normalize_address("720 O'Sage Drive")
    normalize.test_normalize_address("155 Georgetown Circle Northwest")
    normalize.test_normalize_address("1520 East Brow Road")
    normalize.test_normalize_address("8366 Tennessee 153")
    normalize.test_normalize_address("Tennessee 153")
    normalize.test_normalize_address("TN-153")


def import_intakes(input_csv_paths:list[str], db_path:str):
    print("Connecting to " + db_path)
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # clear hes_intake table
    print("Deleting all records from table: hes_intake")
    cursor.execute("DELETE FROM hes_intake")
    connection.commit()
    print()

    record_count = 0
    row_count = 0
    for path in input_csv_paths:
        with open(path, mode="r", encoding="utf-8") as csvfile:
            file_name = os.path.basename(csvfile.name)
            print("Opened " + file_name)
            row_count = 2
            reader = csv.DictReader(csvfile)
            for fields in reader:
                new_intake = intake.Intake(file_name, row_count, fields)
                if constants.VERBOSE:
                    print("Inserting " + str(new_intake))
                
                insert_query = """
                    INSERT INTO hes_intake
                    (source_file, source_row, animal_id, animal_name, intake_date, intake_type, intake_subtype, intake_transfer_from, source_jurisdiction, source_address, zip, normalized_address, stripped_address, match_gis_id, computed_jurisdiction, zip_suggestion, mismatch)
                    VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
                    """
                params = (new_intake.source_file, new_intake.source_row, new_intake.animal_id, new_intake.animal_name, new_intake.intake_date, new_intake.intake_type, new_intake.intake_subtype, new_intake.intake_transfer_from, new_intake.source_jurisdiction, new_intake.source_address, new_intake.zip, new_intake.normalized_address, new_intake.stripped_address, new_intake.match_gis_id, new_intake.computed_jurisdiction, new_intake.zip_suggestion, new_intake.mismatch)
                cursor.execute(insert_query, params)
                connection.commit()

                record_count += 1
                row_count += 1

                if (record_count % constants.INTAKE_INSERT_QTY == 0):
                    print("Processed " + str(record_count) + " rows so far...")
        
        print("Finished importing", path)

    cursor.close()
    connection.close()
    print("import_intakes() Complete, count=" + str(record_count))

def import_gis(input_csv_path:str, db_path):
    print("Connecting to " + db_path)
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # clear hamilton_address table
    print("Deleting all records from table: hamilton_address")
    cursor.execute("DELETE FROM hamilton_address")
    connection.commit()
    print()

    record_count = 0
    insertion_count = 0
    with open(input_csv_path, mode="r", encoding="utf-8") as csvfile:
        print("Opened " + os.path.basename(csvfile.name))
        reader = csv.DictReader(csvfile)
        for fields in reader:
            new_address = hamilton_address.HamiltonAddress(fields)
            
            if new_address.zip_is_included():
                if constants.VERBOSE:
                    print("Inserting " + str(new_address))
                insert_query = """
                    INSERT INTO hamilton_address
                    (address, jurisdiction, zip, normalized_address, stripped_address)
                    VALUES
                    (?,?,?,?,?);
                    """
                params = (new_address.address, new_address.jurisdiction, new_address.zip, new_address.normalized_address, new_address.stripped_address)
                cursor.execute(insert_query, params)
                connection.commit()
                insertion_count += 1
            else:
                if constants.VERBOSE:
                    print("Excluding " + str(new_address))

            record_count += 1
            if (record_count % constants.GIS_INSERT_QTY == 0):
                print("Processed " + str(record_count) + " rows so far...")

    cursor.close()
    connection.close()
    print("import_gis() Complete, record count=" + str(record_count) + ", insertions=" + str(insertion_count))

def recompute_intakes():
    # don't forget to clear search results columns
    print("recompute_intakes() not yet implemented")

def recompute_gis():
    print("recompute_gis() not yet implemented")

def process_data():
    print("Connecting to " + db_path)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    outer_cursor = connection.cursor()

    zip_jurisdiction_dict = dict()
    zip_list = list()
    zip_jurisdiction_query = "SELECT DISTINCT zip, jurisdiction from hamilton_address ORDER BY zip, jurisdiction"
    outer_cursor.execute(zip_jurisdiction_query)
    for row in outer_cursor:
        if str(row["zip"]) not in zip_list:
            zip_list.append(str(row["zip"]))
        if str(row["zip"]) not in zip_jurisdiction_dict.keys():
            zip_jurisdiction_dict[str(row["zip"])] = list()
        zip_jurisdiction_dict[str(row["zip"])].append(normalize.normalize_jurisdiction(row["jurisdiction"]))
    
    print("zip/jurisdiction map")
    print(zip_jurisdiction_dict)
    
    zip_jurisdiction_result = constants.GIS_NOT_FOUND

    update_intake_query = """
        UPDATE hes_intake
        SET 
        match_gis_id = ?,
        computed_jurisdiction = ?,
        match_type = ?,
        zip_suggestion = ?
        WHERE
        id = ?
        """
    #update_intake_params = (match_gis_id, computed_jurisdiction, match_type, zip_jurisdiction, row["id"])
    
    recordCount = 0
    all_intakes_query = "SELECT * FROM hes_intake"
    outer_cursor.execute(all_intakes_query)
    for row in outer_cursor:
        inner_cursor = connection.cursor()
        if constants.VERBOSE:
            print("Searching for object: " + str(row["id"]) + " " + row["animal_name"] + " " + row["normalized_address"])

        if ("TN " + row["zip"]) not in zip_list:
            # Pass 1 - If unknown zip, flag as such
            if constants.VERBOSE:
                print("Zip " + row["zip"] + " outside area")
            update_intake_params = (-1, constants.OUTSIDE_AREA, "Unrecognized Zip: " + row["zip"], "", row["id"])
            inner_cursor.execute(update_intake_query, update_intake_params)
            connection.commit()
        else:
            # Pass 2 - known zip, search for normalized match, including zip
            search_gis_query = "SELECT * FROM hamilton_address WHERE normalized_address= ? AND zip= ?"
            search_gis_params = (row["normalized_address"], "TN " + row["zip"])
            #search_gis_query = "SELECT * FROM hamilton_address WHERE normalized_address= ?"
            #search_gis_params = (row["normalized_address"],)
            inner_cursor.execute(search_gis_query, search_gis_params)
            search_results = inner_cursor.fetchall()

            if 1 == len(search_results):
                # exactly one match!
                gis_id = search_results[0]["id"]
                jurisdiction = normalize.normalize_jurisdiction(search_results[0]["jurisdiction"])
                if constants.VERBOSE:
                    print("[",gis_id,"] ", jurisdiction)
                update_intake_params = (gis_id, jurisdiction, constants.MATCH_NORMALIZED, "", row["id"])
                inner_cursor.execute(update_intake_query, update_intake_params)
                connection.commit()
            elif 1 < len(search_results):
                # multiple matches
                if constants.VERBOSE:
                    print(constants.GIS_DUPLICATE)
                all_match = True
                jurisdiction = normalize.normalize_jurisdiction(search_results[0]["jurisdiction"])
                zip_jurisdiction_result = ""
                zip_jurisdiction_matches = list()
                for row in search_results:
                    if jurisdiction != row["jurisdiction"]:
                        all_match = False
                    if ("TN " + row["zip"] in zip_jurisdiction_dict):
                        zip_jurisdiction_matches.append(normalize.normalize_jurisdiction(zip_jurisdiction_dict["TN " + row["zip"]]))
                # str.join if the list has multiples, but if all_match=True then just do the first one
                zip_jurisdiction_result = str.join(";", zip_jurisdiction_matches)
                update_intake_params = (-1, constants.GIS_DUPLICATE, "", zip_jurisdiction_result, row["id"])
                if all_match:
                    zip_jurisdiction_result = zip_jurisdiction_matches[0]
                    update_intake_params = (-1, jurisdiction, constants.MATCH_NORMALIZED, "", row["id"])
                inner_cursor.execute(update_intake_query, update_intake_params)
                connection.commit() 
            elif 0 == len(search_results):
                # Pass 3 - Search for stripped address, including zip
                if constants.VERBOSE:
                    print(constants.GIS_NOT_FOUND)
                stripped_search_gis_query = "SELECT * FROM hamilton_address WHERE stripped_address= ? AND zip= ?"
                stripped_search_gis_params = (row["stripped_address"], "TN " + row["zip"])
                inner_cursor.execute(stripped_search_gis_query, stripped_search_gis_params)
                stripped_search_results = inner_cursor.fetchall()

                if 1 == len(stripped_search_results):
                    # exactly one match!
                    gis_id = stripped_search_results[0]["id"]
                    jurisdiction = normalize.normalize_jurisdiction(stripped_search_results[0]["jurisdiction"])
                    if constants.VERBOSE:
                        print("[",gis_id,"] ", jurisdiction)
                    update_intake_params = (gis_id, jurisdiction, constants.MATCH_STRIPPED, "", row["id"])
                    inner_cursor.execute(update_intake_query, update_intake_params)
                    connection.commit()
                else:
                    # Pass 4, no matches, surrender for now and suggest all jurisdictions in the zip
                    # (later, search without zip)
                    suggested_zips = str.join(";",list(zip_jurisdiction_dict[str("TN " + row["zip"])]))
                    suggested_zips += ";" + constants.OUTSIDE_AREA
                    update_intake_params = (-1, constants.GIS_NOT_FOUND, "", suggested_zips, row["id"])
                    inner_cursor.execute(update_intake_query, update_intake_params)
                    connection.commit()

        inner_cursor.close()
        recordCount += 1

        if (recordCount % constants.INTAKE_SEARCH_QTY == 0):
            print("Processed " + str(recordCount) + " rows so far...")

    print("Checking for mismatches")
    clear_mismatch_query = """
        UPDATE hes_intake
        SET
        mismatch = ''
    """
    update_mismatch_query = """
        UPDATE hes_intake
        SET 
        mismatch = 'X'
        WHERE
        source_jurisdiction <> computed_jurisdiction
    """
    outer_cursor.execute(clear_mismatch_query)
    connection.commit()
    outer_cursor.execute(update_mismatch_query)
    connection.commit()

    outer_cursor.close()
    connection.close()
    print("process_data() Complete, count=" + str(recordCount))

def write_output():
    if os.path.isfile(output_path):
        print("Deleting existing " + output_path)
        os.remove(output_path)

    print("Connecting to " + db_path)
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM hes_intake')

    
    with open(output_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write headers
        writer.writerow([i[0] for i in cursor.description])

        recordCount = 0
        for row in cursor:
            writer.writerow(row)
            recordCount += 1

            if (recordCount % constants.OUTPUT_WRITE_QTY == 0):
                print("Processed " + str(recordCount) + " rows so far...")

    # Close the database connection
    connection.close()
    print("Output saved to: " + output_path)
    print("write_output() Complete, count=" + str(recordCount)) 

print_intro()
check_database()
while True:
    show_menu()