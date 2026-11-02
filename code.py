import csv
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
 
# Database setup file name
DB_NAME = "ngc_kiosk.db"
 
 
def init_db():
  """Initializes the SQLite database and adds mock data if empty."""
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_ref TEXT UNIQUE,
            surname TEXT,
            email TEXT,
            talk_title TEXT,
            checked_in INTEGER DEFAULT 0
        )
    """)
  # Insert sample data for testing
  cursor.execute("SELECT COUNT(*) FROM attendees")
  if cursor.fetchone()[0] == 0:
    sample_data = [
        ("NGC101", "Smith", "smith@email.com", "Intro to Game Dev"),
        ("NGC102", "Johnson", "johnson@email.com", "Advanced Python for Mods"),
        ("NGC103", "hason", "ohason@email.com", "Indie RPG Design"),
        ("NGC104", "Turnbull", "turnbull@email.com", "some 4th thing i aint think this through")
    ]
    cursor.executemany(
        """
            INSERT INTO attendees (booking_ref, surname, email, talk_title)
            VALUES (?, ?, ?, ?)
        """,
        sample_data,
    )
  conn.commit()
  conn.close()
 
 
class NGCKioskApp:
 
  def __init__(self, root):
    self.root = root
    self.root.title("NGC Convention Check-In Kiosk")
 
    # FR1: Run in fullscreen kiosk mode
    self.root.attributes("-fullscreen", True)
    self.root.configure(bg="#f0f2f5")
 
    init_db()
    self.create_main_screen()
 
  def create_main_screen(self):
    """Displays the main welcome and search screen."""
    for widget in self.root.winfo_children():
      widget.destroy()
 
    # Header
    header_frame = tk.Frame(self.root, bg="#1a1a2e", height=120)
    header_frame.pack(fill=tk.X, side=tk.TOP)
 
    tk.Label(
        header_frame,
        text="Newcastle Games Convention (NGC)\nConvention Check-In Kiosk",
        font=("Arial", 22, "bold"),
        bg="#1a1a2e",
        fg="white",
    ).pack(pady=25)
 
    # Body / Search Container
    body_frame = tk.Frame(self.root, bg="#f0f2f5")
    body_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
 
    tk.Label(
        body_frame,
        text="Please enter your Booking Reference, Surname, or Email:",
        font=("Arial", 16),
        bg="#f0f2f5",
    ).pack(pady=15)
 
    self.search_var = tk.StringVar()
    self.search_entry = tk.Entry(
        body_frame, textvariable=self.search_var, font=("Arial", 20), width=30
    )
    self.search_entry.pack(pady=15)
    self.search_entry.focus()
    self.search_entry.bind("<Return>", lambda event: self.search_booking())
 
    search_btn = tk.Button(
        body_frame,
        text="Search Booking",
        font=("Arial", 16, "bold"),
        bg="#4e54c8",
        fg="white",
        padx=20,
        pady=10,
        command=self.search_booking,
    )
    search_btn.pack(pady=20)
 
    # Footer (Staff Dashboard & Exit)
    footer_frame = tk.Frame(self.root, bg="#f0f2f5")
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=30, pady=30)
 
    tk.Button(
        footer_frame,
        text="Staff Dashboard",
        font=("Arial", 12),
        command=self.open_staff_login,
    ).pack(side=tk.LEFT)
    tk.Button(
        footer_frame,
        text="Exit Kiosk",
        font=("Arial", 12),
        bg="#ff4d4d",
        fg="white",
        command=self.root.quit,
    ).pack(side=tk.RIGHT)
 
  def search_booking(self):
    """FR2: Search by booking reference, surname or email."""
    query = self.search_var.get().strip()
    if not query:
      messagebox.showerror("Error", "Please enter a search query.")
      return
 
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, booking_ref, surname, email, talk_title, checked_in
        FROM attendees
        WHERE booking_ref LIKE ? OR surname LIKE ? OR email LIKE ?
    """,
        (f"%{query}%", f"%{query}%", f"%{query}%"),
    )
    results = cursor.fetchall()
    conn.close()
 
    if not results:
      messagebox.showinfo(
          "Not Found", "No booking records found matching your search."
      )
    else:
      self.show_results_screen(results)
 
  def show_results_screen(self, results):
    """FR3: Display booked talks and attendee details."""
    for widget in self.root.winfo_children():
      widget.destroy()
 
    header_frame = tk.Frame(self.root, bg="#1a1a2e", height=100)
    header_frame.pack(fill=tk.X, side=tk.TOP)
 
    tk.Label(
        header_frame,
        text="Matching Bookings - Select to Check In",
        font=("Arial", 20, "bold"),
        bg="#1a1a2e",
        fg="white",
    ).pack(pady=25)
 
    body_frame = tk.Frame(self.root, bg="#f0f2f5")
    body_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
 
    for row in results:
      attendee_id, bref, surname, email, talk, checked_in = row
      status_text = (
          "Already Checked In" if checked_in == 1 else "Not Checked In"
      )
      status_color = "green" if checked_in == 1 else "orange"
 
      card = tk.Frame(body_frame, bg="white", bd=2, relief=tk.GROOVE)
      card.pack(fill=tk.X, pady=10, ipadx=10, ipady=10)
 
      info_text = f"Attendee: {surname} ({email}) | Ref: {bref}\nBooked Talk: {talk}"
      tk.Label(
          card,
          text=info_text,
          font=("Arial", 14),
          bg="white",
          justify=tk.LEFT,
      ).pack(side=tk.LEFT, padx=15)
 
      tk.Label(
          card,
          text=status_text,
          font=("Arial", 12, "bold"),
          fg=status_color,
          bg="white",
      ).pack(side=tk.RIGHT, padx=15)
 
      if checked_in == 0:
        tk.Button(
            card,
            text="Check In Now",
            font=("Arial", 12, "bold"),
            bg="#28a745",
            fg="white",
            command=lambda aid=attendee_id: self.perform_checkin(aid),
        ).pack(side=tk.RIGHT, padx=15)
 
    tk.Button(
        self.root,
        text="← Back to Search",
        font=("Arial", 14),
        command=self.create_main_screen,
    ).pack(side=tk.BOTTOM, pady=25)
 
  def perform_checkin(self, attendee_id):
    """FR4 & FR5: Record check-in and prevent duplicate check-ins."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT checked_in, surname, talk_title FROM attendees WHERE id = ?",
        (attendee_id,),
    )
    row = cursor.fetchone()
 
    if row[0] == 1:
      messagebox.showwarning(
          "Already Checked In", "This ticket has already been used!"
      )
    else:
      cursor.execute(
          "UPDATE attendees SET checked_in = 1 WHERE id = ?", (attendee_id,)
      )
      conn.commit()
      messagebox.showinfo(
          "Success",
          f"Check-in successful for {row[1]}!\nEnjoy: '{row[2]}'.",
      )
    conn.close()
    self.create_main_screen()
 
  def open_staff_login(self):
    """Staff PIN prompt for dashboard access (FR6)."""
    login_win = tk.Toplevel(self.root)
    login_win.title("Staff Login")
    login_win.geometry("320x180")
 
    tk.Label(
        login_win, text="Enter Staff Password:", font=("Arial", 12, "bold")
    ).pack(pady=15)
    pwd_entry = tk.Entry(login_win, show="*", font=("Arial", 14))
    pwd_entry.pack(pady=5)
    pwd_entry.focus()
 
    def verify():
      if pwd_entry.get() == "adminpasswordidfk":  # Default staff password
        login_win.destroy()
        self.open_staff_dashboard()
      else:
        messagebox.showerror("Error", "Incorrect Password")
 
    tk.Button(
        login_win,
        text="Login",
        bg="#4e54c8",
        fg="white",
        font=("Arial", 10, "bold"),
        command=verify,
    ).pack(pady=15)
 
  def open_staff_dashboard(self):
    """FR6: Staff reporting dashboard."""
    dash_win = tk.Toplevel(self.root)
    dash_win.title("Staff Reporting Dashboard")
    dash_win.geometry("800x500")
 
    tk.Label(
        dash_win,
        text="Convention Attendance Reporting Dashboard",
        font=("Arial", 16, "bold"),
    ).pack(pady=15)
 
    columns = ("Reference", "Surname", "Email", "Talk Title", "Status")
    tree = ttk.Treeview(dash_win, columns=columns, show="headings")
    for col in columns:
      tree.heading(col, text=col)
      tree.column(col, width=140)
 
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT booking_ref, surname, email, talk_title, checked_in FROM attendees"
    )
    for row in cursor.fetchall():
      status = "Checked In" if row[4] == 1 else "Not Checked In"
      tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], status))
    conn.close()
 
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
 
    # FR7: Export attendance to CSV button
    tk.Button(
        dash_win,
        text="Export Attendance to CSV (FR7)",
        font=("Arial", 12, "bold"),
        bg="#007bff",
        fg="white",
        command=self.export_csv,
    ).pack(pady=15)
 
  def export_csv(self):
    """FR7: Export attendance data to CSV."""
    try:
      conn = sqlite3.connect(DB_NAME)
      cursor = conn.cursor()
      cursor.execute(
          "SELECT booking_ref, surname, email, talk_title, checked_in FROM attendees"
      )
      rows = cursor.fetchall()
      conn.close()
 
      filename = "ngc_attendance_report.csv"
      with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Booking Reference", "Surname", "Email", "Talk Title", "Checked In"]
        )
        for row in rows:
          status = "Yes" if row[4] == 1 else "No"
          writer.writerow([row[0], row[1], row[2], row[3], status])
 
      messagebox.showinfo(
          "Export Successful", f"Attendance report saved successfully to {filename}"
      )
    except Exception as e:
      messagebox.showerror("Export Failed", str(e))
 
 
if __name__ == "__main__":
  root = tk.Tk()
  app = NGCKioskApp(root)
  root.mainloop()
