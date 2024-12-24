import os
import sqlite3
import random
from datetime import datetime, timedelta
from time import sleep

# ----------------------------------------- #
# 1) Helper Functions                      #
# ----------------------------------------- #

def read_data_from_file(file_path):
    """
    Reads lines from a text file under the 'datasets/' folder
    and returns a list of stripped strings.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "datasets", file_path)
    #file_path = f"datasets/{file_path}"  # Dynamic path calculation
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

def random_date(start, end):
    """
    Returns a random datetime between 'start' and 'end'.
    """
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def random_afm():
    """
    Returns a random integer in the range [100_000_000, 999_999_999].
    """
    return random.randint(100_000_000, 999_999_999)

def random_phone():
    """
    Returns a random 'phone-like' integer.
    For demonstration, we randomly pick a 69x or 2651x style phone.
    """
    return random.choice([
        random.randint(69_000_00000, 699_999_9999),
        random.randint(2651_000000, 2651_999999)
    ])

def random_partition(total, parts):
    """
    Divides 'total' into 'parts' random positive integer chunks that sum to 'total'.
    """
    result = []
    allocated = 0

    for i in range(parts - 1):
        # Maximum that can be assigned to this chunk
        # so that we can still distribute at least '1' to the remaining chunks
        max_for_chunk = total - allocated - ((parts - 1) - i)
        chunk = random.randint(1, max_for_chunk)
        result.append(chunk)
        allocated += chunk

    final_chunk = total - allocated
    result.append(final_chunk)

    return result

def get_everything(cursor, query):
    """
    Executes the given 'query' with the provided 'cursor'
    and returns a list of the first column of each row.
    """
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]

# ----------------------------------------- #
# 2) Create + Drop DB schema               #
# ----------------------------------------- #

def create_database(db_path, schema_file_path):
    """
    Creates (or recreates) the database by running the SQL schema script.
    """
    with open(schema_file_path, 'r', encoding='utf-8') as schema_file:
        schema_content = schema_file.read()

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.executescript(schema_content)  # Runs the entire schema script
    connection.commit()
    connection.close()

    print("Database created successfully!")

def drop_tables(db_path):
    """
    Drops all tables in the new schema (using PRAGMA foreign_keys=OFF).
    Useful if you want to start fresh each time.
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Disable FK checks to avoid dependency errors
    cursor.execute("PRAGMA foreign_keys = OFF;")

    statements = [
        'DROP TABLE IF EXISTS "communication-CLIENT";',
        'DROP TABLE IF EXISTS "communication-PARTNER";',
        'DROP TABLE IF EXISTS "communication-PRINTING";',
        'DROP TABLE IF EXISTS "order_printing_house";',
        'DROP TABLE IF EXISTS "contributes";',
        'DROP TABLE IF EXISTS "client_orders";',
        'DROP TABLE IF EXISTS "CONTRACT";',
        'DROP TABLE IF EXISTS "PUBLICATION";',
        'DROP TABLE IF EXISTS "GENRE";',
        'DROP TABLE IF EXISTS "PRINTING_HOUSE";',
        'DROP TABLE IF EXISTS "CLIENT";',
        'DROP TABLE IF EXISTS "PARTNER";'
    ]

    for sql in statements:
        cursor.execute(sql)

    # Re-enable FK checks
    cursor.execute("PRAGMA foreign_keys = ON;")
    connection.commit()
    connection.close()

    print("All tables dropped successfully!")

# ----------------------------------------- #
# 3) Data Population Logic                 #
# ----------------------------------------- #

