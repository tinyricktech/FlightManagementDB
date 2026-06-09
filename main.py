import sqlite3

# Database Operations class managing all interactions with the Flight Management Database

class DBOperations:

    sql_create_pilots = """
        CREATE TABLE IF NOT EXISTS Pilots (
            PilotID INTEGER PRIMARY KEY AUTOINCREMENT,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            Rank TEXT NOT NULL,
            LicenceNumber TEXT NOT NULL UNIQUE
        )"""

    sql_create_destinations = """
        CREATE TABLE IF NOT EXISTS Destinations (
            DestinationID INTEGER PRIMARY KEY AUTOINCREMENT,
            AirportName TEXT NOT NULL,
            City TEXT NOT NULL,
            Country TEXT NOT NULL,
            IATACode TEXT NOT NULL UNIQUE
        )"""

    sql_create_flights = """
        CREATE TABLE IF NOT EXISTS Flights (
            FlightID INTEGER PRIMARY KEY AUTOINCREMENT,
            DepartureDate TEXT NOT NULL,
            DepartureTime TEXT NOT NULL,
            Status TEXT NOT NULL,
            PilotID INTEGER,
            OriginID INTEGER,
            DestinationID INTEGER,
            FOREIGN KEY (PilotID) REFERENCES Pilots(PilotID),
            FOREIGN KEY (OriginID) REFERENCES Destinations(DestinationID),
            FOREIGN KEY (DestinationID) REFERENCES Destinations(DestinationID)
        )"""

    def _init_(self):
        try:
            self.conn = sqlite3.connect("FlightManagement.db")
            self.cur = self.conn.cursor()
            self.cur.execute(self.sql_create_pilots)
            self.cur.execute(self.sql_create_destinations)
            self.cur.execute(self.sql_create_flights)
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def get_connection(self):
        self.conn = sqlite3.connect("FlightManagement.db")
        self.cur = self.conn.cursor()

    # Add a new flight
    def insert_flight(self):
        try:
            self.get_connection()
            print("\n--- Add New Flight ---")
            departure_date = input("Enter Departure Date (YYYY-MM-DD): ")
            departure_time = input("Enter Departure Time (HH:MM): ")
            status = input("Enter Status (Scheduled/Delayed/Cancelled): ")
            pilot_id = int(input("Enter Pilot ID: "))
            origin_id = int(input("Enter Origin Destination ID: "))
            destination_id = int(input("Enter Destination ID: "))
            self.cur.execute(
                "INSERT INTO Flights (DepartureDate, DepartureTime, Status, PilotID, OriginID, DestinationID) VALUES (?, ?, ?, ?, ?, ?)",
                (departure_date, departure_time, status, pilot_id, origin_id, destination_id)
            )
            self.conn.commit()
            print("Flight added successfully.")
        except Exception as e:
            self.conn.rollback()
            print("Error: " + str(e))
        finally:
            self.conn.close()

    # View flights by criteria
    def view_flights(self):
        try:
            self.get_connection()
            print("\n--- View Flights ---")
            print("1. By Destination")
            print("2. By Status")
            print("3. By Departure Date")
            choice = int(input("Enter choice: "))
            if choice == 1:
                city = input("Enter City: ")
                self.cur.execute("""
                    SELECT f.FlightID, f.DepartureDate, f.DepartureTime, f.Status,
                           p.FirstName, p.LastName, o.City, d.City
                    FROM Flights f
                    JOIN Pilots p ON f.PilotID = p.PilotID
                    JOIN Destinations o ON f.OriginID = o.DestinationID
                    JOIN Destinations d ON f.DestinationID = d.DestinationID
                    WHERE d.City = ?""", (city,))
            elif choice == 2:
                status = input("Enter Status (Scheduled/Delayed/Cancelled): ")
                self.cur.execute("""
                    SELECT f.FlightID, f.DepartureDate, f.DepartureTime, f.Status,
                           p.FirstName, p.LastName, o.City, d.City
                    FROM Flights f
                    JOIN Pilots p ON f.PilotID = p.PilotID
                    JOIN Destinations o ON f.OriginID = o.DestinationID
                    JOIN Destinations d ON f.DestinationID = d.DestinationID
                    WHERE f.Status = ?""", (status,))
            elif choice == 3:
                date = input("Enter Date (YYYY-MM-DD): ")
                self.cur.execute("""
                    SELECT f.FlightID, f.DepartureDate, f.DepartureTime, f.Status,
                           p.FirstName, p.LastName, o.City, d.City
                    FROM Flights f
                    JOIN Pilots p ON f.PilotID = p.PilotID
                    JOIN Destinations o ON f.OriginID = o.DestinationID
                    JOIN Destinations d ON f.DestinationID = d.DestinationID
                    WHERE f.DepartureDate = ?""", (date,))
            results = self.cur.fetchall()
            if results:
                print("\nFlightID | Date       | Time  | Status     | Pilot          | From       | To")
                print("-" * 85)
                for row in results:
                    print(f"{row[0]:<9} | {row[1]:<10} | {row[2]:<5} | {row[3]:<10} | {row[4]} {row[5]:<10} | {row[6]:<10} | {row[7]}")
            else:
                print("No flights found.")
        except Exception as e:
            print("Error: " + str(e))
        finally:
            self.conn.close()

    # Update flight information
    def update_flight(self):
        try:
            self.get_connection()
            print("\n--- Update Flight ---")
            flight_id = int(input("Enter Flight ID to update: "))
            print("1. Update Departure Time")
            print("2. Update Status")
            choice = int(input("Enter choice: "))
            if choice == 1:
                new_time = input("Enter new Departure Time (HH:MM): ")
                self.cur.execute("UPDATE Flights SET DepartureTime = ? WHERE FlightID = ?", (new_time, flight_id))
            elif choice == 2:
                new_status = input("Enter new Status (Scheduled/Delayed/Cancelled): ")
                self.cur.execute("UPDATE Flights SET Status = ? WHERE FlightID = ?", (new_status, flight_id))
            self.conn.commit()
            if self.cur.rowcount != 0:
                print(str(self.cur.rowcount) + " row(s) updated.")
            else:
                print("Cannot find this flight in the database.")
        except Exception as e:
            self.conn.rollback()
            print("Error: " + str(e))
        finally:
            self.conn.close()

    # Assign a pilot to a flight
    def assign_pilot(self):
        try:
            self.get_connection()
            print("\n--- Assign Pilot to Flight ---")
            flight_id = int(input("Enter Flight ID: "))
            pilot_id = int(input("Enter Pilot ID: "))
            self.cur.execute("UPDATE Flights SET PilotID = ? WHERE FlightID = ?", (pilot_id, flight_id))
            self.conn.commit()
            if self.cur.rowcount != 0:
                print("Pilot assigned successfully.")
            else:
                print("Cannot find this flight in the database.")
        except Exception as e:
            self.conn.rollback()
            print("Error: " + str(e))
        finally:
            self.conn.close()

    # View pilot schedule
    def view_pilot_schedule(self):
        try:
            self.get_connection()
            print("\n--- View Pilot Schedule ---")
            pilot_id = int(input("Enter Pilot ID: "))
            self.cur.execute("""
                SELECT f.FlightID, f.DepartureDate, f.DepartureTime, f.Status,
                       o.City, d.City, p.FirstName, p.LastName, p.Rank
                FROM Flights f
                JOIN Pilots p ON f.PilotID = p.PilotID
                JOIN Destinations o ON f.OriginID = o.DestinationID
                JOIN Destinations d ON f.DestinationID = d.DestinationID
                WHERE f.PilotID = ?
                ORDER BY f.DepartureDate""", (pilot_id,))
            results = self.cur.fetchall()
            if results:
                print(f"\nSchedule for Pilot: {results[0][6]} {results[0][7]} ({results[0][8]})")
                print("-" * 70)
                print("FlightID | Date       | Time  | Status     | From       | To")
                print("-" * 70)
                for row in results:
                    print(f"{row[0]:<9} | {row[1]:<10} | {row[2]:<5} | {row[3]:<10} | {row[4]:<10} | {row[5]}")
            else:
                print("No flights found for this pilot.")
        except Exception as e:
            print("Error: " + str(e))
        finally:
            self.conn.close()

    # View and update destination information
    def manage_destinations(self):
        try:
            self.get_connection()
            print("\n--- Destination Management ---")
            print("1. View all destinations")
            print("2. Update destination")
            choice = int(input("Enter choice: "))
            if choice == 1:
                self.cur.execute("SELECT * FROM Destinations")
                results = self.cur.fetchall()
                print("\nID | Airport Name         | City         | Country      | IATA")
                print("-" * 65)
                for row in results:
                    print(f"{row[0]:<3} | {row[1]:<20} | {row[2]:<12} | {row[3]:<12} | {row[4]}")
            elif choice == 2:
                dest_id = int(input("Enter Destination ID to update: "))
                new_airport = input("Enter new Airport Name: ")
                self.cur.execute("UPDATE Destinations SET AirportName = ? WHERE DestinationID = ?", (new_airport, dest_id))
                self.conn.commit()
                if self.cur.rowcount != 0:
                    print("Destination updated successfully.")
                else:
                    print("Cannot find this destination in the database.")
        except Exception as e:
            self.conn.rollback()
            print("Error: " + str(e))
        finally:
            self.conn.close()

    # Delete a flight
    def delete_flight(self):
        try:
            self.get_connection()
            print("\n--- Delete Flight ---")
            flight_id = int(input("Enter Flight ID to delete: "))
            self.cur.execute("DELETE FROM Flights WHERE FlightID = ?", (flight_id,))
            self.conn.commit()
            if self.cur.rowcount != 0:
                print(str(self.cur.rowcount) + " row(s) deleted.")
            else:
                print("Cannot find this flight in the database.")
        except Exception as e:
            self.conn.rollback()
            print("Error: " + str(e))
        finally:
            self.conn.close()

    # Summary queries
    def view_summaries(self):
        try:
            self.get_connection()
            print("\n--- Summary Reports ---")
            print("1. Number of flights per destination")
            print("2. Number of flights per pilot")
            choice = int(input("Enter choice: "))
            if choice == 1:
                self.cur.execute("""
                    SELECT d.City, d.Country, COUNT(f.FlightID) AS TotalFlights
                    FROM Destinations d
                    LEFT JOIN Flights f ON d.DestinationID = f.DestinationID
                    GROUP BY d.DestinationID
                    ORDER BY TotalFlights DESC""")
                results = self.cur.fetchall()
                print("\nCity         | Country      | Total Flights")
                print("-" * 45)
                for row in results:
                    print(f"{row[0]:<13} | {row[1]:<12} | {row[2]}")
            elif choice == 2:
                self.cur.execute("""
                    SELECT p.FirstName, p.LastName, p.Rank, COUNT(f.FlightID) AS TotalFlights
                    FROM Pilots p
                    LEFT JOIN Flights f ON p.PilotID = f.PilotID
                    GROUP BY p.PilotID
                    ORDER BY TotalFlights DESC""")
                results = self.cur.fetchall()
                print("\nPilot Name         | Rank       | Total Flights")
                print("-" * 50)
                for row in results:
                    print(f"{row[0]} {row[1]:<15} | {row[2]:<10} | {row[3]}")
        except Exception as e:
            print("Error: " + str(e))
        finally:
            self.conn.close()

    # Populate sample data
    def populate_sample_data(self):
        try:
            self.get_connection()

            pilots = [
                ("James", "Carter", "Captain", "LIC001"),
                ("Sarah", "Mitchell", "First Officer", "LIC002"),
                ("David", "Thompson", "Captain", "LIC003"),
                ("Emma", "Watson", "First Officer", "LIC004"),
                ("Michael", "Brown", "Captain", "LIC005"),
                ("Laura", "Jones", "First Officer", "LIC006"),
                ("Robert", "Davis", "Captain", "LIC007"),
                ("Sophie", "Wilson", "First Officer", "LIC008"),
                ("William", "Moore", "Captain", "LIC009"),
                ("Charlotte", "Taylor", "First Officer", "LIC010")
            ]

            destinations = [
                ("Heathrow Airport", "London", "United Kingdom", "LHR"),
                ("Charles de Gaulle", "Paris", "France", "CDG"),
                ("JFK International", "New York", "USA", "JFK"),
                ("Dubai International", "Dubai", "UAE", "DXB"),
                ("Frankfurt Airport", "Frankfurt", "Germany", "FRA"),
                ("Amsterdam Schiphol", "Amsterdam", "Netherlands", "AMS"),
                ("Tokyo Haneda", "Tokyo", "Japan", "HND"),
                ("Sydney Airport", "Sydney", "Australia", "SYD"),
                ("Toronto Pearson", "Toronto", "Canada", "YYZ"),
                ("Madrid Barajas", "Madrid", "Spain", "MAD"),
                ("Rome Fiumicino", "Rome", "Italy", "FCO"),
                ("Singapore Changi", "Singapore", "Singapore", "SIN")
            ]

            flights = [
                ("2025-06-01", "08:00", "Scheduled", 1, 1, 2),
                ("2025-06-01", "10:30", "Scheduled", 2, 1, 3),
                ("2025-06-02", "14:00", "Delayed", 3, 2, 4),
                ("2025-06-02", "16:45", "Scheduled", 4, 3, 5),
                ("2025-06-03", "09:15", "Scheduled", 5, 4, 6),
                ("2025-06-03", "11:00", "Cancelled", 6, 5, 7),
                ("2025-06-04", "13:30", "Scheduled", 7, 6, 8),
                ("2025-06-04", "15:00", "Scheduled", 8, 7, 9),
                ("2025-06-05", "07:45", "Delayed", 9, 8, 10),
                ("2025-06-05", "19:00", "Scheduled", 10, 9, 11),
                ("2025-06-06", "06:30", "Scheduled", 1, 10, 12),
                ("2025-06-06", "12:00", "Scheduled", 2, 11, 1),
                ("2025-06-07", "17:30", "Scheduled", 3, 12, 2),
                ("2025-06-07", "20:00", "Delayed", 4, 1, 4),
                ("2025-06-08", "08:30", "Scheduled", 5, 2, 6)
            ]

            self.cur.executemany("INSERT OR IGNORE INTO Pilots (FirstName, LastName, Rank, LicenceNumber) VALUES (?, ?, ?, ?)", pilots)
            self.cur.executemany("INSERT OR IGNORE INTO Destinations (AirportName, City, Country, IATACode) VALUES (?, ?, ?, ?)", destinations)
            self.cur.executemany("INSERT OR IGNORE INTO Flights (DepartureDate, DepartureTime, Status, PilotID, OriginID, DestinationID) VALUES (?, ?, ?, ?, ?, ?)", flights)
            self.conn.commit()
            print("Sample data loaded successfully.")
        except Exception as e:
            self.conn.rollback()
            print("Error: " + str(e))
        finally:
            self.conn.close()


