# ourModules/search_window.py

import tkinter as tk
from tkinter import ttk, messagebox

class SearchWindow(tk.Toplevel):
    """
    A separate Toplevel window for searching the database.
    """
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        
        self.title("Search Database")
        self.geometry("700x400")
        self.db_manager = db_manager
        
        # Container frame
        container = ttk.Frame(self, padding=10)
        container.pack(expand=True, fill='both')
        
        lbl_title = ttk.Label(container, text="Search the Database", font=('Arial', 14, 'bold'))
        lbl_title.pack(pady=5)
        
        controls_frame = ttk.Frame(container)
        controls_frame.pack(pady=5)
        
        # Table selection
        lbl_table = ttk.Label(controls_frame, text="Table:")
        lbl_table.grid(row=0, column=0, padx=5, pady=5)
        
        self.table_var = tk.StringVar()
        tables = self.db_manager.get_table_list()
        self.cmb_table = ttk.Combobox(controls_frame, textvariable=self.table_var, values=tables, state='readonly')
        self.cmb_table.grid(row=0, column=1, padx=5, pady=5)
        self.cmb_table.bind("<<ComboboxSelected>>", self.on_table_selected)
        
        # Column selection
        lbl_column = ttk.Label(controls_frame, text="Column:")
        lbl_column.grid(row=1, column=0, padx=5, pady=5)
        
        self.column_var = tk.StringVar()
        self.cmb_column = ttk.Combobox(controls_frame, textvariable=self.column_var, values=[], state='readonly')
        self.cmb_column.grid(row=1, column=1, padx=5, pady=5)
        
        # Operator
        lbl_op = ttk.Label(controls_frame, text="Operator:")
        lbl_op.grid(row=2, column=0, padx=5, pady=5)
        
        self.op_var = tk.StringVar(value='LIKE')
        operators = ['=', 'LIKE', '<', '>', '<=', '>=']
        self.cmb_op = ttk.Combobox(controls_frame, textvariable=self.op_var, values=operators, state='readonly')
        self.cmb_op.grid(row=2, column=1, padx=5, pady=5)
        
        # Value
        lbl_value = ttk.Label(controls_frame, text="Value:")
        lbl_value.grid(row=3, column=0, padx=5, pady=5)
        
        self.value_var = tk.StringVar()
        self.ent_value = ttk.Entry(controls_frame, textvariable=self.value_var)
        self.ent_value.grid(row=3, column=1, padx=5, pady=5)
        
        # Search button
        btn_search = ttk.Button(controls_frame, text="Search", command=self.run_search)
        btn_search.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Treeview for results
        self.tree_frame = ttk.Frame(container)
        self.tree_frame.pack(expand=True, fill='both', pady=5)
        
        self.scroll_y = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.scroll_y.pack(side="right", fill="y")
        
        self.results_tree = ttk.Treeview(self.tree_frame, show='headings', yscrollcommand=self.scroll_y.set)
        self.results_tree.pack(side="left", fill="both", expand=True)
        self.scroll_y.config(command=self.results_tree.yview)

        return;
    
    def on_table_selected(self, event):
        """Load column names for the chosen table."""
        table_name = self.table_var.get()
        columns_info = self.db_manager.get_table_columns(table_name)
        col_names = [col[1] for col in columns_info]
        self.cmb_column['values'] = col_names
        if col_names:
            self.cmb_column.current(0)

        return;
    
    def run_search(self):
        """Build a SELECT query based on the user's inputs."""
        table = self.table_var.get()
        column = self.column_var.get()
        operator = self.op_var.get()
        value = self.value_var.get().strip()
        
        if not table or not column:
            messagebox.showwarning("Warning", "Please select a table and column.")
            return
        
        if operator.upper() == "LIKE":
            where_clause = f'"{column}" LIKE ?'
            params = (f'%{value}%', )
        else:
            where_clause = f'"{column}" {operator} ?'
            params = (value, )
        
        query = f'SELECT * FROM "{table}" WHERE {where_clause}'
        
        try:
            rows = self.db_manager.fetchall(query, params)
            self.display_results(rows, table)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed:\n{e}")

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
        
        for row in rows:
            self.results_tree.insert("", "end", values=row)
        
        return;
