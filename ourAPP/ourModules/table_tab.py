# ourModules/table_tab.py

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
#from main import *
from ourModules.translations import to_display_value, from_display_value, get_specialization_display_values

class TableTab(ttk.Frame):
    """
    Each tab handles CRUD for a single table.
    """
    def __init__(self, parent_notebook, db_manager, table_name, display_name=None):
        super().__init__(parent_notebook)
        
        self.db_manager = db_manager
        self.table_name = table_name
        self.display_name = display_name or table_name.capitalize() # Use display_name if provided
        
        # Retrieve columns info
        self.columns_info = self.db_manager.get_table_columns(self.table_name)
        self.col_names = [col[1] for col in self.columns_info]
        
        # Layout: top for Treeview, bottom for controls
        self.create_treeview_section()
        self.create_form_section()
        self.populate_treeview() # load data

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
            if col == "comments":
                self.tree.column(col, width=120, anchor='w') # w: Align all data in your Treeview to the left! ⭐
        
        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)
        
        # Buttons for Edit - Delete - Unselect
        self.btn_frame = ttk.Frame(self)
        self.btn_frame.pack(side="top", fill="x", padx=5, pady=5)
        
        self.edit_btn = ttk.Button(self.btn_frame, text="Edit Selected", command=self.edit_selected)
        self.edit_btn.pack(side="left", padx=5)
        
        self.delete_btn = ttk.Button(self.btn_frame, text="Delete Selected", command=self.delete_selected)
        self.delete_btn.pack(side="left", padx=5)

        self.unselect_btn = ttk.Button(self.btn_frame, text="Unselect", command=self.unselect_row)
        self.unselect_btn.pack(side="left", padx=5)

        return;
    def create_form_section(self):
        """A frame with Entry widgets for each column (for insert/edit)."""
        self.fields_color="#d6fffd" #name,tax_id labels colors
        self.back_color="#d8d8d6" #background color

        
        # Use tk.LabelFrame instead of ttk.LabelFrame
        self.form_frame = tk.LabelFrame(
            self, 
            text=f"{self.display_name} - Insert / Edit Record",
            bg=  self.back_color ,        #"#f4f4f9",#   "#d6fffd" ,   #"#d9e8f5",  # Set background color
            fg="#333",  # Set text color
            font=("Arial", 10, "bold"),  # Optional font customization
            padx=10, 
            pady=10
        )
        self.form_frame.pack(side="bottom", fill="x", padx=5, pady=5)

        self.entry_vars = {}
        
        # Create a row of labels + entries for each column  #"#d6fffd"
        for index, colinfo in enumerate(self.columns_info):
            col_name = colinfo[1]

            lbl = tk.Label(self.form_frame, text=col_name, width=20, bg=self.fields_color, fg="#333")
            lbl.grid(row=index, column=0, padx=5, pady=2, sticky='w')

            var = tk.StringVar()

            if col_name == "specialisation":  # Use a Combobox
                ent = ttk.Combobox(
                    self.form_frame,
                    textvariable=var,
                    values=get_specialization_display_values(),
                    state='readonly',
                    width=28
                )
            elif col_name == "comments":  # Use a Combobox from 1 -> 5
                ent = ttk.Combobox(
                    self.form_frame,
                    textvariable=var,
                    values=[str(i) for i in range(1, 6)],
                    state='readonly',
                    width=28
                )
            else:  # Normal Entry
                ent = tk.Entry(self.form_frame, textvariable=var, width=30, bg="white")

            ent.grid(row=index, column=1, padx=5, pady=2, sticky='w')
            self.entry_vars[col_name] = var

        # Insert / Update button
        self.action_btn = ttk.Button(self.form_frame, text="Insert", command=self.insert_record)
        self.action_btn.grid(row=len(self.columns_info), column=0, columnspan=2, pady=10)

    def create_form_section_og(self):
        """A frame with Entry widgets for each column (for insert/edit)."""
        # Apply the style in your main code (usually once in your main application)
        # style = ttk.Style()
        # style.theme_use('clam') 
        # style.configure("Custom.TLabelFrame", background="#d9e8f5", foreground="#333")  # Background and text color
        # style.configure("Custom.TLabelFrame.Label", background="#d9e8f5", font=("Arial", 10, "bold"))

        # # Update your LabelFrame
        # self.form_frame = ttk.LabelFrame(self, text=f"{self.display_name} - Insert / Edit Record", padding=10, style="Custom.TLabelFrame")
        # self.form_frame.pack(side="bottom", fill="x", padx=5, pady=5)

        self.form_frame = ttk.LabelFrame(self, text=f"{self.display_name} - Insert / Edit Record", padding=10)
        self.form_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        #self.form_frame = ttk.LabelFrame(self, text="Insert / Edit Record", padding=10, style="Custom.TLabelFrame")

        self.entry_vars = {}
        
        # Create a row of labels+entries for each column
        for index, colinfo in enumerate(self.columns_info):
            col_name = colinfo[1]

            lbl = ttk.Label(self.form_frame, text=col_name, width=20)
            lbl.grid(row=index, column=0, padx=5, pady=2, sticky='w')

            var = tk.StringVar()
            
            if col_name == "specialisation": # Use a Combobox
                ent = ttk.Combobox(
                    self.form_frame,
                    textvariable=var,
                    values = get_specialization_display_values(),
                    state='readonly',
                    width=28
                )
                ent.grid(row=index, column=1, padx=5, pady=2, sticky='w')
            elif col_name == "comments": # Use a Combobox from 1 -> 5
                ent = ttk.Combobox(
                    self.form_frame,
                    textvariable=var,
                    values = [str(i) for i in range(1, 6)],
                    state='readonly',
                    width=28
                )
                ent.grid(row=index, column=1, padx=5, pady=2, sticky='w')
            else: # Normal Entry
                ent = ttk.Entry(self.form_frame, textvariable=var, width=30)
                ent.grid(row=index, column=1, padx=5, pady=2, sticky='w')

            self.entry_vars[col_name] = var

        # Insert / Update button
        self.action_btn = ttk.Button(self.form_frame, text="Insert", command=self.insert_record)
        self.action_btn.grid(row=len(self.columns_info), column=0, columnspan=2, pady=10)

        return;
    
    def populate_treeview(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = self.db_manager.fetchall(f'SELECT * FROM "{self.table_name}"')
        for r in rows:
            display_values = []
            for col_idx, raw_val in enumerate(r):
                col_name = self.col_names[col_idx]
                # Transform the raw_val to a display-friendly value
                display_val = to_display_value(col_name, raw_val)
                display_values.append(display_val)
            
            self.tree.insert("", "end", values=display_values)

        return;
    
    def on_row_select(self, event):
        """When user selects a row from the tree, fill the form for editing."""
        selected_item = self.tree.selection()
        if not selected_item:
            return;
        
        row_data = self.tree.item(selected_item, 'values')
        for col_name, value in zip(self.col_names, row_data): # Fill in the form
            self.entry_vars[col_name].set(value)
        
        # Switch to "Update" mode
        self.action_btn.configure(text="Update", command=self.update_record)

        return;
    
    def insert_record(self):
        """Gather data from entries and perform an INSERT."""
        data = []
        for col in self.col_names:
            val = self.entry_vars[col].get().strip()
            val = from_display_value(col, val) # Convert display value back to raw value
            if val == '':  # if user typed empty string, store None
                val = None
            data.append(val)
        
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
            return;
        
        old_row_data = self.tree.item(selected_item, 'values')
        new_data = []
        for col_name in self.col_names:
            val = self.entry_vars[col_name].get().strip()
            val = from_display_value(col_name, val)
            if val == '':
                val = None
            new_data.append(val)
        
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
        #self.conn.execute("PRAGMA foreign_keys = ON")

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

    def unselect_row(self):
        """Clear any selection in the TreeView and reset the form."""
        self.tree.selection_remove(*self.tree.selection())  # removes all selections
        self.clear_form()  # the same method that resets the entry fields
        
        return;

    def select_row_data(self, row_data):
        """
        Fill the form with the given row_data and select the matching row in the TreeView.
        """
        # 1. Fill in the form fields
        for col_name, value in zip(self.col_names, row_data):
            self.entry_vars[col_name].set("" if value is None else str(value))

        # 2. Find a row in the Treeview that matches `row_data` exactly
        self.tree.selection_remove(*self.tree.selection())  # Clear any previous selection
        
        for item in self.tree.get_children():
            item_values = self.tree.item(item, "values")
            
            # Compare the item_values with the row_data tuple
            # Note: They must match exactly!
            if item_values == row_data:
                self.tree.selection_set(item)
                self.tree.focus(item)  # move focus to that item
                break

        # 3. Switch the action button to "Update"
        self.action_btn.configure(text="Update", command=self.update_record)

        return;