# ourModules/stats_window.py

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class StatsWindow(tk.Toplevel):
    """
    A separate Toplevel window for statistics & charts.
    """
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        
        self.title("Database Statistics")

        window_width = 1200
        window_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.db_manager = db_manager
        
        # Main container
        container = ttk.Frame(self, padding=10)
        container.pack(expand=True, fill='both')
        
        lbl_title = ttk.Label(container, text="Statistics & Charts", font=('Arial', 14, 'bold'))
        lbl_title.pack(pady=5)
        
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=5)
        
        # Example: Show Book Stock
        btn_show_stock = ttk.Button(btn_frame, text="Show Book Stock Chart", command=self.plot_book_stock)
        btn_show_stock.pack(side="left", padx=5)

        # Show Money Earned
        btn_money_earned = ttk.Button(btn_frame, text="Show Money Earned", command=self.plot_money_earned)
        btn_money_earned.pack(side="left", padx=5)

        # Show Accounts Payable to Printing House
        btn_accounts_payable = ttk.Button(btn_frame, text="Show Accounts Payable to Printing House",
                                          command=self.plot_accounts_payable_printing_house)
        btn_accounts_payable.pack(side="left", padx=5)
        
        # A frame to hold the matplotlib figure
        self.plot_frame = ttk.Frame(container)
        self.plot_frame.pack(expand=True, fill='both')
        
        self.canvas = None

        return
    
    def plot_book_stock(self):
        """Example: Query PUBLICATION table for (title, stock), make a bar chart."""
        try:
            rows = self.db_manager.fetchall('SELECT "title", "stock" FROM "PUBLICATION"')
            titles = [r[0] for r in rows]
            stocks = [r[1] for r in rows]
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch book stock:\n{e}")
            return
        
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(titles, stocks, color='blue')
        ax.set_xlabel('Book Title', fontsize=12)
        ax.set_ylabel('Stock Count', fontsize=12)
        ax.set_title('Book Stock Levels', fontsize=14)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        self.show_plot(fig)

        return
    
    def plot_money_earned(self):
        """
        Example: sum of "payment" per year from the "client_orders" table.
        Adjust as needed if your schema differs.
        """
        try:
            rows = self.db_manager.fetchall('''
                SELECT strftime('%Y', "order date") AS Year, SUM("payment") AS Total_Earned
                FROM "client_orders"
                GROUP BY Year
                ORDER BY Year
            ''')
            # Each row is (Year, Total_Earned)
            years = [r[0] if r[0] else "Unknown" for r in rows]
            sums = [r[1] if r[1] else 0 for r in rows]
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch money earned:\n{e}")
            return
        
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(years, sums, color='green')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Money Earned', fontsize=12)
        ax.set_title('Money Earned by Year', fontsize=14)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        self.show_plot(fig)

        return

    def plot_accounts_payable_printing_house(self):
        try:
            rows = self.db_manager.fetchall('''
                SELECT strftime('%Y', "order date") AS Year, SUM("cost") AS Total_Payable
                FROM "order_printing_house"
                GROUP BY Year
                ORDER BY Year
            ''')
            # Each row is (Year, Total_Payable)
            years = [r[0] if r[0] else "Unknown" for r in rows]
            sums = [r[1] if r[1] else 0 for r in rows]
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch accounts payable:\n{e}")
            return
        
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(years, sums, color='green')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Total Payable', fontsize=12)
        ax.set_title('Printing Costs by Year', fontsize=14)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        self.show_plot(fig)

        return
    
    def show_plot(self, fig):
        """Embed the Matplotlib figure in the plot_frame."""
        for child in self.plot_frame.winfo_children():
            child.destroy()
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill='both')

        return

''''''
# class StatsWindow(tk.Toplevel):
#     """
#     A separate Toplevel window for statistics & charts.
#     """
#     def __init__(self, parent, db_manager):
#         super().__init__(parent)
        
#         self.title("Database Statistics")
#         self.geometry("800x500")
#         self.db_manager = db_manager
        
#         # Main container
#         container = ttk.Frame(self, padding=10)
#         container.pack(expand=True, fill='both')
        
#         lbl_title = ttk.Label(container, text="Statistics & Charts", font=('Arial', 14, 'bold'))
#         lbl_title.pack(pady=5)
        
#         btn_frame = ttk.Frame(container)
#         btn_frame.pack(pady=5)
        
