from scourgify import normalize_address_record
from scourgify.address_constants import (
    DIRECTIONAL_REPLACEMENTS,
    STREET_TYPE_ABBREVIATIONS
)

address_conversion_map = [
    [" Avenue", " Ave"],
    [" Circle", " Cir"],
    [" Court", " Ct"],
    [" Drive", " Dr"],
    [" Lane", " Ln"],
    [" Parkway", " Pkwy"],
    [" Place", " Pl"],
    [" Road", " Rd"],
    [" Street", " St"],
    [" Trail", " Trl"]
]

jurisdiction_conversion_map = [
    ["CHATTANOOGA", "Chattanooga (MAC Service Region)"],
    ["COLLEGEDALE", "Collegedale"],
    ["EAST RIDGE", "East Ridge (ERAS Service Region)"],
    ["HAMILTON COUNTY", "Unincorporated Hamilton County"],
    ["LAKESITE", "Lakesite (MAC Service Region)"],
    ["LOOKOUT MOUNTAIN", "Lookout Mountain (LM PD Service Region)"],
    ["RED BANK", "Red Bank (MAC Service Region)"],
    ["RIDGESIDE", "Ridgeside"],
    ["SIGNAL MOUNTAIN", "Signal Mountain"],
    ["SODDY DAISY", "Soddy Daisy"],
    ["WALDEN", "Walden"]
]

def test_normalize_address(address: str):
    print("IN:")
    print(address)
    print("OUT:")
    normalized_address = normalize_address(address)
    print(normalized_address)
    print("STRIPPED:")
    stripped_address = strip_address(normalized_address)
    print(stripped_address)


def normalize_address(address: str) -> str:
    normalized_address = address.upper().strip()

    try:
        # bonus hwy 58 treatment
        normalized_address = normalized_address.replace("TENNESSEE 58", "HIGHWAY 58")
        normalized_address = normalized_address.replace("TN-58", "HIGHWAY 58")
        normalized_address = normalized_address.replace("TENNESSEE 153", "HIGHWAY 153")
        normalized_address = normalized_address.replace("TN-153", "HIGHWAY 153")

        normalized_address = normalize_address_record(normalized_address)["address_line_1"]
    except:
        # previous custom code if scourgify doesn't work
        for item in address_conversion_map:
            if (normalized_address.endswith(item[0])):
                normalized_address = normalized_address[:-len(item[0])] + item[1]

        # O'Sage lol, also there are no apostrophes in the GIS dataset so this probably fixes other stuff
        normalized_address = normalized_address.replace("'","")

        # bonus hwy 58 treatment, this is duplicated because it didn't work when i put it at the top? idk
        normalized_address = normalized_address.replace("TENNESSEE 58", "HIGHWAY 58")
        normalized_address = normalized_address.replace("TN-58", "HIGHWAY 58")
        normalized_address = normalized_address.replace("TENNESSEE 153", "HIGHWAY 153")
        normalized_address = normalized_address.replace("TN-153", "HIGHWAY 153")
    
        normalized_address = normalized_address.strip()

    return normalized_address

def strip_address(address: str) -> str:
    # assumes the address has already been normalized by scourgify
    for item in DIRECTIONAL_REPLACEMENTS.values():
        if (address.endswith(" " + item)):
            address = address[:-len(item)].strip()
    
    for item in STREET_TYPE_ABBREVIATIONS.values():
        if (address.endswith(" " + item)):
            address = address[:-len(item)].strip()

    return address

def normalize_jurisdiction(jurisdiction: str) -> str:
    for item in jurisdiction_conversion_map:
        if jurisdiction == item[0]:
            jurisdiction = item[1]

    return jurisdiction