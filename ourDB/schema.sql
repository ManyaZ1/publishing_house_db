CREATE TABLE IF NOT EXISTS "ΣΥΝΕΡΓΑΤΗΣ" (
	"ονομασία" string,
	"α.φ.μ." integer,
	"ειδίκευση" string,
	"σχόλια" string,
	PRIMARY KEY ("α.φ.μ.")
);

CREATE TABLE IF NOT EXISTS "ΣΥΜΒΟΛΑΙΟ" (
	"αμοιβή" float,
	"ημ. έναρξης" date,
	"διάρκεια" date,
	"id" integer,
	"περιγραφή" string,
	"ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ." integer,
	"ΕΝΤΥΠΟ-isbn" integer,
	PRIMARY KEY ("id", "ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.", "ΕΝΤΥΠΟ-isbn"),
	FOREIGN KEY ("ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.") REFERENCES "ΣΥΝΕΡΓΑΤΗΣ" ("α.φ.μ.")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("ΕΝΤΥΠΟ-isbn") REFERENCES "ΕΝΤΥΠΟ" ("isbn")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "ΠΕΛΑΤΗΣ" (
	"α.φ.μ." integer,
	"ονομασία" string,
	"τοποθεσία" string,
	PRIMARY KEY ("α.φ.μ.")
);

CREATE TABLE IF NOT EXISTS "ΤΥΠΟΓΡΑΦΕΙΟ" (
	"τοποθεσία" string,
	"id" integer,
	"δυνατότητες" string,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "ΕΙΔΟΣ" (
	"ηλικιακό εύρος" string,
	"περιγραφή" string,
	"id" integer,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "ΕΝΤΥΠΟ" (
	"τίτλος" string,
	"isbn" integer,
	"τιμή" float,
	"stock" integer,
	"ΕΙΔΟΣ-id" integer,
	PRIMARY KEY ("isbn", "ΕΙΔΟΣ-id"),
	FOREIGN KEY ("ΕΙΔΟΣ-id") REFERENCES "ΕΙΔΟΣ" ("id")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "ζητάει" (
	"ΠΕΛΑΤΗΣ-α.φ.μ." integer,
	"ΕΝΤΥΠΟ-isbn" integer,
	"ποσότητα" integer,
	"ημ. παραγγελίας" date,
	"ημ. παράδοσης" date,
	"χρηματικό ποσό" float,
	PRIMARY KEY ("ΠΕΛΑΤΗΣ-α.φ.μ.", "ΕΝΤΥΠΟ-isbn"),
	FOREIGN KEY ("ΠΕΛΑΤΗΣ-α.φ.μ.") REFERENCES "ΠΕΛΑΤΗΣ" ("α.φ.μ.")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("ΕΝΤΥΠΟ-isbn") REFERENCES "ΕΝΤΥΠΟ" ("isbn")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "επεξεργαζεται" (
	"ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ." integer,
	"ΕΝΤΥΠΟ-isbn" integer,
	"ΕΤΑ" date,
	"ημ. έναρξης" date,
	"ημ. ολοκλήρωσης" date,
	"πληρωμή" boolean,
	PRIMARY KEY ("ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.", "ΕΝΤΥΠΟ-isbn"),
	FOREIGN KEY ("ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.") REFERENCES "ΣΥΝΕΡΓΑΤΗΣ" ("α.φ.μ.")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("ΕΝΤΥΠΟ-isbn") REFERENCES "ΕΝΤΥΠΟ" ("isbn")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "παραγγέλνει" (
	"ΤΥΠΟΓΡΑΦΕΙΟ-id" integer,
	"ΕΝΤΥΠΟ-isbn" integer,
	"ημ. παραγγελίας" date,
	"ημ. παράδοσης" date,
	"ποσότητα" integer,
	"κόστος" float,
	PRIMARY KEY ("ΤΥΠΟΓΡΑΦΕΙΟ-id", "ΕΝΤΥΠΟ-isbn"),
	FOREIGN KEY ("ΤΥΠΟΓΡΑΦΕΙΟ-id") REFERENCES "ΤΥΠΟΓΡΑΦΕΙΟ" ("id")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("ΕΝΤΥΠΟ-isbn") REFERENCES "ΕΝΤΥΠΟ" ("isbn")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "επικοινωνία-ΠΕΛΑΤΗΣ" (
	"ΠΕΛΑΤΗΣ-α.φ.μ." integer,
	"ΠΕΛΑΤΗΣ-επικοινωνία" integer,
	PRIMARY KEY ("ΠΕΛΑΤΗΣ-α.φ.μ.", "ΠΕΛΑΤΗΣ-επικοινωνία"),
	FOREIGN KEY ("ΠΕΛΑΤΗΣ-α.φ.μ.") REFERENCES "ΠΕΛΑΤΗΣ" ("α.φ.μ.")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "επικοινωνία-ΣΥΝΕΡΓΑΤΗΣ" (
	"ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ." integer,
	"ΣΥΝΕΡΓΑΤΗΣ-επικοινωνία" integer,
	PRIMARY KEY ("ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.", "ΣΥΝΕΡΓΑΤΗΣ-επικοινωνία"),
	FOREIGN KEY ("ΣΥΝΕΡΓΑΤΗΣ-α.φ.μ.") REFERENCES "ΣΥΝΕΡΓΑΤΗΣ" ("α.φ.μ.")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "επικοινωνία-ΤΥΠΟΓΡΑΦΕΙΟ" (
	"ΤΥΠΟΓΡΑΦΕΙΟ-id" integer,
	"ΤΥΠΟΓΡΑΦΕΙΟ-επικοινωνία" integer,
	PRIMARY KEY ("ΤΥΠΟΓΡΑΦΕΙΟ-id", "ΤΥΠΟΓΡΑΦΕΙΟ-επικοινωνία"),
	FOREIGN KEY ("ΤΥΠΟΓΡΑΦΕΙΟ-id") REFERENCES "ΤΥΠΟΓΡΑΦΕΙΟ" ("id")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

