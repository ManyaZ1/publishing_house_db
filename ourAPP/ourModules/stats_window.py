# ourModules/stats_window.py

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from ourModules.translations import SPECIALIZATION_REVERSE_MAP

class StatsWindow(tk.Toplevel):
    """
    A separate Toplevel window for statistics & charts.
    """
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        
        self.title("Database Statistics")
        self.initialize_window()
        self.db_manager = db_manager
        
        # Main container
        container = ttk.Frame(self, padding=10)
        container.pack(expand=True, fill='both')
        
        lbl_title = ttk.Label(container, text="- Statistics & Charts -", font=('Arial', 14, 'bold'))
        lbl_title.pack(pady=5)
        
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=5)
        
        # Show Book Stock
        btn_show_stock = ttk.Button(
            btn_frame, text="Books Stock",
            command=lambda:self.plot_chart(
                '''
                SELECT "title", "stock"
                FROM "PUBLICATION"
                ORDER BY "stock" DESC
                ''',
                'Book Title', 'Stock Count', 'Book Stock Levels', 'blue'
            )
        )
        btn_show_stock.pack(side="left", padx=5)

        # Show Money Earned
        btn_money_earned = ttk.Button(
            btn_frame, text="Money Earned",
            command=lambda:self.plot_chart(
                '''
                SELECT strftime('%Y', "order date") AS Year, SUM("payment") AS Total_Earned
                FROM "client_orders"
                GROUP BY Year
                ORDER BY Year
                ''',
                'Year', 'Money Earned', 'Money Earned by Year', 'purple'
            )
        )
        btn_money_earned.pack(side="left", padx=5)

        # Show Accounts Payable to Printing House
        btn_accounts_payable = ttk.Button(
            btn_frame, text="Accounts Payable to Printing House",
            command=lambda:self.plot_chart(
                '''
                SELECT strftime('%Y', "order date") AS Year, SUM("cost") AS Total_Payable
                FROM "order_printing_house"
                GROUP BY Year
                ORDER BY Year
                ''',
                'Year', 'Total Payable', 'Printing Costs by Year', 'green'
            )
        )
        btn_accounts_payable.pack(side="left", padx=5)

        # Show Each Book's Quantity Sales
        btn_book_sales = ttk.Button(
            btn_frame, text="Book Sales",
            command=lambda:self.plot_chart(
                '''
                SELECT PUBLICATION."title", SUM("client_orders"."quantity") AS Total_Sales
                FROM "client_orders" JOIN "PUBLICATION" ON "client_orders"."Publication-isbn"="PUBLICATION"."isbn"
                GROUP BY "PUBLICATION"."title"
                ORDER BY Total_Sales DESC
                ''',
                'Book Title', 'Total Sales', 'Book Sales by (Client) Quantity Orders', 'orange'
            )
        )
        btn_book_sales.pack(side="left", padx=5)

        # Show Each Author's Sales
        btn_author_sales = ttk.Button(
            btn_frame, text="Author Sales",
            command=lambda:self.plot_chart(
                f'''
                SELECT "PARTNER"."name", SUM("client_orders"."quantity") AS Total_Sales
                FROM ("PARTNER" JOIN "contributes" ON "contributes"."Partner_TaxId" = "PARTNER"."Tax_Id")
                                 JOIN "client_orders" ON "client_orders"."Publication-isbn" = "contributes"."Publication-isbn"
                WHERE "PARTNER"."specialisation" = {SPECIALIZATION_REVERSE_MAP["Writer"]}
                GROUP BY "PARTNER"."Tax_Id"
                ORDER BY Total_Sales DESC;
                ''',
                'Author Name', 'Total Sales', 'Author Sales by (Client) Quantity Orders', 'red'
            )
        )
        btn_author_sales.pack(side="left", padx=5)
        
        # A frame to hold the matplotlib figure
        self.plot_frame = ttk.Frame(container)
        self.plot_frame.pack(expand=True, fill='both')
        
        self.canvas = None

        return;

    def initialize_window(self):
        (window_width, window_height) = (1200, 700)
        (screen_width, screen_height) = (self.winfo_screenwidth(), self.winfo_screenheight())
        (x, y) = ((screen_width // 2) - (window_width // 2), (screen_height // 2) - (window_height // 2))
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        return;

    def plot_chart(self, sql_query, x_label_name, y_label_name, title_name, chart_color):
        """
        A universal chart plotting function.
        """
        try:
            rows = self.db_manager.fetchall(sql_query)
        except Exception as e:
            messagebox.showerror("Data error", f"Could not fetch data:\n\n{type(e).__name__}: {e}")

            return;
    
        x_list = [r[0] if r[0] else "Unknown" for r in rows]
        y_list = [r[1] if r[1] else 0 for r in rows]
    
        # ----------------- Print the data in a table -----------------
        max_x_len = max(len(x_label_name), *(len(str(x)) for x in x_list)) if x_list else len(x_label_name)
        max_y_len = max(len(y_label_name), *(len(str(y)) for y in y_list)) if y_list else len(y_label_name)
        def make_separator(char="-", corner="+", fill_char="-"):
            return ( # Helper to create a horizontal line separator
                corner 
                + char*(max_x_len + 2) 
                + corner 
                + char*(max_y_len + 2) 
                + corner
            );
        # Print title block
        print("\n" + "=" * (max_x_len + max_y_len + 7))
        print(f"  {title_name}")
        print("=" * (max_x_len + max_y_len + 7))
        
        header_separator = make_separator() # Print header row
        print(header_separator)
        print(f"| {x_label_name.ljust(max_x_len)} | {y_label_name.ljust(max_y_len)} |")
        print(header_separator)
        for x_val, y_val in zip(x_list, y_list):
            print(f"| {str(x_val).ljust(max_x_len)} | {str(y_val).rjust(max_y_len)} |") # Print data rows
        print(header_separator) # Print bottom border

        # ----------------- Plot the data in a bar chart -----------------
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(x_list, y_list, color=chart_color)
        ax.set_xlabel(x_label_name, fontsize=12)
        ax.set_ylabel(y_label_name, fontsize=12)
        ax.set_title(title_name, fontsize=14)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        self.show_plot(fig)

        return;

    def show_plot(self, fig):
        """Embed the Matplotlib figure in the plot_frame."""
        for child in self.plot_frame.winfo_children():
            child.destroy()
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill='both')

        return;
