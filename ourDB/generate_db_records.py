import sqlite3
import random
from datetime import datetime, timedelta
from time import sleep

# Διαβάζει τα δεδομένα από 1 αρχείο κειμένου και τα επιστρέφει ως λίστα (χρησιμοποιείτε για τα datasets)
def read_data_from_file(file_path):
    file_path = f"datasets/{file_path}"
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()];

def create_database(db_path, schema_file_path):
    with open(schema_file_path, 'r', encoding='utf-8') as schema_file:
        schema_content = schema_file.read()

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.executescript(schema_content)
    connection.commit()
    connection.close()
    print("Η ΒΔ/πίνακες δημιουργήθηκαν επιτυχώς!")

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
    # Datasets για τη δημιουργία ρεαλιστικών ονομάτων και τίτλων
    first_names = read_data_from_file('first_names.txt')
    last_names = read_data_from_file('last_names.txt')
    categories = read_data_from_file('categories.txt')
    collaborator_categories = ["Συγγραφέας", "Γραφίστας", "Επιμελητής", "Μεταφραστής"]
    printing_house_capabilities = ["Offset Printing", "Digital Printing", "Foil Stamping",
                                "Custom Packaging Solutions", "Eco-Friendly Printing"]
    locations = read_data_from_file('locations.txt')
    book_titles = read_data_from_file('book_titles.txt')
    bookstores_names = read_data_from_file('bookstores_names.txt')

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor() # Ο cursor είναι ένας δείκτης που δείχνει σε μια συγκεκριμένη γραμμή του πίνακα

    # ---------- ΣΥΝΕΡΓΑΤΗΣ ---------- # Α.Φ.Μ., Ονομασία, Ειδίκευση, Σχόλια
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
    
    cursor.executemany(
        'INSERT INTO "ΣΥΝΕΡΓΑΤΗΣ" ("ονομασία", "α.φ.μ.", "ειδίκευση", "σχόλια") \
        VALUES (?, ?, ?, ?)', collaborators
        ) # Στο VALUES (?, ?, ?, ?), τα ? είναι placeholders για τα πραγματικά δεδομένα που θα εισαχθοϋν!

    # Βρες όλα τα ΑΦΜ των συνεργατών που μόλις εισήχθησαν! Θα τα χρειαστούμε αργότερα!
    cursor.execute('SELECT "α.φ.μ." FROM "ΣΥΝΕΡΓΑΤΗΣ"')
    all_collaborator_afms = [row[0] for row in cursor.fetchall()]

    # ---------- ΠΕΛΑΤΗΣ ---------- # Α.Φ.Μ., Ονομασία, Τοποθεσία
    client_afms = set()
    clients = []
    for _ in range(15):
        while True:
            afm_value = random_afm()
            ################################### Δεν θέλουμε να υπάρχει ίδιο ΑΦΜ με συνεργάτη!
            if afm_value not in client_afms and afm_value not in all_collaborator_afms:
                client_afms.add(afm_value)
                break;
        
        name = f"{random.choice(bookstores_names)}"

        clients.append((afm_value, name, random.choice(locations)))
    
    cursor.executemany(
        'INSERT INTO "ΠΕΛΑΤΗΣ" ("α.φ.μ.", "ονομασία", "τοποθεσία") \
        VALUES (?, ?, ?)', clients
        )

    # Βρες όλα τα ΑΦΜ των πελατών που μόλις εισήχθησαν! Θα τα χρειαστούμε!
    cursor.execute('SELECT "α.φ.μ." FROM "ΠΕΛΑΤΗΣ"')
    all_client_afms = [row[0] for row in cursor.fetchall()]

    # ---------- ΤΥΠΟΓΡΑΦΕΙΟ ---------- # Τοποθεσία, ID, Δυνατότητες
    printing_ids = set()
    printing_houses = []
    for _ in range(5):
        while True:
            printing_id = random.randint(1, 500)
            if printing_id not in printing_ids:
                printing_ids.add(printing_id)
                break;
        
        capabilities = random.choice(printing_house_capabilities)

        printing_houses.append((random.choice(locations), printing_id, capabilities))
    
    cursor.executemany(
        'INSERT INTO "ΤΥΠΟΓΡΑΦΕΙΟ" ("τοποθεσία", "id", "δυνατότητες") \
        VALUES (?, ?, ?)', printing_houses
        )

    # Βρες όλα τα IDs των τυπογραφείων που μόλις εισήχθησαν.
    cursor.execute('SELECT "id" FROM "ΤΥΠΟΓΡΑΦΕΙΟ"')
    all_printing_ids = [row[0] for row in cursor.fetchall()]

    # ---------- ΕΙΔΟΣ ---------- # Ηλικιακό εύρος, Περιγραφή, ID
    category_ids = set()
    category_data = []
    new_id = 1
    for category in categories:            
        category_ids.add(new_id)
        new_id += 1

        description = f"Books in the {category.lower()} genre"

        category_data.append((category, description, new_id))
    
    cursor.executemany(
        'INSERT INTO "ΕΙΔΟΣ" ("ηλικιακό εύρος", "περιγραφή", "id") \
        VALUES (?, ?, ?)', category_data
        )

    # Βρες όλα τα IDs των ειδών που μόλις εισήχθησαν.
    cursor.execute('SELECT "id" FROM "ΕΙΔΟΣ"')
    all_category_ids = [row[0] for row in cursor.fetchall()]

    # ---------- ΕΝΤΥΠΟ ---------- # Τίτλος, ISBN, Τιμή, Stock, ΕΙΔΟΣ-id
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

    cursor.executemany(
        'INSERT INTO "ΕΝΤΥΠΟ" ("τίτλος", "isbn", "τιμή", "stock", "ΕΙΔΟΣ-id") \
        VALUES (?, ?, ?, ?, ?)', entypa
        )

    # Βρες όλα τα ISBNs που μόλις εισήχθησαν.
    cursor.execute('SELECT "isbn" FROM "ΕΝΤΥΠΟ"')
    all_isbn = [row[0] for row in cursor.fetchall()]

    # Αντιστοίχισε τα ISBNs με τα αποθέματα των βιβλίων!
    cursor.execute('SELECT "isbn", "stock" FROM "ΕΝΤΥΠΟ"')
    all_isbn_stock = {row[0]: row[1] for row in cursor.fetchall()}

    # ---------- ΣΥΜΒΟΛΑΙΟ ---------- # Αμοιβή, Ημ. Έναρξης, Διάρκεια, ID, Περιγραφή, ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ., ΕΝΤΥΠΟ-isbn
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
        '"ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.", "ΕΝΤΥΠΟ-isbn") '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        contracts
    )

    # ---------- ζητάει ---------- # ΠΕΛΑΤΗΣ-α.φ.μ., ΕΝΤΥΠΟ-isbn, ποσότητα, ημ. παραγγελίας, ημ. παράδοσης, χρηματικό ποσό
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

        # Βρες την τιμή του επιλεγμένου βιβλίου από τον πίνακα ΕΝΤΥΠΟ
        cursor.execute('SELECT τιμή FROM "ΕΝΤΥΠΟ" WHERE isbn = ?', (chosen_isbn,))
        price_of_book = cursor.fetchone()[0] # Προσθέτω το [0] γιατί το fetchone() επιστρέφει tuple
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
        '"ημ. παραγγελίας", "ημ. παράδοσης", "χρηματικό ποσό") '
        'VALUES (?, ?, ?, ?, ?, ?)',
        orders
    )

    # Βρες όλα τα ISBNs που έχουν παραγγελθεί από τους πελάτες.
    cursor.execute('SELECT "ΕΝΤΥΠΟ-isbn" FROM "ζητάει"')
    all_isbn_order = [row[0] for row in cursor.fetchall()]

    # Αντιστοίχισε τα ISBNs με το πλήθος των βιβλίων που έχουν παραγγελθεί από τους πελάτες!
    cursor.execute('SELECT "ΕΝΤΥΠΟ-isbn", SUM("ποσότητα") FROM "ζητάει" GROUP BY "ΕΝΤΥΠΟ-isbn"')
    all_isbn_quantity_order = {row[0]: row[1] for row in cursor.fetchall()}

    # ---------- επεξεργαζεται ---------- # ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ., ΕΝΤΥΠΟ-isbn, ΕΤΑ, ημ. έναρξης, ημ. ολοκλήρωσης, πληρωμή
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
        eta_date = completion_date - timedelta(days = random.randint(1, 2 * 365))
        paid = random.choice([0, 1])  # Το boolean στην SQLite μπορεί να αντιστοιχεί σε 0 ή 1

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
        '"ημ. ολοκλήρωσης", "πληρωμή") '
        'VALUES (?, ?, ?, ?, ?, ?)',
        processes
    )

    # ---------- παραγγέλνει ---------- # ΤΥΠΟΓΡΑΦΕΙΟ-id, ΕΝΤΥΠΟ-isbn, ημ. παραγγελίας, ημ. παράδοσης, ποσότητα, κόστος
    used_ph_isbn_pairs = set()
    printing_orders = []
    for _ in range(20):
        while True:
            ph_id = random.choice(all_printing_ids)
            chosen_isbn = random.choice(all_isbn_order)
            if (ph_id, chosen_isbn) not in used_ph_isbn_pairs:
                used_ph_isbn_pairs.add((ph_id, chosen_isbn))
                break;

        client_order_delivery_date = cursor.execute(
            'SELECT "ημ. παράδοσης" \
            FROM "ζητάει" \
            WHERE "ΕΝΤΥΠΟ-isbn" = ?', (chosen_isbn,)
            ).fetchone()[0]
        client_order_delivery_date = datetime.strptime(client_order_delivery_date, "%Y-%m-%d")
        delivery_date = client_order_delivery_date - timedelta(days = random.randint(1, 60))
        order_date = delivery_date - timedelta(days = random.randint(1, 30))
        quantity = all_isbn_stock[chosen_isbn] + all_isbn_quantity_order[chosen_isbn] # Σύνολο αποθέματος + ποσότητα που έχει ζητηθεί!

        # Βρες την τιμή του επιλεγμένου βιβλίου από τον πίνακα ΕΝΤΥΠΟ
        cursor.execute('SELECT τιμή FROM "ΕΝΤΥΠΟ" WHERE isbn = ?', (chosen_isbn,))
        price_of_book = cursor.fetchone()[0]
        # Όρισε 1 κόστος παραγωγής (ανά τεμάχιο) που να έχει κάποια σχέση με την τιμή πώλησης!
        # Συγκεκριμένα, από 20% έως 80% της τιμής πώλησης.
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

    # ======================================================= #
    # Γέμισε τους “επικοινωνία-*” πίνακες με τυχαία τηλέφωνα! #
    # ======================================================= #

    # --- επικοινωνία-ΠΕΛΑΤΗΣ ---
    client_contacts = []
    for afm in all_client_afms:
        for _ in range(random.randint(1, 3)):
            client_contacts.append((afm, random_phone()))
    cursor.executemany(
        'INSERT INTO "επικοινωνία-ΠΕΛΑΤΗΣ" ("ΠΕΛΑΤΗΣ-α.φ.μ.", "ΠΕΛΑΤΗΣ-επικοινωνία") \
        VALUES (?, ?)', client_contacts
        )

    # --- επικοινωνία-ΣΥΝΕΡΓΑΤΗΣ ---
    collaborator_contacts = []
    for afm in all_collaborator_afms:
        for _ in range(random.randint(1, 3)):
            collaborator_contacts.append((afm, random_phone()))
    cursor.executemany(
        'INSERT INTO "επικοινωνία-ΣΥΝΕΡΓΑΤΗΣ" ("ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.", "ΣΥΝΕΡΓΑΤΗΣ-επικοινωνία") \
        VALUES (?, ?)', collaborator_contacts
        )

    # --- επικοινωνία-ΤΥΠΟΓΡΑΦΕΙΟ ---
    printing_contacts = []
    for pid in all_printing_ids:
        for _ in range(random.randint(1, 3)):
            printing_contacts.append((pid, random_phone()))
    cursor.executemany(
        'INSERT INTO "επικοινωνία-ΤΥΠΟΓΡΑΦΕΙΟ" ("ΤΥΠΟΓΡΑΦΕΙΟ-id", "ΤΥΠΟΓΡΑΦΕΙΟ-επικοινωνία") \
        VALUES (?, ?)', printing_contacts
        )

    # ============ #
    # Final Commit #
    # ============ #
    connection.commit()
    connection.close()
    print("Η ΒΔ γέμισε με δεδομένα επιτυχώς!")

    return;

def drop_tables(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Απενεργοποίησε τους έλεγχους των ξένων κλειδιών για να αποφύγεις τυχόν λάθη εξάρτησης!
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
    
    # Ενεργοποίησε ξανά τους έλεγχους των ξένων κλειδιών!
    cursor.execute("PRAGMA foreign_keys = ON;")

    connection.commit()
    connection.close()

    print("Όλα τα δεδομένα της ΒΔ διαγράφηκαν επιτυχώς!\n\nΕκκίνηση γεμίσματος ΒΔ με νέα δεδομένα...")

    return;

def main():
    db_path = "publishing_house.db"
    schema_file_path = "schema.sql"

    drop_tables(db_path)

    create_database(db_path, schema_file_path)
    populate_database(db_path)

    sleep(1)

    return;

if __name__ == "__main__":
    main()
