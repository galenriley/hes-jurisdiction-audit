import normalize

exclude_zips = [
   "TN 37402",
   "TN 37403",
   "TN 37406",
   "TN 37408",
   "TN 37350",
   "TN 37351",
   "TN 37412",
   "TN 37407",
   "TN 37410",
   "TN 37450"
   ]

class HamiltonAddress:
    id:int = -1
    address:str = ""
    jurisdiction:str = ""
    zip:str = ""
    normalized_address:str = ""
    stripped_address:str = ""

    def __init__(self, fields: dict):
        self.address = fields["Location"]
        self.jurisdiction = fields["Jurisdiction"]
        self.zip = fields["ZIPCODE"]
        self.normalized_address = normalize.normalize_address(self.address)
        self.stripped_address = normalize.strip_address(self.normalized_address)

    def zip_is_included(self) -> bool:
       # ignore the exclusion filter
       return True

       if exclude_zips.__contains__(self.zip):
          return False
       else:
          return True

    def __str__(self):
     return self.jurisdiction + " | " + self.address