#         # Example: Show Book Stock
#         btn_show_stock = ttk.Button(btn_frame, text="Show Book Stock Chart", command=self.plot_book_stock)
#         btn_show_stock.pack(side="left", padx=5)

#         # Show Money Earned
#         btn_money_earned = ttk.Button(btn_frame, text="Show Money Earned", command=self.plot_money_earned)
#         btn_money_earned.pack(side="left", padx=5)

#         # Show Accounts Payable to Printing House
#         btn_accounts_payable = ttk.Button(btn_frame, text="Show Accounts Payable to Printing House",
#                                           command=self.plot_accounts_payable_printing_house)
#         btn_accounts_payable.pack(side="left", padx=5)
        
#         # A frame to hold the matplotlib figure
#         self.plot_frame = ttk.Frame(container)
#         self.plot_frame.pack(expand=True, fill='both')
        
#         self.canvas = None

#         return;
    
#     def plot_book_stock(self):
#         """Example: Query ΕΝΤΥΠΟ table for (τίτλος, stock), make a bar chart."""
#         try:
#             rows = self.db_manager.fetchall('SELECT "τίτλος", "stock"\
#                                              FROM "ΕΝΤΥΠΟ"')
#             titles = [r[0] for r in rows]
#             stocks = [r[1] for r in rows]
#         except Exception as e:
#             messagebox.showerror("Error", f"Could not fetch book stock:\n{e}")
#             return;
        
#         fig, ax = plt.subplots(figsize=(6,4))
#         ax.bar(titles, stocks, color='blue')
#         ax.set_xlabel('Book Title', fontsize=12)
#         ax.set_ylabel('Stock Count', fontsize=12)
#         ax.set_title('Book Stock Levels', fontsize=14)
#         plt.xticks(rotation=45, ha="right")
#         plt.tight_layout()
        
#         self.show_plot(fig)

#         return;
    
#     def plot_money_earned(self):
#         """
#         Example: sum of "χρηματικό ποσό" per year from the "ζητάει" table.
#         Adjust as needed if your schema differs.
#         """
#         try:
#             rows = self.db_manager.fetchall('''
#                 SELECT strftime('%Y', "ημ. παραγγελίας") AS Year, SUM("χρηματικό ποσό") AS Total_Earned
#                 FROM "ζητάει"
#                 GROUP BY Year
#                 ORDER BY Year
#             ''')
#             # Each row is (Year, Total_Earned)
#             years = [r[0] if r[0] else "Unknown" for r in rows]
#             sums = [r[1] if r[1] else 0 for r in rows]
            
#         except Exception as e:
#             messagebox.showerror("Error", f"Could not fetch money earned:\n{e}")
#             return;
        
#         fig, ax = plt.subplots(figsize=(6,4))
#         ax.bar(years, sums, color='green')
#         ax.set_xlabel('Year', fontsize=12)
#         ax.set_ylabel('Money Earned', fontsize=12)
#         ax.set_title('Money Earned by Year', fontsize=14)
#         plt.xticks(rotation=45, ha="right")
#         plt.tight_layout()
        
#         self.show_plot(fig)

#         return;

#     def plot_accounts_payable_printing_house(self):
#         try:
#             rows = self.db_manager.fetchall('''
#                 SELECT strftime('%Y', "ημ. παραγγελίας") AS Year, SUM("κόστος") AS Total_Earned
#                 FROM "παραγγέλνει"
#                 GROUP BY Year
#                 ORDER BY Year
#             ''')
#             # Each row is (Year, Total_Earned)
#             years = [r[0] if r[0] else "Unknown" for r in rows]
#             sums = [r[1] if r[1] else 0 for r in rows]
            
#         except Exception as e:
#             messagebox.showerror("Error", f"Could not fetch money earned:\n{e}")
#             return;
        
#         fig, ax = plt.subplots(figsize=(6,4))
#         ax.bar(years, sums, color='green')
#         ax.set_xlabel('Έτος', fontsize=12)
#         ax.set_ylabel('Συνολικό κόστος', fontsize=12)
#         ax.set_title('Κόστος τύπωσης εντύπων ανά έτος', fontsize=14)
#         plt.xticks(rotation=45, ha="right")
#         plt.tight_layout()
        
#         self.show_plot(fig)

#         return;
    
#     def show_plot(self, fig):
#         """Embed the Matplotlib figure in the plot_frame."""
#         for child in self.plot_frame.winfo_children():
#             child.destroy()
        
#         self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
#         self.canvas.draw()
#         self.canvas.get_tk_widget().pack(expand=True, fill='both')

#         return;
