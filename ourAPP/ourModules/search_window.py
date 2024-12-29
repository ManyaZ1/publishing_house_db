# ourModules/search_window.py

from time import perf_counter
from difflib import get_close_matches
import tkinter as tk
from tkinter import ttk, messagebox
from ourModules.translations import from_display_value, to_display_value, table_to_display, table_from_display
# ourModules.translations.py, επειδή το θέλει βάση το που είναι το αρχείο από την θέση της main.py

class SearchWindow(tk.Toplevel):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        
        self.title("🔎")
        self.initialize_window()
        self.db_manager = db_manager
        
        # ------------ Container frame ------------
        container = ttk.Frame(self, padding=10)
        container.pack(expand=True, fill='both')
        
        lbl_title = ttk.Label(container, text="- Search the Database -", font=('Arial', 14, 'bold'))
        lbl_title.pack(pady=5)
        
        controls_frame = ttk.Frame(container)
        controls_frame.pack(pady=5)
        
        # ------------ Table selection ------------
        lbl_table = ttk.Label(controls_frame, text="Table:")
        lbl_table.grid(row=0, column=0, padx=5, pady=5)
        
        self.table_var = tk.StringVar()
        
        # 3. Get the actual table names from the DB, then map them to friendly names
        tables_raw = self.db_manager.get_table_list()  # actual DB table names
        tables_display = [table_to_display(t) for t in tables_raw]
        
        self.cmb_table = ttk.Combobox(
            controls_frame,
            textvariable=self.table_var,
            values=tables_display,
            state='readonly'
        )
        self.cmb_table.grid(row=0, column=1, padx=5, pady=5)
        self.cmb_table.bind("<<ComboboxSelected>>", self.on_table_selected)
        
        # ------------ Column selection ------------
        lbl_column = ttk.Label(controls_frame, text="Column:")
        lbl_column.grid(row=1, column=0, padx=5, pady=5)
        
        self.column_var = tk.StringVar()
        self.cmb_column = ttk.Combobox(controls_frame, textvariable=self.column_var, values=[], state='readonly')
        self.cmb_column.grid(row=1, column=1, padx=5, pady=5)
        
        # ------------ Operator ------------
        lbl_op = ttk.Label(controls_frame, text="Operator:")
        lbl_op.grid(row=2, column=0, padx=5, pady=5)
        
        self.op_var = tk.StringVar(value='LIKE')
        operators = ['=', 'LIKE', '<', '>', '<=', '>=']
        self.cmb_op = ttk.Combobox(controls_frame, textvariable=self.op_var, values=operators, state='readonly')
        self.cmb_op.grid(row=2, column=1, padx=5, pady=5)
        
        # ------------ Value ------------
        lbl_value = ttk.Label(controls_frame, text="Value:")
        lbl_value.grid(row=3, column=0, padx=5, pady=5)
        
        self.value_var = tk.StringVar()
        self.ent_value = ttk.Entry(controls_frame, textvariable=self.value_var)
        self.ent_value.grid(row=3, column=1, padx=5, pady=5)
        
        # Edit button - Transfer Data in main window
        btn_select = ttk.Button(controls_frame, text="Edit selected", command=self.select_for_editing)
        btn_select.grid(row=4, column=0, columnspan=1, pady=5)

        # ------------ Search button ------------
        btn_search = ttk.Button(controls_frame, text="Search", command=self.run_search)
        btn_search.grid(row=4, column=1, columnspan=1, pady=5)
        
        # ------------ Treeview for results ------------
        self.tree_frame = ttk.Frame(container)
        self.tree_frame.pack(expand=True, fill='both', pady=5)
        
        self.scroll_y = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.scroll_y.pack(side="right", fill="y")
        
        self.results_tree = ttk.Treeview(self.tree_frame, show='headings', yscrollcommand=self.scroll_y.set)
        self.results_tree.pack(side="left", fill="both", expand=True)
        self.scroll_y.config(command=self.results_tree.yview)

        # Frame for displaying search metadata
        self.metadata_frame = ttk.Frame(container)
        self.metadata_frame.pack(fill='x', pady=5)

        # Label for elapsed time
        self.lbl_time = ttk.Label(self.metadata_frame, text="Time Elapsed: ~ seconds")
        self.lbl_time.pack(side='left', padx=10)

        # Label for result count
        self.lbl_count = ttk.Label(self.metadata_frame, text="Results Found: ~")
        self.lbl_count.pack(side='left', padx=10)

        return;

    def initialize_window(self):
        (window_width, window_height) = (1200, 700)
        (screen_width, screen_height) = (self.winfo_screenwidth(), self.winfo_screenheight())
        (x, y) = ((screen_width // 2) - (window_width // 2), (screen_height // 2) - (window_height // 2))
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        return;

    def bring_to_front(self):
        """Bring the window to the front, set focus, and ensure it's visible."""
        self.focus_set()   # Set focus to the window
        self.deiconify()   # Restore the window if it was minimized or hidden
        self.lift()        # Bring the window to the top of the window stack

        return;
    
    def on_table_selected(self, event):
        """Load column names for the chosen table."""
        # Convert the friendly name from the combo box back to the actual table name
        user_friendly_name = self.table_var.get()
        actual_table_name = table_from_display(user_friendly_name)

        columns_info = self.db_manager.get_table_columns(actual_table_name)
        col_names = [col[1] for col in columns_info]
        self.cmb_column['values'] = col_names
        if col_names:
            self.cmb_column.current(0)
        
        return;
    
    def run_search(self, suggested_value=None):
        """Build a SELECT query based on the user's inputs."""
        # Convert the selected table from friendly name to actual DB name
        table_friendly = self.table_var.get()
        table = table_from_display(table_friendly)
        
        column = self.column_var.get()
        operator = self.op_var.get()
        value = suggested_value if suggested_value is not None \
            else self.value_var.get().strip()
        
        if not table or not column:
            messagebox.showwarning("Warning", "Please select a table and column.", parent=self)
            self.bring_to_front() # After a message box is dismissed

            return;
        
        if operator.upper() == "LIKE":
            where_clause = f'"{column}" LIKE ?'
            params = (f'%{value}%', )
        else:
            where_clause = f'"{column}" {operator} ?'
            params = (value, )
        
        query = f'SELECT * FROM "{table}" WHERE {where_clause}'
        
        try:
            start_time =   perf_counter() # Start timing
            rows_raw =     self.db_manager.fetchall(query, params)
            end_time =     perf_counter() # Stop timing
            elapsed_time = end_time - start_time
            
            # Convert raw rows to display-friendly rows
            rows = [
                tuple(
                    to_display_value(col_name, r)
                    for col_name, r in zip(self.cmb_column['values'], row)
                )
                for row in rows_raw
            ]
            self.display_results(rows, table) # Display the results in the Treeview
            
            # Update the elapsed time and result count labels
            self.lbl_time.config(text=f"Time Elapsed: {elapsed_time:.4f} seconds")
            self.lbl_count.config(text=f"Results Found: {len(rows)}")

            # Suggestion logic
            if len(rows) == 0 and suggested_value is None:
                # Fetch all existing items from the database using fetchall directly
                get_everything_query = f'SELECT "{column}" FROM "{table}"'
                everything_raw = self.db_manager.fetchall(get_everything_query)
                everything = [str(row[0]) for row in everything_raw if row[0] is not None]
                # str(), αλλιώς TypeError: object of type 'int' has no len()!
                
                # Use difflib to find close matches with a cutoff for similarity
                suggestions = get_close_matches(value, everything, n=1, cutoff=0.8)
                if suggestions:
                    suggested = suggestions[0]
                    message = f"No results found for '{value}'.\n - - -> Did you mean: '{suggested}'?"
                    response = messagebox.askyesno("Suggestion", message, parent=self)
                    self.bring_to_front() # After a message box is dismissed
                    if response:
                        # If user agrees, perform the search with the suggested value
                        self.value_var.set(suggested)
                        self.run_search(suggested_value=suggested)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed:\n{e}", parent=self)
            self.bring_to_front() # After a message box is dismissed

        return;
    
    def display_results(self, rows, table_name):
        """Populate the results_tree with the query results."""
        # Clear old columns
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_tree["columns"] = ()
        
        # Get columns info
        columns_info = self.db_manager.get_table_columns(table_name)
        col_names = [col[1] for col in columns_info]
        
        self.results_tree["columns"] = col_names
        for c in col_names:
            self.results_tree.heading(c, text=c)
            self.results_tree.column(c, width=120, anchor='center')
            if c == "comments":
                self.results_tree.column(c, width=120, anchor='w') # w: Align all data in your Treeview to the left! ⭐
        
        for row in rows:
            self.results_tree.insert("", "end", values=row)

        return;

    def select_for_editing(self):
        # Get selected row from the results_tree
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a row in the search results first.", parent=self)
            self.bring_to_front() # After a message box is dismissed

            return;

        # We assume only one row selected
        row_data = self.results_tree.item(selected, 'values')
        # Δεν χρειάζεται μετατροπή, είναι ήδη σε display value το main Window!
        
        # Get the actual table name
        table_friendly = self.table_var.get()
        table = table_from_display(table_friendly)
        
        # Call a method on the parent (the main app) to select the row
        self.master.select_row_in_table(table, row_data)
        
        self.destroy()

        return;
