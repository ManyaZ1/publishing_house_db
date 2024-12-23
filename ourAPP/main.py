# main.py

import os
import tkinter as tk
from tkinter import ttk

# Import your modules from the mymodules directory
from ourModules.database_manager import DatabaseManager
from ourModules.table_tab import TableTab
from ourModules.search_window import SearchWindow
from ourModules.stats_window import StatsWindow
import os
import tkinter as tk
from tkinter import ttk

# Import your modules from the mymodules directory
from ourModules.database_manager import DatabaseManager
from ourModules.table_tab import TableTab
from ourModules.search_window import SearchWindow
from ourModules.stats_window import StatsWindow

class PublishingHouseApp(tk.Tk):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #print(f"Script directory: {script_dir}")

# Remove the last folder 'ourDB'
    new_path = os.path.dirname(script_dir)

    #print("New path:", new_path)
    #cwd = os.getcwd()
    #print(f"Current working directory: {cwd}")
    db_path = new_path + "/publishing_house.db"
    def __init__(self, db_path):
        super().__init__()
        
        self.title("Publishing House DB - GUI")
        self.geometry("1100x650")
        
        # Style / Colors
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background="#f0d9b5")    # main background
        style.configure('TLabel', background="#f0d9b5", foreground="#333")
        style.configure('TNotebook', background="#f0d9b5")
        style.configure('TNotebook.Tab', background="#d1bb93")
        style.configure('TButton', background="#b58863", foreground="#fff", font=('Arial', 10, 'bold'))
        style.map('TButton', background=[('active', '#a57958')])

        style.configure('Treeview', background="#fffaf0", fieldbackground="#fffaf0", foreground="black")
        style.configure('Treeview.Heading', background="#b58863", foreground="#fff", font=('Arial', 10, 'bold'))

        # Database
        self.db_manager = DatabaseManager(db_path)
        
        # Top button frame
        self.top_button_frame = ttk.Frame(self, padding=10)
        self.top_button_frame.pack(side="top", fill="x")
        
        # Buttons for search/stats
        self.search_button = ttk.Button(self.top_button_frame, text="Search", command=self.open_search_window)
        self.search_button.pack(side="left", padx=5)
        
        self.stats_button = ttk.Button(self.top_button_frame, text="Statistics", command=self.open_stats_window)
        self.stats_button.pack(side="left", padx=5)
        
        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create a "Home" tab
        self.create_home_tab()
        
        # Create a tab for each table in the DB
        self.table_frames = {}
        table_list = self.db_manager.get_table_list()
        for table in table_list:
            frame = TableTab(self.notebook, self.db_manager, table)
            self.table_frames[table] = frame
            self.notebook.add(frame, text=table)

        # Clean up on close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        return
    
    def create_home_tab(self):
        """
        A simple 'Home' tab with instructions or an overview.
        """
        home_frame = ttk.Frame(self.notebook)
        label = ttk.Label(
            home_frame, 
            text=(
                "Welcome to the Publishing House Database!\n\n"
                "Use the tabs above to view, insert, or edit data in each table.\n"
                "Or click the buttons (top-left) to open the Search or Statistics windows.\n\n"
                "Enjoy exploring your database!"
            ),
            anchor="center",
            font=('Arial', 12, 'bold')
        )
        label.pack(padx=10, pady=10, expand=True, fill='both')
        
        self.notebook.add(home_frame, text="Home")

        return
    
    def open_search_window(self):
        SearchWindow(self, self.db_manager)

        return
    
    def open_stats_window(self):
        StatsWindow(self, self.db_manager)

        return

    def on_closing(self):
        self.db_manager.close_connection()
        self.destroy()

        return

def main():
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    app = PublishingHouseApp(db_path=cwd + "/publishing_house.db")
    app.mainloop()

    return

if __name__ == "__main__":
    main()

'''
class PublishingHouseApp(tk.Tk):
    def __init__(self, db_path="publishing_house.db"):
        super().__init__()
        
        self.title("Publishing House DB - GUI")
        self.geometry("1100x650")
        
        # Style / Colors
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background="#f0d9b5")    # main background
        style.configure('TLabel', background="#f0d9b5", foreground="#333")
        style.configure('TNotebook', background="#f0d9b5")
        style.configure('TNotebook.Tab', background="#d1bb93")
        style.configure('TButton', background="#b58863", foreground="#fff", font=('Arial', 10, 'bold'))
        style.map('TButton', background=[('active', '#a57958')])

        style.configure('Treeview', background="#fffaf0", fieldbackground="#fffaf0", foreground="black")
        style.configure('Treeview.Heading', background="#b58863", foreground="#fff", font=('Arial', 10, 'bold'))

        # Database
        self.db_manager = DatabaseManager(db_path)
        
        # Top button frame
        self.top_button_frame = ttk.Frame(self, padding=10)
        self.top_button_frame.pack(side="top", fill="x")
        
        # Buttons for search/stats
        self.search_button = ttk.Button(self.top_button_frame, text="Search", command=self.open_search_window)
        self.search_button.pack(side="left", padx=5)
        
        self.stats_button = ttk.Button(self.top_button_frame, text="Statistics", command=self.open_stats_window)
        self.stats_button.pack(side="left", padx=5)
        
        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create a "Home" tab
        self.create_home_tab()
        
        # Create a tab for each table in the DB
        self.table_frames = {}
        table_list = self.db_manager.get_table_list()
        for table in table_list:
            frame = TableTab(self.notebook, self.db_manager, table)
            self.table_frames[table] = frame
            self.notebook.add(frame, text=table)

        # Clean up on close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        return;
    
    def create_home_tab(self):
        """
        A simple 'Home' tab with instructions or an overview.
        """
        home_frame = ttk.Frame(self.notebook)
        label = ttk.Label(
            home_frame, 
            text=(
                "Welcome to the Publishing House Database!\n\n"
                "Use the tabs above to view, insert, or edit data in each table.\n"
                "Or click the buttons (top-left) to open the Search or Statistics windows.\n\n"
                "Enjoy exploring your database!"
            ),
            anchor="center",
            font=('Arial', 12, 'bold')
        )
        label.pack(padx=10, pady=10, expand=True, fill='both')
        
        self.notebook.add(home_frame, text="Home")

        return;
    
    def open_search_window(self):
        SearchWindow(self, self.db_manager)

        return;
    
    def open_stats_window(self):
        StatsWindow(self, self.db_manager)

        return;

    def on_closing(self):
        self.db_manager.close_connection()
        self.destroy()

        return;

def main():
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    app = PublishingHouseApp(db_path= cwd +"/ourDB/publishing_house.db" )#"../ourDB/publishing_house.db"
    app.mainloop()

    return;

if __name__ == "__main__":
    main()'''
