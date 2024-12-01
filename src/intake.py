import constants
import normalize

class Intake:
    id:int = -1
    source_file:str = ""    # input csv file name
    source_row:int = 0      # spreadsheet row number, where 1 is headers
    animal_id:str = ""
    animal_name:str = ""
    intake_date:str = ""
    intake_type:str = ""
    intake_subtype:str = ""
    intake_transfer_from:str = ""
    source_jurisdiction:str = ""
    source_address:str = ""
    zip:str = ""
    normalized_address:str = ""
    stripped_address:str = ""
    match_gis_id:int = -1
    computed_jurisdiction:str = constants.INIT
    zip_suggestion:str = ""
    mismatch:str = ""

    def __init__(self, source_file:str, source_row:int, fields:dict):
        self.source_file = source_file
        self.source_row = source_row
        self.animal_id = fields["Animal ID"]
        self.animal_name = fields["Name"]
        self.intake_date = fields["Intake Date"]
        self.intake_type = fields["Intake Type"]
        self.intake_subtype = fields["Intake Subtype"]
        self.intake_transfer_from = fields["Intake Transfer From"]
        self.source_jurisdiction = fields["Intake Jurisdiction"]
        if fields["Intake Found Address"] == "—":
            self.source_address = fields["Intake From Address 1"]
        else:
            self.source_address = fields["Intake Found Address"]
        if fields["Intake Found Zip"] == "—":
            self.zip = fields["Intake From Zip"]
        else:
            self.zip = fields["Intake Found Zip"]
        self.normalized_address = normalize.normalize_address(self.source_address)
        self.stripped_address = normalize.strip_address(self.normalized_address)

    def __str__(self):
        return self.animal_name + " | " + str(self.source_row) + " | " + self.source_jurisdiction + " | " + self.source_address