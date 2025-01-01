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
from ourModules.animated_window import AnimatedWindow

class PublishingHouseApp(tk.Tk):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    new_path = os.path.dirname(script_dir)
    db_path = os.path.join(new_path, "publishing_house.db")

    def __init__(self, db_path):
        super().__init__()
        
        self.title("Publishing House DB - GUI")
        self.state('zoomed') # Maximizes the window
        self.canvas_color="#f0d9b5"#"#aeb6bf"#"#f0d9b5" # Background color for the canvas og:"#f0d9b5" tirquiose #c4fefb vissini #d98880
        self.treeview_bg="#fffaf0"#"#e7c88c" # Background color for the treeview og:"#fffaf0" light tirquiose #d6fffd"
        # Style / Colors
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background=self.canvas_color) # main background
        style.configure('TLabel', background=self.canvas_color, foreground="#333")
        style.configure('TNotebook', background=self.canvas_color)
        style.configure('TNotebook.Tab', background="#d1bb93")
        style.configure('TButton', background="#b58863", foreground="#fff", font=('Arial', 10, 'bold'))
        style.map('TButton', background=[('active', '#a57958')])

        style.configure('Treeview', background=self.treeview_bg, fieldbackground=self.treeview_bg, foreground="black") # Treeview background color
        style.configure('Treeview.Heading', background="#b58863", foreground="#fff", font=('Arial', 10, 'bold'))
        #style.configure("TLabelFrame", background="#fffff", foreground="#333")  # Background and text color
        #style.configure("TLabelFrame.Label", background="#f4f4f9", foreground="#333", font=("Arial", 10, "bold"))
        #style.configure("Custom.TLabelFrame", background="#d9e8f5", foreground="#333")
        #style.configure("Custom.TLabelFrame.Label", background="#d9e8f5", foreground="#333", font=("Arial", 10, "bold"))

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
        
        canvas = tk.Canvas(home_frame, bg=self.canvas_color, highlightthickness=0)
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
                bg=self.canvas_color,    #     "#f0d9b5",  #  '#e8ddc9',           #'#ffffff', # Solid background for readability
                fg='#5C4033',#"#333",
                justify='center',
                pady=10,
                wraplength=label_width
            )
            label.place(relx=0.5, rely=0.15, anchor="center")  # Adjust `rely` to 0.4 for slightly above center
            # Center the label
            #anvas.create_window(width//2, height//2, window=label)
            return;
        
        # Initial draw
        self.after(100, draw_emoji) # Delay to allow canvas to initialize size
        
        # Bind the resize event to redraw emojis
        canvas.bind("<Configure>", draw_emoji)

        return;

    def open_search_window(self):
        temp = SearchWindow(self, self.db_manager)
        animator = AnimatedWindow(temp, start_size=(100, 100), final_size=(1280, 700), duration=400)
        temp.protocol("WM_DELETE_WINDOW", animator.close_animation)
        animator.open_animation()

        return;

    def open_stats_window(self):
        temp = StatsWindow(self, self.db_manager)
        animator = AnimatedWindow(temp, start_size=(100, 100), final_size=(1280, 700), duration=400)
        temp.protocol("WM_DELETE_WINDOW", animator.close_animation)
        animator.open_animation()

        return;

    def on_closing(self):
        """Prompt user, then close connection and destroy window if confirmed."""
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.db_manager.close_connection()
            exit();

        return;

    def select_row_in_table(self, table_name, row_data): #
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
