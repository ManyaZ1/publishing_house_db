--Επιβεβαιώνουμε ότι PRAGMA foreign_keys είναι 1 στο SQLite3 για να ενεργοποιήσουμε τον έλεγχο των εξωτερικών κλειδιών

CREATE TABLE IF NOT EXISTS "PARTNER" (
	"name" string,
	"Tax_Id" integer,
	"specialisation" integer,
	"comments" string,
	CONSTRAINT "check_specialisation" CHECK ("specialisation" BETWEEN 1 AND 4), --Έλεγχος για το πεδίο specialisation
	PRIMARY KEY ("Tax_Id") --οχι null το Tax_Id
);

-- δεν διαγράφουμε ποτέ partner, γιατί πρέπει να κραταμε αρχειο με ολα τα συμβολαια για ιστορικους λογους
-- οποτε χρειαζομαστε και τα κλειδια των συνεργατων
-- επομένως χρησιμοποιούμε το RESTRICT στο ON DELETE
-- Επίσης, δεν επιτρέπεται η αλλαγή του Tax_Id του PARTNER
-- οπότε χρησιμοποιούμε το RESTRICT στο ON UPDATE

CREATE TABLE IF NOT EXISTS "CONTRACT" ( 
	"payment" REAL CHECK(typeof(payment) = 'real' AND payment >= 0) ,
	"start_date" TEXT CHECK(
        start_date LIKE '____-__-__' -- Matches YYYY-MM-DD pattern
        AND date(start_date) IS NOT NULL -- Validates it as a proper date
    ),
	"expiration_date" TEXT CHECK(
        expiration_date LIKE '____-__-__' -- Matches YYYY-MM-DD pattern
        AND date(expiration_date) IS NOT NULL -- Validates it as a proper date
        AND expiration_date > start_date -- Ensures logical consistency
    ),
	"id" integer,
	"description" string,
	"Partner_Tax_Id" integer NOT NULL, --δεν γινεται να υπαρχει συμβολαιο χωρις συνεργατη με ΑΦΜ
	"Publication-isbn" integer NOT NULL, --δεν γινεται να υπαρχει συμβολαιο χωρις βιβλιο με isbn
	PRIMARY KEY ("id"),
	FOREIGN KEY ("Partner_Tax_Id") REFERENCES "PARTNER" ("Tax_Id") --referential integrity constraint
            ON UPDATE RESTRICT --δεν επιτρεπεται αλλαγη του Tax_Id του PARTNER
            ON DELETE RESTRICT,--δεν επιτρέπεται διαγραφή Tax_Id
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn") --referential integrity constraint
            ON UPDATE RESTRICT --δεν επιτρεπεται αλλαγη του isbn του PUBLICATION
            ON DELETE RESTRICT -- δεν επιτρέπεται διαγραφή isbn
);

CREATE TABLE IF NOT EXISTS "CLIENT" (
	"Tax_ID" integer,
	"name" string,
	"location" string,
	PRIMARY KEY ("Tax_ID")
);

CREATE TABLE IF NOT EXISTS "PRINTING_HOUSE" (
	"p_location" string,
	"p_id" integer,
	"capabilities" integer,
	PRIMARY KEY ("p_id")
);

