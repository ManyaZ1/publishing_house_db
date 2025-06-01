# publishing_house_db

## Βάσεις Δεδομένων (Διδασκαλία 2024-2025) (ECE_ΓK703) - Data Bases 2024-2025 project (ECE_GK703):

Για να εκτελεστεί σωστά η εφαρμογή ο χρήστης χρειάζεται να ακολουθήσει τα εξής βήματα:

### Requirements - Απαιτήσεις:

Python: Εγκαταστήστε την Python από τον σύνδεσμο https://www.python.org/downloads/.

Git Bash (optional): Για εύκολη λήψη του repository.

Βήματα Εγκατάστασης:
1. Clone the repository:
   Αν το Git Bash είναι εγκαταστημένο: `git clone https://github.com/ManyaZ1/publishing_house_db`
   
   Αλλιώς:
   Ακολουθήστε τον σύνδεσμο: github.com/ManyaZ1/publishing_house_db.
   Κάντε κλικ στο Code (πράσινο κουμπί) -> επιλέξτε Download ZIP. 
   Αποσυμπιέστε το αρχείο και ανοίξτε ένα τερματικό στο φάκελο.

3. Install requirements and generate database:
   
   Τέλος, εκτελέστε τις εξής εντολές στο τερματικό:

```
cd publishing_house_db 

pip install -r requirements.txt

python ourDB\generate_db_records.py

python ourAPP\main.py
```

Σημείωση: Σε περιβάλλοντα macOS ή Linux, χρησιμοποιήστε / αντί για \ στις διαδρομές. 

Παραπάνω oδηγίες χρήσης της εφαρμογής περιλαμβάνονται στην αναφορά στον φάκελο report.

Σημείωση: Για αλλαγή του μεγέθους της randomly-generated βάσης, χρειάζεται αλλαγή του scale_factor που ορίζεται στην main() του ourDB/generate_db_records.py
