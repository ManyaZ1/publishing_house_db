# ourModules/table_tab.py

import tkinter as tk
from tkinter import ttk, messagebox

class TableTab(ttk.Frame):
    """
    Each tab handles CRUD for a single table.
    """
    def __init__(self, parent_notebook, db_manager, table_name):
        super().__init__(parent_notebook)
        
        self.db_manager = db_manager
        self.table_name = table_name
        
        # Retrieve columns info
        self.columns_info = self.db_manager.get_table_columns(self.table_name)
        self.col_names = [col[1] for col in self.columns_info]
        
        # Layout: top for Treeview, bottom for controls
        self.create_treeview_section()
        self.create_form_section()
        self.populate_treeview()  # load data

        return;
    
    def create_treeview_section(self):
        """Create a Treeview to show all rows for the given table."""
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=self.col_names,
            show='headings',
            yscrollcommand=self.tree_scroll.set
        )
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree_scroll.config(command=self.tree.yview)
        
        # Set up headings
        for col in self.col_names:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        
        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)
        
        # Buttons for Edit & Delete
        self.btn_frame = ttk.Frame(self)
        self.btn_frame.pack(side="top", fill="x", padx=5, pady=5)
        
        self.edit_btn = ttk.Button(self.btn_frame, text="Edit Selected", command=self.edit_selected)
        self.edit_btn.pack(side="left", padx=5)
        
        self.delete_btn = ttk.Button(self.btn_frame, text="Delete Selected", command=self.delete_selected)
        self.delete_btn.pack(side="left", padx=5)

        return;
    
    def create_form_section(self):
        """A frame with Entry widgets for each column (for insert/edit)."""
        self.form_frame = ttk.LabelFrame(self, text="Insert / Edit Record", padding=10)
        self.form_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        self.entry_vars = {}
        
        # Create a row of labels+entries for each column
        for index, colinfo in enumerate(self.columns_info):
            col_name = colinfo[1]
            
            lbl = ttk.Label(self.form_frame, text=col_name, width=20)
            lbl.grid(row=index, column=0, padx=5, pady=2, sticky='w')
            
            var = tk.StringVar()
            ent = ttk.Entry(self.form_frame, textvariable=var, width=30)
            ent.grid(row=index, column=1, padx=5, pady=2, sticky='w')
            self.entry_vars[col_name] = var
        
        # Insert / Update button
        self.action_btn = ttk.Button(self.form_frame, text="Insert", command=self.insert_record)
        self.action_btn.grid(row=len(self.columns_info), column=0, columnspan=2, pady=10)

        return;
    
    def populate_treeview(self):
        """Load all data from the table into the treeview."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        rows = self.db_manager.fetchall(f'SELECT * FROM "{self.table_name}"')
        for r in rows:
            self.tree.insert("", "end", values=r)

        return;
    
    def on_row_select(self, event):
        """When user selects a row from the tree, fill the form for editing."""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        row_data = self.tree.item(selected_item, 'values')
        
        # Fill in the form
        for col_name, value in zip(self.col_names, row_data):
            self.entry_vars[col_name].set(value)
        
        # Switch to "Update" mode
        self.action_btn.configure(text="Update", command=self.update_record)

        return;
    
    def insert_record(self):
        """Gather data from entries and perform an INSERT."""
        data = []
        for col in self.col_names:
            val = self.entry_vars[col].get().strip()
            data.append(val if val != '' else None)
        
        placeholders = ", ".join(["?" for _ in data])
        columns = ", ".join([f'"{c}"' for c in self.col_names])
        query = f'INSERT INTO "{self.table_name}" ({columns}) VALUES ({placeholders})'
        
        try:
            self.db_manager.execute(query, data)
            messagebox.showinfo("Success", "Record inserted successfully.")
            self.populate_treeview()
            self.clear_form()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"Insertion failed. IntegrityError: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not insert record.\n{e}")

        return;
    
    def update_record(self):
        """Gather data from entries and perform an UPDATE on the selected record."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No row selected.")
            return
        
        old_row_data = self.tree.item(selected_item, 'values')
        
        new_data = []
        for col_name in self.col_names:
            new_data.append(self.entry_vars[col_name].get().strip())
        
        set_clause = ", ".join([f'"{c}"=?' for c in self.col_names])
        
        # Identify PK columns
        pk_cols = [col[1] for col in self.columns_info if col[5] != 0]
        if not pk_cols:
            # If no PK, match on all columns of the old row
            pk_cols = self.col_names
        
        where_clause_parts = []
        where_params = []
        
        for idx, col_name in enumerate(self.col_names):
            if col_name in pk_cols:
                where_clause_parts.append(f'"{col_name}"=?')
                where_params.append(old_row_data[idx])
        
        where_clause = " AND ".join(where_clause_parts)
        query = f'UPDATE "{self.table_name}" SET {set_clause} WHERE {where_clause}'
        
        params = new_data + where_params
        
        try:
            self.db_manager.execute(query, params)
            messagebox.showinfo("Success", "Record updated successfully.")
            self.populate_treeview()
            self.clear_form()
            # Switch button back to Insert
            self.action_btn.configure(text="Insert", command=self.insert_record)
        except Exception as e:
            messagebox.showerror("Error", f"Could not update record.\n{e}")

        return;
    
    def delete_selected(self):
        """Delete the selected row from the DB."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No row selected to delete.")
            return;
        
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete?")
        if not confirm:
            return;
        
        row_data = self.tree.item(selected_item, 'values')
        
        pk_cols = [col[1] for col in self.columns_info if col[5] != 0]
        if not pk_cols:
            pk_cols = self.col_names
        
        where_clause_parts = []
        where_params = []
        
        for idx, col_name in enumerate(self.col_names):
            if col_name in pk_cols:
                where_clause_parts.append(f'"{col_name}"=?')
                where_params.append(row_data[idx])
        
        where_clause = " AND ".join(where_clause_parts)
        query = f'DELETE FROM "{self.table_name}" WHERE {where_clause}'
        
        try:
            self.db_manager.execute(query, where_params)
            self.tree.delete(selected_item)
            messagebox.showinfo("Success", "Record deleted successfully.")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete record.\n{e}")

        return;
    
    def edit_selected(self):
        """Manually trigger row selection logic for editing."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No row selected to edit.")
            return;
        self.on_row_select(None)

        return;
    
    def clear_form(self):
        """Resets the entry fields to empty and resets the action button."""
        for col in self.entry_vars:
            self.entry_vars[col].set("")
        self.action_btn.configure(text="Insert", command=self.insert_record)

        return;