CREATE TABLE IF NOT EXISTS "GENRE" (
	"age_range" string,
	"description" string,
	"id" integer,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "PUBLICATION" (
	"title" string,
	"isbn" integer,
	"price" REAL CHECK(typeof(price) = 'real' AND price >= 0) ,  --float would let irregular values in the database
	"stock" integer,
	"genre-id" integer,
	PRIMARY KEY ("isbn"),
	FOREIGN KEY ("genre-id") REFERENCES "GENRE" ("id") --referential integrity constraint
            ON UPDATE CASCADE --Αν αλλάξει το id ενός είδους, αλλάζει και στον πίνακα PUBLICATION   
            ON DELETE SET NULL --Δεν θέλουμε να διαγράψουμε ένα βιβλίο αν αυτό ανήκει σε κάποιο είδος, ακομα και αν διαγραψουμε το ειδος
);          --id ειδους μπορει να αλλαξει, αλλα δεν θελουμε να διαγραφεται το βιβλιο (δεν χρειαζονται αυστηροι περιορισοι οπως στα ΑΦΜ)
            --To id ενός είδους μπορεί να αλλάξει και επιτρέπται να γίνει manually updated από τον χρήστη

CREATE TABLE IF NOT EXISTS "client_orders" (
	"order_id" integer NOT NULL,
	"Client_Tax_ID" integer,
	"Publication-isbn" integer,
	"quantity" integer,
	"order date" TEXT,
	"delivery date" TEXT,
	"payment" REAL CHECK(typeof(payment) = 'real' AND payment >= 0),
	PRIMARY KEY ("order_id"),
	FOREIGN KEY ("Client_Tax_ID") REFERENCES "CLIENT" ("Tax_ID")
            ON UPDATE RESTRICT  --Δεν επιτρεπεται αλλαγη του Tax_Id του CLIENT
            ON DELETE RESTRICT, -- Δεν θέλουμε να διαγράψουμε έναν πελάτη αν έχει κάνει παραγγελία, ωστε να διατηρήσουμε ιστορικο συναλλαγών
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn")
            ON UPDATE RESTRICT  --Δεν επιτρεπεται αλλαγη του isbn του PUBLICATION
            ON DELETE RESTRICT  --Δεν επιτρεπεται διαγραφη βιβλιου με isbn
	CONSTRAINT 	valid_order_date CHECK(
        						"order date" LIKE '____-__-__' -- Matches YYYY-MM-DD pattern
        						AND date("order date") IS NOT NULL), -- Validates it as a proper date
	CONSTRAINT 	valid_delivery_date CHECK( 
								"delivery date" IS NULL -- Allow NULL values
								OR(
								"delivery date" LIKE '____-__-__' -- Matches YYYY-MM-DD pattern
								AND date("delivery date") IS NOT NULL -- Validates it as a proper date
								AND "delivery date" > "order date") -- Ensures logical consistency
	)
);

CREATE TABLE IF NOT EXISTS "contributes" (
	"Partner_TaxId" integer,
	"Publication-isbn" integer,
	"start_date" TEXT CHECK(
		start_date LIKE '____-__-__' -- Matches YYYY-MM-DD pattern
		AND date(start_date) IS NOT NULL -- Validates it as a proper date
	),
	"estimated_completion_date" TEXT CHECK(
		"estimated_completion_date" LIKE '____-__-__' -- Matches YYYY-MM-DD pattern
		AND date("estimated_completion_date") IS NOT NULL -- Validates it as a proper date
		AND "estimated_completion_date" >= start_date -- Ensures logical consistency
	),
	"completion_date" TEXT CHECK(
		completion_date is NULL -- Allow NULL values
		OR (
            "completion_date" LIKE '____-__-__'
            AND date("completion_date") IS NOT NULL
            AND "completion_date" >= "start_date"
        )
		
	),
	"payment_date" TEXT	,
	PRIMARY KEY ("Partner_TaxId", "Publication-isbn"),
	FOREIGN KEY ("Partner_TaxId") REFERENCES "PARTNER" ("Tax_Id") --referential integrity constraint
            ON UPDATE RESTRICT --Δεν θέλουμε να αλλάξουμε το Tax_Id του PARTNER οπότε το αποτρέπουμε με το RESTRICT
            ON DELETE RESTRICT, -- κραταμε το tax_id ωστε να σχηματιζει Unique key, δεν επιτρεπεται διαγραφη συνεργατη
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn")	--referential integrity constraint
            ON UPDATE RESTRICT --Δεν θέλουμε να αλλάξουμε το isbn του PUBLICATION οπότε το αποτρέπουμε με το RESTRICT
            ON DELETE RESTRICT -- κραταμε το isbn ωστε να σχηματιζει Unique key, δεν επιτρεπεται διαγραφη εντυπου
	CONSTRAINT valid_payment_date CHECK(
        "payment_date" IS NULL -- Allow NULL values
        OR (
            "payment_date" LIKE '____-__-__'
            AND date("payment_date") IS NOT NULL
            AND "payment_date" >= "start_date"
        )
    )
);

CREATE TABLE IF NOT EXISTS "order_printing_house" (
	"order_id" integer NOT NULL,
	"Printing-id" integer ,
	"Publication-isbn" integer, 
	"order date" date NOT NULL,
	"delivery date" date,
	"quantity" integer,
	"cost" REAL CHECK(typeof(cost) = 'real' AND cost >= 0),
	--FOREIGN PRIMARY KEY OPOTE ON DELETE SET DEFAULT ΔΕΝ ΣΥΝΙΣΤΑΤΑΙ DUE TO UNIQUNESS CONSTRAINT
	PRIMARY KEY ("order_id"),
	FOREIGN KEY ("Printing-id") REFERENCES "PRINTING_HOUSE" ("p_id") --referential integrity constraint
            ON UPDATE RESTRICT --Δεν θέλουμε να αλλάξουμε το p_id του PRINTING_HOUSE οπότε το αποτρέπουμε με το RESTRICT
            ON DELETE RESTRICT ,-- Retain the order, κρατάμε την παραγγελια δεν επιτρέπεται διαγραφή του τυπογραφειου
			--ακομα και αν δεν συνεργαζομαστε πλεον με καποιο τυπογραφειο, παραμενει στην βαση για ιστορικους λογους
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn")	--referential integrity constraint
            ON UPDATE RESTRICT 	--Δεν θέλουμε να αλλάξουμε το isbn του PUBLICATION οπότε το αποτρέπουμε με το RESTRICT
            ON DELETE RESTRICT -- δεν διαγραφεται το εντυπο απο την βαση
			-- ακομα και αν το βιβλιο δεν το προσφερουμε πια, θελουμε τις λεπτομερειες της συναλλαγης
	CONSTRAINT 	valid_order_date_print CHECK(
        						"order date" LIKE '____-__-__' -- Matches YYYY-MM-DD pattern
        						AND date("order date") IS NOT NULL), -- Validates it as a proper date
	CONSTRAINT 	valid_delivery_date_print CHECK(
								"delivery date" IS NULL -- Allow NULL values
								OR("delivery date" LIKE '____-__-__' -- Matches YYYY-MM-DD pattern
								AND date("delivery date") IS NOT NULL
								AND date("delivery date")>="order date") -- Validates it as a proper date)
								)
);                              

