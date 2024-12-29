CREATE TABLE IF NOT EXISTS "PARTNER" (
	"name" string,
	"Tax_Id" integer,
	"specialisation" integer ,
	"comments" integer,
	CONSTRAINT "check_specialisation" CHECK ("specialisation" BETWEEN 1 AND 4),
	PRIMARY KEY ("Tax_Id")
);

CREATE TABLE IF NOT EXISTS "CONTRACT" (
	"payment" float,
	"start_date" date,
	"expiration_date" date,
	"id" integer,
	"description" string,
	"Partner_Tax_Id" integer,
	"Publication-isbn" integer,
	PRIMARY KEY ("id", "Partner_Tax_Id", "Publication-isbn"),
	FOREIGN KEY ("Partner_Tax_Id") REFERENCES "PARTNER" ("Tax_Id")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
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
	PRIMARY KEY ("isbn", "genre-id"),
	FOREIGN KEY ("genre-id") REFERENCES "GENRE" ("id")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "client_orders" (
	"Client_Tax_ID" integer,
	"Publication-isbn" integer,
	"quantity" integer,
	"order date" date,
	"delivery date" date,
	"payment" float,
	PRIMARY KEY ("Client_Tax_ID", "Publication-isbn"),
	FOREIGN KEY ("Client_Tax_ID") REFERENCES "CLIENT" ("Tax_ID")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "contributes" (
	"Partner_TaxId" integer,
	"Publication-isbn" integer,
	"estimated_completion_date" date,
	"start_date" date,
	"completion_date" date,
	"payment" boolean,
	PRIMARY KEY ("Partner_TaxId", "Publication-isbn"),
	FOREIGN KEY ("Partner_TaxId") REFERENCES "PARTNER" ("Tax_Id")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "order_printing_house" (
	"Printing-id" integer,
	"Publication-isbn" integer,
	"order date" date,
	"delivery date" date,
	"quntity" integer,
	"cost" float,
	PRIMARY KEY ("Printing-id", "Publication-isbn"),
	FOREIGN KEY ("Printing-id") REFERENCES "PRINTING_HOUSE" ("p_id")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Publication-isbn") REFERENCES "PUBLICATION" ("isbn")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "communication-CLIENT" (
	"Clinet_Tax_ID" integer,
	"Client_Comm" integer,
	PRIMARY KEY ("Clinet_Tax_ID", "Client_Comm"),
	FOREIGN KEY ("Clinet_Tax_ID") REFERENCES "CLIENT" ("Tax_ID")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "communication-PARTNER" (
	"Partner_Tax_Id" integer,
	"partner_comm" integer,
	PRIMARY KEY ("Partner_Tax_Id", "partner_comm"),
	FOREIGN KEY ("Partner_Tax_Id") REFERENCES "PARTNER" ("Tax_Id")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "communication-PRINTING" (
	"Printing-id" integer,
	"Printing_comm" integer,
	PRIMARY KEY ("Printing-id", "Printing_comm"),
	FOREIGN KEY ("Printing-id") REFERENCES "PRINTING_HOUSE" ("p_id")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

