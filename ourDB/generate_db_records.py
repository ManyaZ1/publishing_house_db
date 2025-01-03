from os.path import dirname, abspath, join
from os import remove

from datetime import datetime, timedelta
from time import sleep, perf_counter
import sqlite3
import random

class PublishingDatabaseManager:
    def __init__(self, scale_factor=1):
        """
        Initializes paths, scale factor, and preloads all datasets + default record counts.
        """
        # Directories
        self.script_dir = dirname(abspath(__file__)) # Directory of this file
        self.new_path   = dirname(self.script_dir)   # One level above

        self.db_path          = join(self.new_path, "publishing_house.db")
        self.schema_file_path = join(self.script_dir, "schema.sql")
        self.datasets_dir     = join(self.script_dir, "datasets")

        # Scale factor: multiples of data
        self.scale_factor = scale_factor

        # Default base counts
        self.default_counts = {
            'partners':        10,
            'clients':         15,
            'printing_houses': 5,
            'publications':    20,
            'contracts':       30,
            'client_orders':   50,
            'contributions':   40,
        }

        # Compute final counts for each data type (scaled)
        self.n_partners        = int(self.default_counts['partners']        * self.scale_factor)
        self.n_clients         = int(self.default_counts['clients']         * self.scale_factor)
        self.n_printing_houses = int(self.default_counts['printing_houses'] * self.scale_factor)
        self.n_publications    = int(self.default_counts['publications']    * self.scale_factor)
        self.n_contracts       = int(self.default_counts['contracts']       * self.scale_factor)
        self.n_client_orders   = int(self.default_counts['client_orders']   * self.scale_factor)
        self.n_contributions   = int(self.default_counts['contributions']   * self.scale_factor)

        # Preload datasets so we don't read from files repeatedly in each method.
        self.first_names = self._read_data_from_file('first_names.txt')
        self.last_names  = self._read_data_from_file('last_names.txt')
        self.categories  = self._read_data_from_file('categories.txt')
        self.locations   = self._read_data_from_file('locations.txt')
        self.book_titles = self._read_data_from_file('book_titles.txt')

        return;

    # 1) Helper Methods (internal usage)
    #    A single leading underscore is simply a naming convention that
    #    signals "this is meant to be an internal or private method"!
    def _read_data_from_file(self, file_name):
        """
        Reads lines from the given text file inside 'datasets/'.
        Returns a list of stripped lines.
        """
        full_path = join(self.datasets_dir, file_name)
        with open(full_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f];

    @staticmethod
    def _random_date(start, end):
        """
        Returns a random datetime between 'start' and 'end'.
        """
        delta = end - start
        random_days = random.randint(0, delta.days)
        return start + timedelta(days=random_days);

    @staticmethod
    def _random_afm():
        """
        Returns a random integer in the range [100_000_000, 999_999_999].
        """
        return random.randint(100_000_000, 999_999_999);

    @staticmethod
    def _random_phone():
        """
        Returns a random 'phone-like' integer (mimicking Greek phone system).
        """
        return random.choice([
            random.randint(690_000_0000, 699_999_9999),
            random.randint(210_000_0000, 289_999_9999)
        ]);

    @staticmethod
    def _random_partition(total, parts):
        """
        Splits 'total' into 'parts' random positive integer chunks that sum to 'total'.
        """
        result = []
        allocated = 0
        for i in range(parts - 1):
            max_for_chunk = total - allocated - ((parts - 1) - i)
            chunk = random.randint(1, max_for_chunk)
            result.append(chunk)
            allocated += chunk
        final_chunk = total - allocated
        result.append(final_chunk)

        return result;

    @staticmethod
    def _get_everything(cursor, query):
        """
        Executes 'query' with the provided 'cursor'
        and returns a list of the first column of each row.
        """
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()];

    # 2) DB Setup (create / delete)
    def _delete_db_file(self):
        """
        Deletes the existing database file if it exists.
        """
        try:
            remove(self.db_path)
            print("Old database file deleted successfully!")
        except FileNotFoundError:
            print("No old database file found.")
        print("") # newline - better output formatting

        return;

    def _create_database(self):
        """
        Creates a new SQLite database by reading and executing the schema file.
        """
        with open(self.schema_file_path, 'r', encoding='utf-8') as schema_file:
            schema_content = schema_file.read()

        connection = sqlite3.connect(self.db_path)
        # Enable foreign key support
        connection.execute("PRAGMA foreign_keys = ON;")
        cursor = connection.cursor()
        cursor.executescript(schema_content)
        connection.commit()
        connection.close()

        print("Database created successfully!\n")

        return;

    # 3) Data Population
    def _populate_database(self):
        """
        Main 'population' routine that inserts all data into the DB,
        using the internal state.
        """
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON;")
        cursor = connection.cursor()

        # ------------------- PARTNER -------------------
        start_time = perf_counter()

        partners = self._generate_partners()
        cursor.executemany(
            'INSERT INTO "PARTNER" ("name", "Tax_Id", "specialisation", "comments") '
            'VALUES (?, ?, ?, ?)', partners
        )

        end_time = perf_counter()
        print(f"Partner generation took {end_time - start_time:.5f} seconds.")

        self.all_partner_tax_ids = self._get_everything(cursor, 'SELECT "Tax_Id" FROM "PARTNER"')

        # ------------------- CLIENT --------------------
        start_time = perf_counter()

        clients = self._generate_clients()
        cursor.executemany(
            'INSERT INTO "CLIENT" ("Tax_ID", "name", "location") '
            'VALUES (?, ?, ?)', clients
        )

        end_time = perf_counter()
        print(f"Client generation took {end_time - start_time:.5f} seconds.")

        self.all_client_tax_ids = self._get_everything(cursor, 'SELECT "Tax_ID" FROM "CLIENT"')

        # ---------------- PRINTING_HOUSE ---------------
        start_time = perf_counter()

        printing_houses = self._generate_ph()
        cursor.executemany(
            'INSERT INTO "PRINTING_HOUSE" ("p_location", "p_id", "capabilities") '
            'VALUES (?, ?, ?)', printing_houses
        )

        end_time = perf_counter()
        print(f"Printing house generation took {end_time - start_time:.5f} seconds.")

        self.all_printing_ids = self._get_everything(cursor, 'SELECT "p_id" FROM "PRINTING_HOUSE"')

        # ------------------- GENRE ---------------------
        start_time = perf_counter()

        # We'll insert one row per category from our file. No scale option!
        genre_data = []
        g_id = 1
        for cat in self.categories:
            description = f"Books in the {cat.lower()} genre"
            age_range = random.choice(["3+", "7+", "14+", "18+"])
            genre_data.append((age_range, description, g_id))
            g_id += 1
        cursor.executemany(
            'INSERT INTO "GENRE" ("age_range", "description", "id") '
            'VALUES (?, ?, ?)', genre_data
        )

        end_time = perf_counter()
        print(f"Genre generation took {end_time - start_time:.5f} seconds.")

        self.all_genre_ids = self._get_everything(cursor, 'SELECT "id" FROM "GENRE"')

        # ----------------- PUBLICATION -----------------
        start_time = perf_counter()

        publications = self._generate_publications()
        cursor.executemany(
            'INSERT INTO "PUBLICATION" ("title", "isbn", "price", "stock", "genre-id") '
            'VALUES (?, ?, ?, ?, ?)', publications
        )

        end_time = perf_counter()
        print(f"Publication generation took {end_time - start_time:.5f} seconds.")

        self.all_isbns = self._get_everything(cursor, 'SELECT "isbn" FROM "PUBLICATION"')

        # Build maps for price & stock per ISBN
        cursor.execute('SELECT "isbn", "price", "stock" FROM "PUBLICATION"')
        rows = cursor.fetchall()
        self.all_isbn_price = {row[0]: row[1] for row in rows}
        self.all_isbn_stock = {row[0]: row[2] for row in rows}

        # ------------------- CONTRACT ------------------
        start_time = perf_counter()

        contracts = self._generate_contracts()
        cursor.executemany(
            'INSERT INTO "CONTRACT" '
            '("payment", "start_date", "expiration_date", "id", "description", '
            '"Partner_Tax_Id", "Publication-isbn") '
            'VALUES (?, ?, ?, ?, ?, ?, ?)', contracts
        )

        end_time = perf_counter()
        print(f"Contract generation took {end_time - start_time:.5f} seconds.")

        # ---------------- CLIENT_ORDERS ---------------
        start_time = perf_counter()

        client_orders = self._generate_client_orders()
        cursor.executemany(
            'INSERT INTO "client_orders" ("order_id", "Client_Tax_ID", "Publication-isbn", "quantity", '
            '"order date", "delivery date", "payment") '
            'VALUES (?,?, ?, ?, ?, ?, ?)', client_orders
        )

        end_time = perf_counter()
        print(f"Client order generation took {end_time - start_time:.5f} seconds.")

        # How many copies have been ordered per ISBN
        cursor.execute(
            'SELECT "Publication-isbn", SUM("quantity") '
            'FROM "client_orders" '
            'GROUP BY "Publication-isbn"'
        )
        self.all_isbn_orders_map = {row[0]: row[1] for row in cursor.fetchall()}

        # FETCH ONCE (CLIENT -> earliest delivery date) 
        # Instead of per-row queries in _generate_printing_orders
        cursor.execute(
            'SELECT "Publication-isbn", MIN("delivery date") '
            'FROM "client_orders" '
            'GROUP BY "Publication-isbn"'
        )
        self.min_delivery_date_by_isbn = {row[0]: row[1] for row in cursor.fetchall()}

        # ------------ ORDER_PRINTING_HOUSE ------------
        start_time = perf_counter()

        printing_orders = self._generate_printing_orders(cursor)
        cursor.executemany(
            'INSERT INTO "order_printing_house" '
            '("order_id","Printing-id", "Publication-isbn", "order date", "delivery date", "quantity", "cost") '
            'VALUES (?,?, ?, ?, ?, ?, ?)', printing_orders
        )

        end_time = perf_counter()
        print(f"Printing order generation took {end_time - start_time:.5f} seconds.")

        # FETCH ONCE (PRINTING -> earliest printing date)
        cursor.execute(
            'SELECT "Publication-isbn", MIN("order date") '
            'FROM "order_printing_house" '
            'GROUP BY "Publication-isbn"'
        )
        self.min_printing_date_by_isbn = {row[0]: row[1] for row in cursor.fetchall()}

        # ---------------- CONTRIBUTES ------------------
        start_time = perf_counter()

        contributes_data = self._generate_contributions(cursor)
        cursor.executemany(
            'INSERT INTO "contributes" '
            '("Partner_TaxId", "Publication-isbn", "estimated_completion_date", '
            '"start_date", "completion_date", "payment_date") '
            'VALUES (?, ?, ?, ?, ?, ?)', contributes_data
        )

        end_time = perf_counter()
        print(f"Contribution generation took {end_time - start_time:.5f} seconds.")

        # --------------- COMMUNICATION ----------------
        start_time = perf_counter()

        # -> CLIENT
        client_contacts = self._generate_communication(self.all_client_tax_ids)
        cursor.executemany(
            'INSERT INTO "communication-CLIENT" ("Clinet_Tax_ID", "Client_Comm") '
            'VALUES (?, ?)', client_contacts
        )
        # -> PARTNER
        partner_contacts = self._generate_communication(self.all_partner_tax_ids)
        cursor.executemany(
            'INSERT INTO "communication-PARTNER" ("Partner_Tax_Id", "partner_comm") '
            'VALUES (?, ?)', partner_contacts
        )
        # -> PRINTING
        printing_contacts = self._generate_communication(self.all_printing_ids)
        cursor.executemany(
            'INSERT INTO "communication-PRINTING" ("Printing-id", "Printing_comm") '
            'VALUES (?, ?)', printing_contacts
        )

        end_time = perf_counter()
        print(f"Communication generation took {end_time - start_time:.5f} seconds.")

        # Commit changes
        connection.commit()
        connection.close()

        print("\nDatabase populated successfully!")

        return;

    # 4) Data Generation Methods (no arguments, use self.*)
    def _generate_partners(self):
        """
        Generate random PARTNER data, using 'self.n_partners',
        with no overlap in Tax IDs.
        """
        partner_tax_ids = set()
        partners = []
        for _ in range(self.n_partners):
            while True:
                tax_id = self._random_afm()
                if tax_id not in partner_tax_ids:
                    partner_tax_ids.add(tax_id)
                    break;

            name = f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
            spec = random.randint(1, 4)  # Must be 1 -> 4 per schema
            comments = random.randint(1, 5)
            partners.append((name, tax_id, spec, comments))

        return partners;

    def _generate_clients(self):
        """
        Generate random CLIENT data, using 'self.n_clients',
        ensuring no overlap with existing partner Tax IDs.
        """
        existing_partner_ids = set(self.all_partner_tax_ids)
        client_tax_ids = set()
        clients = []
        for _ in range(self.n_clients):
            while True:
                tax_id = self._random_afm()
                ##################################### Make sure it does not appear in partner IDs
                if (tax_id not in client_tax_ids) and (tax_id not in existing_partner_ids):
                    client_tax_ids.add(tax_id)
                    break;

            name = f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
            loc  = random.choice(self.locations)
            clients.append((tax_id, name, loc))

        return clients;

    def _generate_ph(self):
        """
        Generate printing houses, using 'self.n_printing_houses'.
        """
        printing_houses = []
        p_id = 1
        for _ in range(self.n_printing_houses):
            capabilities = random.randint(1, 5)
            p_loc = random.choice(self.locations)
            printing_houses.append((p_loc, p_id, capabilities))
            p_id += 1

        return printing_houses;

    def _generate_publications(self):
        """
        Generate publications, using 'self.n_publications'.
        """
        used_isbns = set()
        publications = []
        for _ in range(self.n_publications):
            while True:
                # International Standard Book Number (10-ψήφιος αριθμός από την 1η Ιανουαρίου 2007)
                isbn = random.randint(1_000_000_000_000, 9_999_999_999_999)
                if isbn not in used_isbns:
                    used_isbns.add(isbn)
                    break;

            title = random.choice(self.book_titles)
            price = round(random.uniform(5.0, 200.0), 2)
            stock = random.randint(0, 500)
            chosen_genre_id = random.choice(self.all_genre_ids)
            publications.append((title, isbn, price, stock, chosen_genre_id))

        return publications;

    def _generate_contracts(self):
        """
        Generate contracts, using 'self.n_contracts'.
        """
        all_start_dates = [
            self._random_date(datetime(2005, 1, 1), datetime(2009, 12, 31))
            for _ in range(self.n_contracts)
        ]
        all_start_dates.sort() # Δεδομένου ότι τα ID είναι ακολουθία αυξανόμενων αριθμών,
                               # οι παραγγελίες πρέπει να έχουν λογικές ημερομηνίες!
        contracts = []
        contract_id = 1
        for i in range(self.n_contracts):
            payment = round(random.uniform(1000.0, 10000.0), 2)
            start = all_start_dates[i]
            expiration = start + timedelta(days=random.randint(30, 2 * 365))
            partner_tax_id   = random.choice(self.all_partner_tax_ids)
            publication_isbn = random.choice(self.all_isbns)
            description = random.choice(["Easy", "Medium", "Hard", "Very hard"])

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

        return contracts;

    def _generate_client_orders(self):
        """
        Generate client_orders, using 'self.n_client_orders'.
        """
        used_client_book_pairs = set()
        client_orders = []
        order_id = 0
        for i in range(self.n_client_orders):
            while True:
                client_tax_id = random.choice(self.all_client_tax_ids)
                publication_isbn = random.choice(self.all_isbns)
                if (client_tax_id, publication_isbn) not in used_client_book_pairs:
                    used_client_book_pairs.add((client_tax_id, publication_isbn))
                    break;

            quantity = random.randint(10, 50)
            order_date = self._random_date(datetime(2010, 1, 1), datetime(2024, 12, 31))
            delivery_date = order_date + timedelta(days=random.randint(1, 30))
            total_cost = round(self.all_isbn_price[publication_isbn] * quantity, 2)
            order_id += 1
            client_orders.append((
                order_id,
                client_tax_id,
                publication_isbn,
                quantity,
                order_date.strftime("%Y-%m-%d"),
                delivery_date.strftime("%Y-%m-%d"),
                total_cost
            ))

        return client_orders;

    def _generate_contributions(self, cursor):
        """
        Generate 'contributes' records so that each partner's contribution
        is within the [contract_start, contract_end] interval and finishes
        before the earliest printing order date.
        """
        used_contrib = set()
        contributes_data = []

        partner_pub_contracts = {}
        cursor.execute('SELECT "Partner_Tax_Id", "Publication-isbn", "start_date", "expiration_date" FROM "CONTRACT"')
        rows = cursor.fetchall()
        for (p_tax_id, pub_isbn, cstart_str, cend_str) in rows:
            cstart = datetime.strptime(cstart_str, "%Y-%m-%d")
            cend   = datetime.strptime(cend_str,   "%Y-%m-%d")

            key = (p_tax_id, pub_isbn)
            if key not in partner_pub_contracts:
                partner_pub_contracts[key] = []
            partner_pub_contracts[key].append((cstart, cend))

        """
        Collect all "valid windows"
            For each (partner, isbn) + contract window, figure out the
            earliest printing order date. If there's a valid overlap
            between [contract_start, contract_end] and printing date,
            store it in a list.
        """
        valid_windows = []  # will hold tuples of:
        # (partner_tax_id, isbn, contract_start, contract_end, earliest_printing)
        for key, cstart_end_list in partner_pub_contracts.items():
            (partner_tax_id, isbn) = key

            # Earliest printing date for this ISBN
            earliest_printing_date = datetime.strptime(self.min_printing_date_by_isbn[isbn], "%Y-%m-%d")

            # For each contract window for this pair
            for (cstart, cend) in cstart_end_list:
                # The contribution must finish by "min(cend, earliest_printing_date)"
                # so we only consider a window if cstart < that date
                if cstart < earliest_printing_date:
                    # We'll store the actual upper limit for completion
                    # as whichever is earlier
                    cupper = min(cend, earliest_printing_date)
                    # If cstart < cupper, we have a valid window
                    if cstart < cupper:
                        valid_windows.append((partner_tax_id, isbn, cstart, cupper))

        random.shuffle(valid_windows)

        # Create up to n_contributions by picking from valid_windows
        for _ in range(self.n_contributions):
            if not valid_windows:
                # no more valid windows => stop early
                break;

            (partner_tax_id, chosen_isbn, cstart, cupper) = valid_windows.pop()
            key = (partner_tax_id, chosen_isbn)
            # if we've already used this pair, skip it
            if key in used_contrib:
                continue;
            used_contrib.add(key)

            completion_date = self._random_date(cstart, cupper)
            start_date = self._random_date(cstart, completion_date)
            eta_date = self._random_date(start_date, completion_date)

            #paid = random.choice([0, 1])
            #payment = date either null or larger than completion_date

            if random.choice([True, False, False]):  # 1/3 chance for NULL
                payment_date = None
            else:
                payment_date = completion_date + timedelta(days=random.randint(1, 30))
                payment_date=payment_date.strftime("%Y-%m-%d")

            contributes_data.append((
                partner_tax_id,
                chosen_isbn,
                eta_date.strftime("%Y-%m-%d"),
                start_date.strftime("%Y-%m-%d"),
                completion_date.strftime("%Y-%m-%d"),
                payment_date # None or a date
                #paid
            ))

        return contributes_data;

    def _generate_printing_orders(self, cursor):
        """
        Generate the order_printing_house table entries,
        reusing client_orders and publication info from self.*.
        """
        used_ph_isbn_pairs = set()
        printing_orders = []
        order_id = 0
        for chosen_isbn in self.all_isbns:
            #order_id += 1
            # If the ISBN has client orders, we might need more copies
            if chosen_isbn in self.all_isbn_orders_map:
                total_needed = self.all_isbn_stock[chosen_isbn] + self.all_isbn_orders_map[chosen_isbn]
                num_partial_orders = random.randint(1, 3)
                partial_quantities = self._random_partition(total_needed, num_partial_orders)

                # Get a reference {MIN} client delivery date to ensure we print on time
                client_deliv_date = datetime.strptime(self.min_delivery_date_by_isbn[chosen_isbn], "%Y-%m-%d")

                for q in partial_quantities:
                    
                    #while True:
                    printing_id = random.choice(self.all_printing_ids)
                    #    if (printing_id, chosen_isbn) not in used_ph_isbn_pairs:
                    #        used_ph_isbn_pairs.add((printing_id, chosen_isbn))
                    #        break;

                    deliver_date = client_deliv_date - timedelta(days=random.randint(1, 60))
                    order_date   = deliver_date - timedelta(days=random.randint(1, 30))
                    cost_per_unit = 0.2 * self.all_isbn_price[chosen_isbn]
                    total_cost = round(cost_per_unit * q, 2)
                    order_id += 1
                    printing_orders.append((
                        order_id,
                        printing_id,
                        chosen_isbn,
                        order_date.strftime("%Y-%m-%d"),
                        deliver_date.strftime("%Y-%m-%d"),
                        q,
                        total_cost
                    ))
            else:
                # No client orders => we only print the stock once
                #while True:
                printing_id = random.choice(self.all_printing_ids)
                #    if (printing_id, chosen_isbn) not in used_ph_isbn_pairs:
                #        used_ph_isbn_pairs.add((printing_id, chosen_isbn))
                #        break;

                order_dt = self._random_date(datetime(2010, 1, 1), datetime(2024, 12, 31))
                deliver_dt = order_dt + timedelta(days=random.randint(1, 30))
                quantity = self.all_isbn_stock[chosen_isbn]

                cost_per_unit = 0.2 * self.all_isbn_price[chosen_isbn]
                total_cost = round(cost_per_unit * quantity, 2)
                order_id += 1
                printing_orders.append((
                    order_id ,
                    printing_id,
                    chosen_isbn,
                    order_dt.strftime("%Y-%m-%d"),
                    deliver_dt.strftime("%Y-%m-%d"),
                    quantity,
                    total_cost
                ))

        return printing_orders;

    def _generate_communication(self, argument_list):
        """
        For each item in 'argument_list' (a partner/client/printing ID),
        generate 1..3 random phone records.
        """
        temp = []
        for item in argument_list:
            for _ in range(random.randint(1, 3)):
                temp.append((item, self._random_phone()))
        
        return temp;

    # 5) Orchestrator (public method)
    def run(self):
        """
        Main entry point:
         1) Delete old DB
         2) Create fresh DB from schema
         3) Populate with all random data
        """
        self._delete_db_file()
        self._create_database()
        self._populate_database()

        #print("All done! Closing in 5 seconds...")

        #sleep(5)

        return;

def main():
    scale_factor = 3

    print("SQLite version:", sqlite3.sqlite_version)
    manager = PublishingDatabaseManager(scale_factor = scale_factor)

    start = perf_counter()

    manager.run()

    end = perf_counter()
    print(f"Total time: {end - start:.5f} seconds - Scale factor: {scale_factor}.")

    return;

if __name__ == "__main__":
    main()
