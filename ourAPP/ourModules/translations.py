TAB_NAME_MAPPING = {
    "PARTNER": "Partners",
    "CONTRACT": "Contracts",
    "CLIENT": "Clients",
    "PRINTING_HOUSE": "Printing Houses",
    "GENRE": "Genres",
    "PUBLICATION": "Publications",
    "client_orders": "Client Orders",
    "contributes": "Contributes",
    "order_printing_house": "Printing House Orders",
    "communication-CLIENT": "Communication - Clients",
    "communication-PARTNER": "Communication - Partners",
    "communication-PRINTING": "Communication - Printing Houses"
}

TAB_NAME_MAPPING_REVERSE = {v: k for k, v in TAB_NAME_MAPPING.items()}

SPECIALIZATION_MAP = {
    1: "Translator",
    2: "Writer",
    3: "Graphic designer",
    4: "Editor"
}

SPECIALIZATION_REVERSE_MAP = {v: k for k, v in SPECIALIZATION_MAP.items()}

# Functions for translating between raw and display values
def to_display_value(col_name: str, raw_value):
    """
    Given the column name and the raw DB value,
    return a user-friendly display value.
    """
    if col_name == "specialisation" and raw_value is not None:
        return SPECIALIZATION_MAP.get(raw_value, raw_value);
    
    return raw_value;

def from_display_value(col_name: str, display_value):
    """
    Convert a user-friendly display value back to the raw (DB) form.
    """
    if col_name == "specialisation" and display_value is not None:
        return SPECIALIZATION_REVERSE_MAP.get(display_value, display_value);

    return display_value;

def get_specialization_display_values():
    """
    Return a list of display-friendly specialization values.
    """
    return list(SPECIALIZATION_MAP.values());

def table_to_display(table_name: str) -> str:
    """
    Convert the raw database table name (e.g. "PARTNER") into a
    friendly display name (e.g. "Partners").
    Falls back to capitalizing the raw name if not found in TAB_NAME_MAPPING.
    """
    return TAB_NAME_MAPPING.get(table_name, table_name.capitalize());

def table_from_display(display_name: str) -> str:
    """
    Convert a user-friendly display name (e.g. "Partners") back into the
    actual database table name (e.g. "PARTNER").
    Falls back to the display_name as-is if no mapping is found.
    """
    return TAB_NAME_MAPPING_REVERSE.get(display_name, display_name);

def main():
    for key, value in TAB_NAME_MAPPING.items():
        print(f"{key} -> {value}")

    print(" ") # Better readability

    for key, value in SPECIALIZATION_MAP.items():
        print(f"{key} -> {value}")

    return;

if __name__ == "__main__":
    main()
