import sqlite3
import random
from datetime import datetime, timedelta
from time import sleep

# Datasets for generating realistic names and titles
first_names = ["Alan", "John", "Sarah", "Emily", "Michael", "Sophia", "Robert", "Jessica", "David", "Laura"]
last_names = ["Wake", "Smith", "Johnson", "Brown", "Williams", "Taylor", "Anderson", "Lee", "Martinez", "Hernandez"]
categories = ["Fiction", "Science Fiction", "Fantasy", "Biography", "Mystery", "History", "Children", "Romance"]
collaborator_categories = ["Συγγραφέας", "Γραφίστας", "Επιμελητής", "Μεταφραστής"]
printing_house_capabilities = ["Offset Printing", "Digital Printing", "Foil Stamping", "Custom Packaging Solutions", "Eco-Friendly Printing"]
locations = ["Athens", "New York", "Paris", "Berlin", "Tokyo", "Sydney", "London", "Madrid", "Rome", "Toronto"]
book_titles = [
    "The Great Adventure", "Mysterious Island", "Forgotten Tales", "Space and Beyond", "Hidden Treasures", "The Last Dream",
    "Echoes of Time", "Reflections of the Mind", "Under the Stars", "Wonders of the Universe"
    ]
bookstores_names = [
    "The Book Nook", "Page Turners", "Chapters & Tales", "Novel Ideas", "Bound & Beyond", "The Reading Room", "Ink & Paper",
    "The Literary Loft", "Village Books", "Cornerstone Books", "Riverstone Reads", "The Story House", "Turning Pages",
    "City Reads", "The Dusty Cover", "Wordsworth Books", "The Quiet Corner", "Once Upon a Book", "The Bookmark", "Starlight Books"
    ]

def create_database(db_path, schema_file_path):
    with open(schema_file_path, 'r', encoding='utf-8') as schema_file:
        schema_content = schema_file.read()

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.executescript(schema_content)
    connection.commit()
    connection.close()
    print("Database and tables created successfully!")

    return;

def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)

    return start + timedelta(days=random_days);

def random_afm():
    return random.randint(100_000_000, 999_999_999);

def random_phone():
    return random.choice([random.randint(69_000_00000, 699_999_9999), random.randint(2651_000000, 2651_999999)]);

