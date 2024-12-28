# main.py

import os
from sys import exit
import tkinter as tk
from tkinter import ttk, messagebox

from ourModules.database_manager import DatabaseManager
from ourModules.table_tab import TableTab
from ourModules.search_window import SearchWindow
from ourModules.stats_window import StatsWindow

from ourModules.translations import table_to_display

class PublishingHouseApp(tk.Tk):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    new_path = os.path.dirname(script_dir)
    db_path = os.path.join(new_path, "publishing_house.db")

    def __init__(self, db_path):
        super().__init__()
        
        self.title("Publishing House DB - GUI")
        self.state('zoomed') # Maximizes the window
        
        # Style / Colors
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background="#f0d9b5") # main background
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
        
        # Notebook. Η λειτουργία του notebook είναι να μπορεί να έχει πολλά tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create a "Home" tab
        self.create_home_tab()
        
        # Create a tab for each table in the DB
        self.table_frames = {} # Store the TableTab instances
        table_list = self.db_manager.get_table_list() # Get the list of tables from the DB
        for table in table_list:
            display_name = table_to_display(table)
            frame = TableTab(self.notebook, self.db_manager, table, display_name=display_name)
            self.table_frames[table] = frame
            self.notebook.add(frame, text=display_name)

        # Clean up on close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        return;

    def create_home_tab(self):
        """
        A 'Home' tab with a background book emoji and instructions.
        """
        home_frame = ttk.Frame(self.notebook)
        self.notebook.add(home_frame, text="Home")
        
        canvas = tk.Canvas(home_frame, bg="#f0d9b5", highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        
        emoji = "📖 📖"#"📖"
        emoji_font = ("Arial", 280)
        def draw_emoji(event=None):
            canvas.delete("all") # Clear existing emojis
            #(width, height) = (canvas.winfo_width(), canvas.winfo_height())
            #draw the emoji in the center of the canvas with adjusted font size

            (width, height) = (canvas.winfo_width(), canvas.winfo_height())
            canvas.create_text(
                width//2, height//2-height//14,
                text=emoji,
                font=emoji_font,
                fill= '#5C4033' #"#ba5d7e"#"#d1bb93" # Emoji color (adjust as needed)
            )
            # Add the instruction label on top
            instruction_text = (
                "Welcome to the Publishing House Database!\n\n"
                "Use the tabs above to view, insert, or edit data in each table.\n"
                "Or click the buttons (top-left) to open the Search or Statistics windows.\n\n"
                "Enjoy exploring your database!"
            )
            label_width = 800
            label = tk.Label(
                canvas,
                text=instruction_text,
                anchor="center",
                #height= height // 10,
                #width= canvas.winfo_width() // 20,
                font=('Calibri', 14, 'bold'),
                bg="#f0d9b5",#  '#e8ddc9',           #'#ffffff', # Solid background for readability
                fg='#5C4033',#"#333",
                justify='center',
                pady=10,
                wraplength=label_width
            )
            label.place(relx=0.5, rely=0.15, anchor="center")  # Adjust `rely` to 0.4 for slightly above center
            # Center the label
            #anvas.create_window(width//2, height//2, window=label)
            return;
        '''def draw_emojis(event=None):
            canvas.delete("all") # Clear existing emojis
            (width, height) = (canvas.winfo_width(), canvas.winfo_height())

            # Horizontal & Vertical spacing between emojis
            (emoji_spacing_x, emoji_spacing_y) = (50, 40)

            # Introduce padding to prevent cutting emojis at edges
            (padding_x, padding_y) = (emoji_spacing_x // 2, emoji_spacing_y // 2)
            
            # Calculate number of emojis that fit horizontally and vertically
            (columns, rows) = (width // emoji_spacing_x, height // emoji_spacing_y)
            
            for row in range(rows):
                for col in range(columns):
                    (x, y) = (col * emoji_spacing_x + padding_x, row * emoji_spacing_y + padding_y)
                    canvas.create_text(
                        x, y,
                        text=emoji,
                        font=emoji_font,
                        fill="#d1bb93" # Emoji color (adjust as needed)
                    )
            
            # Add the instruction label on top
            instruction_text = (
                "Welcome to the Publishing House Database!\n\n"
                "Use the tabs above to view, insert, or edit data in each table.\n"
                "Or click the buttons (top-left) to open the Search or Statistics windows.\n\n"
                "Enjoy exploring your database!"
            )
            label_width = 800
            label = tk.Label(
                canvas,
                text=instruction_text,
                anchor="center",
                font=('Arial', 14, 'bold'),
                bg='#ffffff', # Solid background for readability
                fg="#333",
                justify='left',
                wraplength=label_width
            )
            # Center the label
            canvas.create_window(width//2, height//2, window=label)

            return;'''
        
        # Initial draw
        self.after(100, draw_emoji) # Delay to allow canvas to initialize size
        
        # Bind the resize event to redraw emojis
        canvas.bind("<Configure>", draw_emoji)

        return;

    def open_search_window(self):
        SearchWindow(self, self.db_manager)
        return;

    def open_stats_window(self):
        StatsWindow(self, self.db_manager)
        return;

    def on_closing(self):
        """Prompt user, then close connection and destroy window if confirmed."""
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.db_manager.close_connection()
            exit();

        return;

    def select_row_in_table(self, table_name, row_data):
        # table_name should exactly match a key in self.table_frames
        if table_name not in self.table_frames:
            messagebox.showerror("Error", f"Table '{table_name}' not found in table_frames!")
            return

        # Switch to that table's tab
        # One way is to find the index:
        keys_list = list(self.table_frames.keys())
        index = keys_list.index(table_name)
        self.notebook.select(index + 1) # +1 because the first tab is the "Home" tab!

        # Then fill in the data
        frame = self.table_frames[table_name]
        frame.select_row_data(row_data) # Call the method in TableTab

        return;

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    new_path   = os.path.dirname(script_dir)
    app = PublishingHouseApp(db_path=os.path.join(new_path, "publishing_house.db"))
    app.mainloop()

    return;

if __name__ == "__main__":
    main()