def populate_database(db_path):
    """
    Populates the newly created DB with random data,
    following the logic from the old code but referencing
    the new table names + columns.
    """
    # Datasets for generating realistic names/titles
    first_names  = read_data_from_file('first_names.txt')
    last_names   = read_data_from_file('last_names.txt')
    categories   = read_data_from_file('categories.txt')
    locations    = read_data_from_file('locations.txt')
    book_titles  = read_data_from_file('book_titles.txt')
    # For this example we will not read 'bookstores_names.txt'
    # because you requested to use first_names + last_names for CLIENT.

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # ---------- PARTNER ----------
    partner_tax_ids = set()
    partners = []
    for _ in range(10):
        while True:
            tax_id = random_afm()   # Our old random_afm
            if tax_id not in partner_tax_ids:
                partner_tax_ids.add(tax_id)
                break

        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        specialisation = random.randint(1, 4)  # Must be 1..4 per schema constraint
        comments = f"Comments for partner with Tax ID {tax_id}"

        partners.append((name, tax_id, specialisation, comments))

    cursor.executemany(
        'INSERT INTO "PARTNER" ("name", "Tax_Id", "specialisation", "comments") VALUES (?, ?, ?, ?)',
        partners
    )

    all_partner_tax_ids = get_everything(cursor, 'SELECT "Tax_Id" FROM "PARTNER"')

    # ---------- CLIENT ----------
    client_tax_ids = set()
    clients = []
    for _ in range(15):
        while True:
            tax_id = random_afm()
            # Ensure no overlap with PARTNER tax IDs
            if (tax_id not in client_tax_ids) and (tax_id not in all_partner_tax_ids):
                client_tax_ids.add(tax_id)
                break

        # Here we do the requested client naming pattern:
        #   name = f"{random.choice(first_names)} {random.choice(last_names)}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        loc  = random.choice(locations)

        clients.append((tax_id, name, loc))

    cursor.executemany(
        'INSERT INTO "CLIENT" ("Tax_ID", "name", "location") VALUES (?, ?, ?)',
        clients
    )

    all_client_tax_ids = get_everything(cursor, 'SELECT "Tax_ID" FROM "CLIENT"')

    # ---------- PRINTING_HOUSE ----------
    printing_houses = []
    printing_id = 1
    for _ in range(5):
        # 'capabilities' is an INT column in the schema,
        # so let's just pick a random int 1..5
        capabilities = random.randint(1, 5)
        printing_houses.append((random.choice(locations), printing_id, capabilities))
        printing_id += 1

    cursor.executemany(
        'INSERT INTO "PRINTING_HOUSE" ("p_location", "p_id", "capabilities") VALUES (?, ?, ?)',
        printing_houses
    )

    all_printing_ids = get_everything(cursor, 'SELECT "p_id" FROM "PRINTING_HOUSE"')

    # ---------- GENRE ----------
    genre_data = []
    genre_id = 1
    for category in categories:
        description = f"Books in the {category.lower()} genre"
        age_range   = random.choice(["3+", "7+", "14+", "18+"])
        genre_data.append((age_range, description, genre_id))
        genre_id += 1

    cursor.executemany(
        'INSERT INTO "GENRE" ("age_range", "description", "id") VALUES (?, ?, ?)',
        genre_data
    )

    all_genre_ids = get_everything(cursor, 'SELECT "id" FROM "GENRE"')

    # ---------- PUBLICATION ----------
    used_isbns = set()
    publications = []
    for _ in range(20):
        while True:
            isbn = random.randint(1_000_000_000_000, 9_999_999_999_999)
            if isbn not in used_isbns:
                used_isbns.add(isbn)
                break

        title = random.choice(book_titles)
        price = round(random.uniform(5.0, 200.0), 2)
        stock = random.randint(0, 1000)
        chosen_genre_id = random.choice(all_genre_ids)

        publications.append((title, isbn, price, stock, chosen_genre_id))

    cursor.executemany(
        'INSERT INTO "PUBLICATION" ("title", "isbn", "price", "stock", "genre-id") VALUES (?, ?, ?, ?, ?)',
        publications
    )

    all_isbns = get_everything(cursor, 'SELECT "isbn" FROM "PUBLICATION"')

    # Build a dictionary of { isbn: price } and { isbn: stock }
    cursor.execute('SELECT "isbn", "price" FROM "PUBLICATION"')
    all_isbn_price = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute('SELECT "isbn", "stock" FROM "PUBLICATION"')
    all_isbn_stock = {row[0]: row[1] for row in cursor.fetchall()}

    # ---------- CONTRACT ----------
    contracts = []
    contract_id = 1
    for _ in range(30):
        payment = round(random.uniform(1000.0, 10000.0), 2)
        start = random_date(datetime(2020, 1, 1), datetime(2023, 12, 31))
        expiration = start + timedelta(days=random.randint(30, 365))
        partner_tax_id   = random.choice(all_partner_tax_ids)
        publication_isbn = random.choice(list(used_isbns))
        description = f"Contract for publication {publication_isbn}"

        contracts.append((
            payment,
            start.strftime("%Y-%m-%d"),
            expiration.strftime("%Y-%m-%d"),
            contract_id,
            description,
            partner_tax_id,
            publication_isbn
        ))
        contract_id += 1

    cursor.executemany(
        'INSERT INTO "CONTRACT" '
        '("payment", "start_date", "expiration_date", "id", "description", '
        '"Partner_Tax_Id", "Publication-isbn") '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        contracts
    )

    # ---------- CLIENT_ORDERS ----------
    used_client_book_pairs = set()
    client_orders = []
    for _ in range(20):
        while True:
            client_tax_id = random.choice(all_client_tax_ids)
            publication_isbn = random.choice(list(used_isbns))
            if (client_tax_id, publication_isbn) not in used_client_book_pairs:
                used_client_book_pairs.add((client_tax_id, publication_isbn))
                break

        quantity = random.randint(10, 50)
        order_date = random_date(datetime(2021, 1, 1), datetime(2023, 12, 31))
        delivery_date = order_date + timedelta(days=random.randint(1, 30))
        total_cost = round(all_isbn_price[publication_isbn] * quantity, 2)

        client_orders.append((
            client_tax_id,
            publication_isbn,
            quantity,
            order_date.strftime("%Y-%m-%d"),
            delivery_date.strftime("%Y-%m-%d"),
            total_cost
        ))

    cursor.executemany(
        'INSERT INTO "client_orders" ("Client_Tax_ID", "Publication-isbn", "quantity", '
        '"order date", "delivery date", "payment") '
        'VALUES (?, ?, ?, ?, ?, ?)',
        client_orders
    )

    # Collect total orders for each ISBN
    cursor.execute(
        'SELECT "Publication-isbn", SUM("quantity") '
        'FROM "client_orders" '
        'GROUP BY "Publication-isbn"'
    )
    all_isbn_orders_map = {row[0]: row[1] for row in cursor.fetchall()}

    # ---------- CONTRIBUTES ----------
    used_contrib = set()
    contributes_data = []
    for _ in range(40):
        while True:
            partner_tax_id = random.choice(all_partner_tax_ids)
            chosen_isbn = random.choice(all_isbns)
            if (partner_tax_id, chosen_isbn) not in used_contrib:
                used_contrib.add((partner_tax_id, chosen_isbn))
                break

        start_date = random_date(datetime(2021, 1, 1), datetime(2023, 12, 31))
        completion_date = start_date + timedelta(days=random.randint(15, 2 * 365))
        eta = random_date(start_date, completion_date)
        paid = random.choice([0, 1])  # boolean in SQLite can be 0 or 1

        contributes_data.append((
            partner_tax_id,
            chosen_isbn,
            eta.strftime("%Y-%m-%d"),
            start_date.strftime("%Y-%m-%d"),
            completion_date.strftime("%Y-%m-%d"),
            paid
        ))

    cursor.executemany(
        'INSERT INTO "contributes" '
        '("Partner_TaxId", "Publication-isbn", "estimated_completion_date", '
        '"start_date", "completion_date", "payment") '
        'VALUES (?, ?, ?, ?, ?, ?)',
        contributes_data
    )

    # ---------- ORDER_PRINTING_HOUSE ----------
    used_ph_isbn_pairs = set()
    printing_orders = []
    for chosen_isbn in all_isbns:
        # If the ISBN is present in client_orders, we may need more copies
        if chosen_isbn in all_isbn_orders_map:
            total_needed = all_isbn_stock[chosen_isbn] + all_isbn_orders_map[chosen_isbn]
            num_partial_orders = random.randint(1, 3)
            partial_quantities = random_partition(total_needed, num_partial_orders)

            # We can pick a 'worst-case' delivery date from the client_orders for that ISBN
            # so that printing finishes before that date
            # (the logic can vary, here is an example picking the earliest or latest date, etc.)
            client_deliv_str = cursor.execute(
                'SELECT min("delivery date") FROM "client_orders" WHERE "Publication-isbn" = ? ',
                (chosen_isbn,)
            ).fetchone()[0]
            client_deliv_date = datetime.strptime(client_deliv_str, "%Y-%m-%d")

            for q in partial_quantities:
                while True:
                    printing_id = random.choice(all_printing_ids)
                    if (printing_id, chosen_isbn) not in used_ph_isbn_pairs:
                        used_ph_isbn_pairs.add((printing_id, chosen_isbn))
                        break

                # Ensure printing order/delivery occurs before the client delivery
                deliver_date = client_deliv_date - timedelta(days=random.randint(1, 60))
                order_date   = deliver_date - timedelta(days=random.randint(1, 30))

                base_cost_per_unit = random.uniform(0.2 * all_isbn_price[chosen_isbn],
                                                    0.6 * all_isbn_price[chosen_isbn])
                total_cost = round(base_cost_per_unit * q, 2)

                printing_orders.append((
                    printing_id,
                    chosen_isbn,
                    order_date.strftime("%Y-%m-%d"),
                    deliver_date.strftime("%Y-%m-%d"),
                    q,
                    total_cost
                ))
        else:
            # If no client orders exist for this ISBN, just do one printing_order
            while True:
                printing_id = random.choice(all_printing_ids)
                if (printing_id, chosen_isbn) not in used_ph_isbn_pairs:
                    used_ph_isbn_pairs.add((printing_id, chosen_isbn))
                    break

            order_dt = random_date(datetime(2021, 1, 1), datetime(2023, 12, 31))
            deliver_dt = order_dt + timedelta(days=random.randint(1, 30))
            quantity = all_isbn_stock[chosen_isbn]

            base_cost_per_unit = random.uniform(0.2 * all_isbn_price[chosen_isbn],
                                                0.6 * all_isbn_price[chosen_isbn])
            total_cost = round(base_cost_per_unit * quantity, 2)

            printing_orders.append((
                printing_id,
                chosen_isbn,
                order_dt.strftime("%Y-%m-%d"),
                deliver_dt.strftime("%Y-%m-%d"),
                quantity,
                total_cost
            ))

    cursor.executemany(
        'INSERT INTO "order_printing_house" '
        '("Printing-id", "Publication-isbn", "order date", "delivery date", "quntity", "cost") '
        'VALUES (?, ?, ?, ?, ?, ?)',
        printing_orders
    )

    # ---------- COMMUNICATION-CLIENT ----------
    client_contacts = []
    for tax_id in all_client_tax_ids:
        for _ in range(random.randint(1, 3)):
            client_contacts.append((tax_id, random_phone()))

    cursor.executemany(
        'INSERT INTO "communication-CLIENT" ("Clinet_Tax_ID", "Client_Comm") VALUES (?, ?)',
        client_contacts
    )

    # ---------- COMMUNICATION-PARTNER ----------
    partner_contacts = []
    for tax_id in all_partner_tax_ids:
        for _ in range(random.randint(1, 3)):
            partner_contacts.append((tax_id, random_phone()))

    cursor.executemany(
        'INSERT INTO "communication-PARTNER" ("Partner_Tax_Id", "partner_comm") VALUES (?, ?)',
        partner_contacts
    )

    # ---------- COMMUNICATION-PRINTING ----------
    printing_contacts = []
    for p_id in all_printing_ids:
        for _ in range(random.randint(1, 3)):
            printing_contacts.append((p_id, random_phone()))

    cursor.executemany(
        'INSERT INTO "communication-PRINTING" ("Printing-id", "Printing_comm") VALUES (?, ?)',
        printing_contacts
    )

    # ----------- Final Commit -----------
    connection.commit()
    connection.close()

    print("Database populated successfully with the new schema!")

# ----------------------------------------- #
# 4) Main                                   #
# ----------------------------------------- #

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #script_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
#     print(f"Current working directory: {cwd}")
    db_path = cwd + "/publishing_house.db"
    schema_file_path = script_dir + "/schema.sql"
    #db_path = "publishing_house.db"
    #schema_file_path = "schema.sql"

    # 1) Drop old tables (if exist)
    drop_tables(db_path)

    # 2) Create tables from new schema
    create_database(db_path, schema_file_path)

    # 3) Populate them with random data
    populate_database(db_path)

    sleep(2)

if __name__ == "__main__":
    main()