def populate_database(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # ============================================================================================================================
    # 1. ΣΥΝΕΡΓΑΤΗΣ (COLLABORATORS)
    # ============================================================================================================================
    collaborator_afms = set()
    collaborators = []
    for _ in range(10):
        while True:
            afm_value = random_afm()
            if afm_value not in collaborator_afms:
                collaborator_afms.add(afm_value)
                break;
        
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        comments = f"Σχόλια για συνεργάτη με ΑΦΜ {afm_value}"

        collaborators.append((name, afm_value, random.choice(collaborator_categories), comments))
    
    cursor.executemany('INSERT INTO "ΣΥΝΕΡΓΑΤΗΣ" ("ονομασία", "α.φ.μ.", "ειδίκευση", "σχόλια") VALUES (?, ?, ?, ?)', collaborators)

    # Grab the AFMs we just inserted! We will use them later!
    cursor.execute('SELECT "α.φ.μ." FROM "ΣΥΝΕΡΓΑΤΗΣ"')
    all_collaborator_afms = [row[0] for row in cursor.fetchall()]

    # ============================================================================================================================
    # 2. ΠΕΛΑΤΗΣ (CLIENT)
    # ============================================================================================================================
    client_afms = set()
    clients = []
    for _ in range(15):
        while True:
            afm_value = random_afm()
            ################################### No overlap with collaborator AFMs!
            if afm_value not in client_afms and afm_value not in collaborator_afms:
                client_afms.add(afm_value)
                break;
        
        name = f"{random.choice(bookstores_names)}"

        clients.append((afm_value, name, random.choice(locations)))
    
    cursor.executemany('INSERT INTO "ΠΕΛΑΤΗΣ" ("α.φ.μ.", "ονομασία", "τοποθεσία") VALUES (?, ?, ?)', clients)

    # Grab the AFMs we just inserted! We will use them later!
    cursor.execute('SELECT "α.φ.μ." FROM "ΠΕΛΑΤΗΣ"')
    all_client_afms = [row[0] for row in cursor.fetchall()]

    # ============================================================================================================================
    # 3. ΤΥΠΟΓΡΑΦΕΙΟ (PRINTING HOUSE)
    # ============================================================================================================================
    new_printing_ids = set()
    printing_houses = []
    for _ in range(5):
        while True:
            printing_id = random.randint(1, 500)
            if printing_id not in new_printing_ids:
                new_printing_ids.add(printing_id)
                break;
        
        capabilities = random.choice(printing_house_capabilities)

        printing_houses.append((random.choice(locations), printing_id, capabilities))
    
    cursor.executemany('INSERT INTO "ΤΥΠΟΓΡΑΦΕΙΟ" ("τοποθεσία", "id", "δυνατότητες") VALUES (?, ?, ?)', printing_houses)

    # Grab the IDs we just inserted! We will use them later!
    cursor.execute('SELECT "id" FROM "ΤΥΠΟΓΡΑΦΕΙΟ"')
    all_printing_ids = [row[0] for row in cursor.fetchall()]

    # ============================================================================================================================
    # 4. ΕΙΔΟΣ (CATEGORY)
    # ============================================================================================================================
    category_ids = set()
    category_data = []
    new_id = 1
    for category in categories:            
        category_ids.add(new_id)
        new_id += 1

        description = f"Books in the {category.lower()} genre"

        category_data.append((category, description, new_id))
    
    cursor.executemany('INSERT INTO "ΕΙΔΟΣ" ("ηλικιακό εύρος", "περιγραφή", "id") VALUES (?, ?, ?)', category_data)

    # Grab the category IDs we just inserted! We will use them later!
    cursor.execute('SELECT "id" FROM "ΕΙΔΟΣ"')
    all_category_ids = [row[0] for row in cursor.fetchall()]

    # ============================================================================================================================
    # 5. ΕΝΤΥΠΟ (BOOK/PRINTED MATERIAL)
    # ============================================================================================================================
    entypa = []
    used_isbn = set()
    for _ in range(20):
        while True:
            isbn = random.randint(1_000_000_000_000, 9_999_999_999_999) # International Standard Book Number (ISBN)
            if isbn not in used_isbn:
                used_isbn.add(isbn)
                break;

        title = random.choice(book_titles)
        price = round(random.uniform(5.0, 200.0), 2) # Στην αρχική έκδοση, πετούσε κάτι αριθμούς με 10 ψηφία χαχαχαχα
        stock = random.randint(0, 1_000)
        cat_id = random.choice(all_category_ids)

        entypa.append((title, isbn, price, stock, cat_id))

    cursor.executemany('INSERT INTO "ΕΝΤΥΠΟ" ("τίτλος", "isbn", "τιμή", "stock", "ΕΙΔΟΣ-id") VALUES (?, ?, ?, ?, ?)', entypa)

    # Grab all ISBNs we just inserted! We will use them later!
    cursor.execute('SELECT "isbn" FROM "ΕΝΤΥΠΟ"')
    all_isbn = [row[0] for row in cursor.fetchall()]

    # ============================================================================================================================
    # Populate “επικοινωνία-*” tables with random phone numbers
    # ============================================================================================================================

    # --- επικοινωνία-ΠΕΛΑΤΗΣ ---
    client_contacts = []
    for afm in client_afms:
        for _ in range(random.randint(1, 3)):
            client_contacts.append((afm, random_phone()))
    cursor.executemany('INSERT INTO "επικοινωνία-ΠΕΛΑΤΗΣ" ("ΠΕΛΑΤΗΣ-α.φ.μ.", "ΠΕΛΑΤΗΣ-επικοινωνία") VALUES (?, ?)', client_contacts)

    # --- επικοινωνία-ΣΥΝΕΡΓΑΤΗΣ ---
    collaborator_contacts = []
    for afm in collaborator_afms:
        for _ in range(random.randint(1, 3)):
            collaborator_contacts.append((afm, random_phone()))
    cursor.executemany('INSERT INTO "επικοινωνία-ΣΥΝΕΡΓΑΤΗΣ" ("ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.", "ΣΥΝΕΡΓΑΤΗΣ-επικοινωνία") VALUES (?, ?)', collaborator_contacts)

    # --- επικοινωνία-ΤΥΠΟΓΡΑΦΕΙΟ ---
    printing_contacts = []
    for pid in new_printing_ids:
        for _ in range(random.randint(1, 3)):
            printing_contacts.append((pid, random_phone()))
    cursor.executemany('INSERT INTO "επικοινωνία-ΤΥΠΟΓΡΑΦΕΙΟ" ("ΤΥΠΟΓΡΑΦΕΙΟ-id", "ΤΥΠΟΓΡΑΦΕΙΟ-επικοινωνία") VALUES (?, ?)', printing_contacts)

    # ============================================================================================================================
    # 6. ΣΥΜΒΟΛΑΙΟ (CONTRACT) - link collaborator + entypo
    # ============================================================================================================================
    contracts = []
    contract_id_used = set()
    for _ in range(40):
        while True:
            contract_id = random.randint(1, 10_000)
            # We'll allow the same contract_id *as long as the 3-part PK* is unique
            # but let's keep it simple and just ensure unique ID for demonstration. Κάτι πίπες, πρέπει να έχει γίνει μαλακία στο schema :)
            if contract_id not in contract_id_used:
                contract_id_used.add(contract_id)
                break;
        
        fee = round(random.uniform(500.0, 5_000.0), 2)
        start_date = random_date(datetime(2015, 1, 1), datetime(2023, 12, 31))
        duration_date = start_date + timedelta(days = random.randint(30, 2 * 365)) # Μπράβο στην python που τα έχει όλα έτοιμα!
        coll_afm = random.choice(all_collaborator_afms)
        chosen_isbn = random.choice(all_isbn)
        description = f"Contract for ISBN {chosen_isbn}"
        
        contracts.append((
            fee,
            start_date.strftime("%Y-%m-%d"),
            duration_date.strftime("%Y-%m-%d"),
            contract_id,
            description,
            coll_afm,
            chosen_isbn
        ))

    cursor.executemany(
        'INSERT INTO "ΣΥΜΒΟΛΑΙΟ" '
        '("αμοιβή", "ημ. έναρξης", "διάρκεια", "id", "περιγραφή", '
        '"ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.", "ΕΝΤΥΠΟ-isbn") VALUES (?, ?, ?, ?, ?, ?, ?)',
        contracts
    )

    # ============================================================================================================================
    # 7. ζητάει (CLIENT ASKS FOR/ORDERS A BOOK)
    # ============================================================================================================================
    used_client_book_pairs = set()
    orders = []
    for _ in range(20):
        while True:
            c_afm = random.choice(all_client_afms)
            chosen_isbn = random.choice(all_isbn)
            if (c_afm, chosen_isbn) not in used_client_book_pairs:
                used_client_book_pairs.add((c_afm, chosen_isbn))
                break;
        
        quantity = random.randint(10, 50)
        order_date = random_date(datetime(2021, 1, 1), datetime(2023, 12, 31))
        delivery_date = order_date + timedelta(days = random.randint(1, 30))

        # Get the price of the chosen book from the ΕΝΤΥΠΟ table
        cursor.execute('SELECT τιμή FROM "ΕΝΤΥΠΟ" WHERE isbn = ?', (chosen_isbn,))
        price_of_book = cursor.fetchone()[0]
        total_cost = round(price_of_book * quantity, 2)
        
        orders.append((
            c_afm,
            chosen_isbn,
            quantity,
            order_date.strftime("%Y-%m-%d"),
            delivery_date.strftime("%Y-%m-%d"),
            total_cost
        ))

    cursor.executemany(
        'INSERT INTO "ζητάει" '
        '("ΠΕΛΑΤΗΣ-α.φ.μ.", "ΕΝΤΥΠΟ-isbn", "ποσότητα", '
        '"ημ. παραγγελίας", "ημ. παράδοσης ", "χρηματικό ποσό") '
        'VALUES (?, ?, ?, ?, ?, ?)',
        orders
    )

    # ============================================================================================================================
    # 8. επεξεργαζεται (COLLABORATOR WORKING ON A BOOK)
    # ============================================================================================================================
    used_edit_book_pairs = set()
    processes = []
    for _ in range(40):
        while True:
            coll_afm = random.choice(all_collaborator_afms)
            chosen_isbn = random.choice(all_isbn)
            if (coll_afm, chosen_isbn) not in used_edit_book_pairs:
                used_edit_book_pairs.add((coll_afm, chosen_isbn))
                break;
        
        start_date = random_date(datetime(2021, 1, 1), datetime(2023, 12, 31))
        completion_date = start_date + timedelta(days = random.randint(15, 2 * 365)) # Το άλλαξα σε 2 * 365 το μέγιστο, επειδή τόσο είναι και το contract duration
        eta_date = completion_date - timedelta(days = random.randint(0, 2 * 365))
        paid = random.choice([0, 1])  # boolean in SQLite can be stored as 0/1

        processes.append((
            coll_afm,
            chosen_isbn,
            eta_date.strftime("%Y-%m-%d"),
            start_date.strftime("%Y-%m-%d"),
            completion_date.strftime("%Y-%m-%d"),
            paid
        ))
    
    cursor.executemany(
        'INSERT INTO "επεξεργαζεται" '
        '("ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.", "ΕΝΤΥΠΟ-isbn", "ΕΤΑ", "ημ. έναρξης", '
        '"ημ. ολοκλήρωσης", "πληρωμή") VALUES (?, ?, ?, ?, ?, ?)',
        processes
    )

    # ============================================================================================================================
    # 9. παραγγέλνει (PRINTING HOUSE ORDERS A BOOK)
    # ============================================================================================================================
    used_ph_isbn_pairs = set()
    printing_orders = []
    for _ in range(20):
        while True:
            ph_id = random.choice(all_printing_ids)
            chosen_isbn = random.choice(all_isbn)
            if (ph_id, chosen_isbn) not in used_ph_isbn_pairs:
                used_ph_isbn_pairs.add((ph_id, chosen_isbn))
                break;

        order_date = random_date(datetime(2021, 1, 1), datetime(2023, 12, 31))
        delivery_date = order_date + timedelta(days = random.randint(5, 60))
        quantity = random.randint(1_000, 10_000)

        # Get the price of the chosen book from the ΕΝΤΥΠΟ table
        cursor.execute('SELECT τιμή FROM "ΕΝΤΥΠΟ" WHERE isbn = ?', (chosen_isbn,))
        price_of_book = cursor.fetchone()[0]
        # Όρισε 1 κόστος παραγωγής (ανά τεμάχιο) που να έχει κάποια σχέση με την τιμή πώλησης!
        # Παράδειγμα: από το 20% έως 80% της τιμής λιανικής
        base_cost_per_unit = random.uniform(0.2 * price_of_book, 0.8 * price_of_book)
        total_cost = round(base_cost_per_unit * quantity, 2)

        printing_orders.append((
            ph_id,
            chosen_isbn,
            order_date.strftime("%Y-%m-%d"),
            delivery_date.strftime("%Y-%m-%d"),
            quantity,
            total_cost
        ))
    
    cursor.executemany(
        'INSERT INTO "παραγγέλνει" '
        '("ΤΥΠΟΓΡΑΦΕΙΟ-id", "ΕΝΤΥΠΟ-isbn", "ημ. παραγγελίας", '
        '"ημ. παράδοσης", "ποσότητα", "κόστος") '
        'VALUES (?, ?, ?, ?, ?, ?)',
        printing_orders
    )

    # ============================================================================================================================
    # Final Commit
    # ============================================================================================================================
    connection.commit()
    connection.close()
    print("Database populated with synthetic data successfully.")

    return;

def drop_tables(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Disable foreign key checks while dropping to avoid dependency errors
    cursor.execute("PRAGMA foreign_keys = OFF;")

    statements = [
        'DROP TABLE IF EXISTS "επικοινωνία-ΠΕΛΑΤΗΣ";',
        'DROP TABLE IF EXISTS "επικοινωνία-ΣΥΝΕΡΓΑΤΗΣ";',
        'DROP TABLE IF EXISTS "επικοινωνία-ΤΥΠΟΓΡΑΦΕΙΟ";',
        'DROP TABLE IF EXISTS "παραγγέλνει";',
        'DROP TABLE IF EXISTS "επεξεργαζεται";',
        'DROP TABLE IF EXISTS "ζητάει";',
        'DROP TABLE IF EXISTS "ΣΥΜΒΟΛΑΙΟ";',
        'DROP TABLE IF EXISTS "ΕΝΤΥΠΟ";',
        'DROP TABLE IF EXISTS "ΕΙΔΟΣ";',
        'DROP TABLE IF EXISTS "ΤΥΠΟΓΡΑΦΕΙΟ";',
        'DROP TABLE IF EXISTS "ΠΕΛΑΤΗΣ";',
        'DROP TABLE IF EXISTS "ΣΥΝΕΡΓΑΤΗΣ";'
    ]
    
    for sql in statements:
        cursor.execute(sql)
    
    # Re-enable foreign key checks
    cursor.execute("PRAGMA foreign_keys = ON;")

    connection.commit()
    connection.close()

    print("All tables dropped successfully!\n")

    return;

def main():
    db_path = "publishing_house.db"
    schema_file_path = "schema.sql"

    drop_tables(db_path) # Drop old tables

    create_database(db_path, schema_file_path)
    populate_database(db_path)

    sleep(1)

    return;

if __name__ == "__main__":
    main()
