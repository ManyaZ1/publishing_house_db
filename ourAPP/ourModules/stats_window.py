# ourModules/stats_window.py

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
        
        # A frame to hold the matplotlib figure
        self.plot_frame = ttk.Frame(container)
        self.plot_frame.pack(expand=True, fill='both')
        
        self.canvas = None

        return;

    def plot_chart(self, sql_query, x_lable_name, y_label_name, title_name, chart_color):
        """
        A universal chart plotting function.
        """
        try:
            rows = self.db_manager.fetchall(sql_query)
            x_list = [r[0] if r[0] else "Unknown" for r in rows]
            y_list = [r[1] if r[1] else 0 for r in rows]
        except Exception as e:
            messagebox.showerror("Data error", f"Could not fetch data:\n\n{type(e).__name__}: {e}")

            return;

        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(x_list, y_list, color=chart_color)
        ax.set_xlabel(x_lable_name, fontsize=12)
        ax.set_ylabel(y_label_name, fontsize=12)
        ax.set_title(title_name, fontsize=14)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        self.show_plot(fig)

        return;

    def show_plot(self, fig):
        """Embed the Matplotlib figure in the plot_frame."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill='both')

        # Force the window to resize slightly to trigger re-layout!
        # This is a workaround to avoid the canvas not fully showing the plot...
        (current_width, current_height) = (self.winfo_width(), self.winfo_height())
        self.geometry(f"{current_width + 1}x{current_height + 1}")
        # Add a small delay before resetting the size
        self.after(10, lambda: self.geometry(f"{current_width}x{current_height}"))

        return;