# Main menu loop

db_ops = DBOperations()

while True:
    print("\n Flight Management System")
    print("**************************")
    print(" 1. Add a New Flight")
    print(" 2. View Flights by Criteria")
    print(" 3. Update Flight Information")
    print(" 4. Assign Pilot to Flight")
    print(" 5. View Pilot Schedule")
    print(" 6. View/Update Destination Information")
    print(" 7. Delete a Flight")
    print(" 8. View Summary Reports")
    print(" 9. Load Sample Data")
    print(" 10. Exit\n")

    try:
        _choose_menu = int(input("Enter your choice: "))
        if _choose_menu == 1:
            db_ops.insert_flight()
        elif _choose_menu == 2:
            db_ops.view_flights()
        elif _choose_menu == 3:
            db_ops.update_flight()
        elif _choose_menu == 4:
            db_ops.assign_pilot()
        elif _choose_menu == 5:
            db_ops.view_pilot_schedule()
        elif _choose_menu == 6:
            db_ops.manage_destinations()
        elif _choose_menu == 7:
            db_ops.delete_flight()
        elif _choose_menu == 8:
            db_ops.view_summaries()
        elif _choose_menu == 9:
            db_ops.populate_sample_data()
        elif _choose_menu == 10:
            print("Goodbye.")
            exit(0)
        else:
            print("Invalid choice. Please try again.")
    except ValueError:
        print("Please enter a valid number.")