CREATE TABLE IF NOT EXISTS "communication-CLIENT" (
	"Clinet_Tax_ID" integer,
	"Client_Comm" integer,
	PRIMARY KEY ("Clinet_Tax_ID", "Client_Comm"),
	FOREIGN KEY ("Clinet_Tax_ID") REFERENCES "CLIENT" ("Tax_ID") --referential integrity constraint
            ON UPDATE RESTRICT --Δεν θέλουμε να αλλάξουμε το Tax_Id του CLIENT οπότε το αποτρέπουμε με το RESTRICT
            ON DELETE CASCADE --Εάν διαγραφεί ένας CLIENT, όλες οι σχετικές εγγραφές στον πίνακα communication-CLIENT διαγράφονται αυτόματα.
);          -- ο πελατης μπορει να διαγραφει μόνο αν δεν εχει καμια σχεση με καποια παραγγελια

CREATE TABLE IF NOT EXISTS "communication-PARTNER" (
	"Partner_Tax_Id" integer,
	"partner_comm" integer,
	PRIMARY KEY ("Partner_Tax_Id", "partner_comm"),
	FOREIGN KEY ("Partner_Tax_Id") REFERENCES "PARTNER" ("Tax_Id") --referential integrity constraint
            ON UPDATE RESTRICT --Δεν θέλουμε να αλλάξουμε το Tax_Id του PARTNER οπότε το αποτρέπουμε με το RESTRICT
            ON DELETE CASCADE --Εάν διαγραφεί ένας PARTNER, όλες οι σχετικές εγγραφές στον πίνακα communication-PARTNER διαγράφονται αυτόματα.
);                   -- Ο συνεργατης μπορει να διαγραφεί μόνο αν δεν εχει καμια σχεση με καποιο συμβολαιο ή συνεισφορα σε εντυπο (contributes)
-- επιτρέπει στον χρήστη διόρθωση των στοιχείων του συνεργάτη πριν συνάψει κάποια παραγγελία/συμφωνία
CREATE TABLE IF NOT EXISTS "communication-PRINTING" (
	"Printing-id" integer,
	"Printing_comm" integer,
	PRIMARY KEY ("Printing-id", "Printing_comm"),
	FOREIGN KEY ("Printing-id") REFERENCES "PRINTING_HOUSE" ("p_id") --referential integrity constraint
            ON UPDATE RESTRICT --καθώς δεν πρόκειται να αλλάξουμε το πεδίο p_id από τον πίνακα PRINTING_HOUSE
            ON DELETE CASCADE --Εάν μια εγγραφή διαγραφεί από τον πίνακα PRINTING_HOUSE,
			-- όλες οι σχετικές εγγραφές στον πίνακα communication-PRINTING διαγράφονται αυτόματα.
);  --το τυπογραφείο μπορεί να διαγραφεί μόνο αν δεν εχει καμια σχεση με καποια παραγγελια

