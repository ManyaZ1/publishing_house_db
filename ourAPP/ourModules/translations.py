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

def main():
    for key, value in TAB_NAME_MAPPING.items():
        print(f"{key} -> {value}")

    return;

if __name__ == "__main__":
    main()
