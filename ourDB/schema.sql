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
	"payment" float,
	"start_date" date,
	"expiration_date" date,
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
	"price" float,
	"stock" integer,
	"genre-id" integer,
	PRIMARY KEY ("isbn"),
	FOREIGN KEY ("genre-id") REFERENCES "GENRE" ("id") --referential integrity constraint
            ON UPDATE CASCADE --Αν αλλάξει το id ενός είδους, αλλάζει και στον πίνακα PUBLICATION   
            ON DELETE SET NULL --Δεν θέλουμε να διαγράψουμε ένα βιβλίο αν αυτό ανήκει σε κάποιο είδος, ακομα και αν διαγραψουμε το ειδος
);          --id ειδους μπορει να αλλαξει, αλλα δεν θελουμε να διαγραφεται το βιβλιο (δεν χρειαζονται αυστηροι περιορισοι οπως στα ΑΦΜ)
            --To id ενός είδους μπορεί να αλλάξει και επιτρέπται να γίνει manually updated από τον χρήστη

CREATE TABLE IF NOT EXISTS "client_orders" (
	"Client_Tax_ID" integer,
	"Publication-isbn" integer,
	"quantity" integer,
	"order date" date,
	"delivery date" date,
	"payment" float,
	PRIMARY KEY ("Client_Tax_ID", "Publication-isbn"),
	FOREIGN KEY ("Client_Tax_ID") REFERENCES "CLIENT" ("Tax_ID")
            ON UPDATE RESTRICT  --Δεν επιτρεπεται αλλαγη του Tax_Id του CLIENT
            ON DELETE RESTRICT, -- Δεν θέλουμε να διαγράψουμε έναν πελάτη αν έχει κάνει παραγγελία, ωστε να διατηρήσουμε ιστορικο συναλλαγών
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn")
            ON UPDATE RESTRICT  --Δεν επιτρεπεται αλλαγη του isbn του PUBLICATION
            ON DELETE RESTRICT  --Δεν επιτρεπεται διαγραφη βιβλιου με isbn
);

CREATE TABLE IF NOT EXISTS "contributes" (
	"Partner_TaxId" integer,
	"Publication-isbn" integer,
	"estimated_completion_date" date,
	"start_date" date,
	"completion_date" date,
	"payment date" date,
	PRIMARY KEY ("Partner_TaxId", "Publication-isbn"),
	FOREIGN KEY ("Partner_TaxId") REFERENCES "PARTNER" ("Tax_Id") --referential integrity constraint
            ON UPDATE RESTRICT --Δεν θέλουμε να αλλάξουμε το Tax_Id του PARTNER οπότε το αποτρέπουμε με το RESTRICT
            ON DELETE RESTRICT, -- κραταμε το tax_id ωστε να σχηματιζει Unique key, δεν επιτρεπεται διαγραφη συνεργατη
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn")	--referential integrity constraint
            ON UPDATE RESTRICT --Δεν θέλουμε να αλλάξουμε το isbn του PUBLICATION οπότε το αποτρέπουμε με το RESTRICT
            ON DELETE RESTRICT -- κραταμε το isbn ωστε να σχηματιζει Unique key, δεν επιτρεπεται διαγραφη εντυπου
);

CREATE TABLE IF NOT EXISTS "order_printing_house" (
	"Printing-id" integer ,
	"Publication-isbn" integer, 
	"order date" date,
	"delivery date" date,
	"quantity" integer,
	"cost" float,
	--FOREIGN PRIMARY KEY OPOTE ON DELETE SET DEFAULT ΔΕΝ ΣΥΝΙΣΤΑΤΑΙ DUE TO UNIQUNESS CONSTRAINT
	PRIMARY KEY ("Printing-id", "Publication-isbn"),
	FOREIGN KEY ("Printing-id") REFERENCES "PRINTING_HOUSE" ("p_id") --referential integrity constraint
            ON UPDATE RESTRICT --Δεν θέλουμε να αλλάξουμε το p_id του PRINTING_HOUSE οπότε το αποτρέπουμε με το RESTRICT
            ON DELETE RESTRICT ,-- Retain the order, κρατάμε την παραγγελια δεν επιτρέπεται διαγραφή του τυπογραφειου
			--ακομα και αν δεν συνεργαζομαστε πλεον με καποιο τυπογραφειο, παραμενει στην βαση για ιστορικους λογους
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn")	--referential integrity constraint
            ON UPDATE RESTRICT 	--Δεν θέλουμε να αλλάξουμε το isbn του PUBLICATION οπότε το αποτρέπουμε με το RESTRICT
            ON DELETE RESTRICT -- δεν διαγραφεται το εντυπο απο την βαση
);                              -- ακομα και αν το βιβλιο δεν το προσφερουμε πια, θελουμε τις λεπτομερειες της συναλλαγης

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

CREATE TABLE IF NOT EXISTS "communication-PRINTING" (
	"Printing-id" integer,
	"Printing_comm" integer,
	PRIMARY KEY ("Printing-id", "Printing_comm"),
	FOREIGN KEY ("Printing-id") REFERENCES "PRINTING_HOUSE" ("p_id") --referential integrity constraint
            ON UPDATE RESTRICT --καθώς δεν πρόκειται να αλλάξουμε το πεδίο p_id από τον πίνακα PRINTING_HOUSE
            ON DELETE CASCADE --Εάν μια εγγραφή διαγραφεί από τον πίνακα PRINTING_HOUSE,
			-- όλες οι σχετικές εγγραφές στον πίνακα communication-PRINTING διαγράφονται αυτόματα.
);  --το τυπογραφείο μπορεί να διαγραφεί μόνο αν δεν εχει καμια σχεση με καποια παραγγελια

