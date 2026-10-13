import sys
import sqlite3

from datetime import datetime
from pathlib import Path

from database_setup import build_database

import queries

db_name = "flight_management.db"
DATETIME_FORMAT = "%Y-%m-%d %H:%M" 
DATE_FORMAT = "%Y-%m-%d"
flight_status = ("Boarding","Arrived", "Delayed", "Cancelled")
pilot_rank = ("Captain", "Vice Captain")

# =====================================================================
# Display helpers
# =====================================================================

def print_table(cursor,results, empty_message="No records found."):
    """Print a lists of results into a pretty table.
    Usually using other light-weight module like tabulate to print
    but considering the main.py might be run in other environment it is not used."""
    if not results:
      print(f"\n  {empty_message}\n")
      return

    headers = [column[0] for column in cursor.description]
    values = [["-" if value is None else str(value) for value in row] for row in results]
    widths = [max(len(h), *(len(r[i]) for r in values)) for i, h in enumerate(headers)]
    line = "  +" + "+".join("-" * (w + 2) for w in widths) + "+"
    print("\n" + line)
    print("  | " + " | ".join(h.upper().ljust(w) for h, w in zip(headers, widths)) + " |")
    print(line)
    for r in values:
        print("  | " + " | ".join(v.ljust(w) for v, w in zip(r, widths)) + " |")
    print(line)
    print("  " + str(len(results)) + " row(s)")


# ========================
# Input Helper 
# =========================

def ask(prompt, default=None):
  """Ask for a value. Default value is shown in [brackets], pressing Enter keeps it."""
  if default is not None:
    value = input(prompt + " [" + str(default) + "]:").strip()
    return value if value else default
  return input(prompt + ": ").strip()

class CancelInput(Exception):
  """Raised when the user presses Enter on a required field to cancel."""

ESC = "\x1b"

def ask_until_valid(prompt, check, default=None, required=True):
  """
  Keep asking until check(value) accepts the value, and return what check returns.
  Allowing user to exit by pressing ESC
  """
  result = None
  while result is None:     
    value = ask(prompt + "(Exit anytime by pressing ESC then Enter)", default)
    if value == ESC:
      raise CancelInput()
    elif value == "" and not required:
      result = "" 
    elif value == "":
      print("  This field is required. Please try again (or press Esc then Enter to cancel).")
    else:
      try:
        result = check(value)
      except ValueError as e:
        print("  " + str(e) + " Please try again.")
  return result

# ===================================================
# Validation helpers for time and date
# Checking on Python side as a redundant layer of validation
# ===================================================
def check_datetime(value):
    """Return value if it matches time format, otherwise raise TypeError or ValueError."""
    if not isinstance(value, str):
        raise TypeError(f"Flight time should be a string, in the format of {DATETIME_FORMAT}")
    try:
        datetime.strptime(value, DATETIME_FORMAT)
    except ValueError:
        raise ValueError(f"'{value}' is not a valid date/time. Use YYYY-MM-DD HH:MM.")
    return value

def check_date(value):
    """Return value if it matches date format, otherwise raise TypeError or ValueError."""
    if not isinstance(value, str):
        raise TypeError(f"Flight time should be a string, in the format of {DATETIME_FORMAT}")
    try:
        datetime.strptime(value, DATE_FORMAT)
    except ValueError:
      raise ValueError(f"'{value}' is not a valid date/time. Use YYYY-MM-DD HH:MM.")
    return value

def check_flight_number(cur, value):
  """A flight number mut not be in use yet and < 8 characters."""
  value = value.strip().upper()
  
  if not value.isalnum() or len(value) > 8:
    raise ValueError("'" + value + "' is not a valid flight number (up to 8 letters and digits).")
  cur.execute(queries.sql_flight_number_exists, (value,))
  if cur.fetchone():
    raise ValueError("Flight number " + value + " already exists.")
  return value
 
def check_arrival_time(departure_time, value):
  """The arrival time must be a valid date/time after the departure time."""
  check_datetime(value)
  if value <= departure_time:
    raise ValueError("Arrival time must be after the departure time (" + departure_time + ").")
  return value

def check_gate(value):
  """Check to ensure gates did not go above 5 characters."""
  if len(value) > 5:
    raise ValueError("A gate can be at most 5 characters.")
  return value.upper()


###########################################
## These checker needs querying the db   ##
##########################################
def find_airport(cur, code):
  """Return (airport_id, code, status, max_flight_size), checking the airport exists and is active."""
  cur.execute(queries.sql_find_airport, (code.upper(),))
  airport = cur.fetchone()
  if airport is None:
    raise ValueError("Unknown airport code '" + code + "'.")
  if not airport[2]:
    raise ValueError("Airport " + code.upper() + " is currently inactive.")
  return airport
 
def check_arrival_airport(cur, code, from_airport):
  """Check if arrival ariport is different from departure airport"""
  to_airport = find_airport(cur, code)
  if to_airport[0] == from_airport[0]:
    raise ValueError("The arrival airport must be different from the departure airport.")
  return to_airport

def check_departure_time(cur, flight_number, value):
  """Check if departure time is correct input and later than arrival time"""
  check_datetime(value)
  cur.execute(queries.sql_flight_exists, (flight_number, value))
  if cur.fetchone():
    raise ValueError(flight_number + " already departs at " + value + ".")
  return value

def check_aircraft(cur, aircraft_id):
  """Check if aircraft_id is a number, exist and active. Returns the id as an int."""
  if not str(aircraft_id).isdigit():
    raise ValueError("The aircraft ID must be a number.")
  cur.execute(queries.sql_find_aircraft, (aircraft_id,))
  aircraft = cur.fetchone()
  if aircraft is None:
    raise ValueError("There is no aircraft with this id.")
  if aircraft[2] != "Active":
    raise ValueError("Aircraft " + str(aircraft_id) + " (" + aircraft[1] + ") is in status '" +
                     aircraft[2] + "'.")
  return int(aircraft_id)

def check_status_number(value):
  """The status is chosen by its number in flight_status (1 to 6). Returns the status name."""
  if not str(value).isdigit() or not 1 <= int(value) <= len(flight_status):
    raise ValueError("Choose a status number from 1 to " + str(len(flight_status)) + ".")
  return flight_status[int(value) - 1]

# # Define DBOperation class to manage all data into the database.
# # Give a name of your choice to the database


class DBOperations:
#   sql_create_table_firsttime = "create table if not exists "

#   sql_create_table = "create table TableName"

#   sql_insert = ""
#   sql_select_all = "select * from TableName"
#   sql_search = "select * from TableName where FlightID = ?"
#   sql_alter_data = ""
#   sql_update_data = ""
#   sql_delete_data = ""
#   sql_drop_table = ""

    def __init__(self, db_name=db_name):
        self.db_name = db_name
        try:
            # First run: build the database from schema.sql and sample_data.sql
            if not Path(self.db_name).exists():
                build_database(self.db_name)
        except Exception as e:
            print(e)

    def get_connection(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()

    # -------------------------------------------------------------------
    # Menu option 1: create/ reset tables and load sample data
    # -------------------------------------------------------------------
    def create_table(self):
        try:
            build_database(self.db_name)
        except Exception as e:
            print(e)

    # -------------------------------------------------------------------
    # Menu option 2: add a new flight
    # -------------------------------------------------------------------

    def add_flight(self, flight):
          """
          Inseart a new flight and retrun the flight number
          Flight details are checked to as a redundant gate ensure data 
          are valid before going into the database.
          """
          try:
            self.cur.execute(queries.sql_insert, (flight.get_flight_number(), flight.get_from_airport(),
                                                flight.get_to_airport(), flight.get_aircraft(),
                                                flight.get_departure_time(), flight.get_arrival_time(),
                                                flight.get_departure_gate() or None,
                                                flight.get_arrival_gate() or None))
            self.conn.commit()
          except sqlite3.IntegrityError as e:
            raise ValueError("The flight could not be saved (" + str(e) + ").")
          return self.cur.lastrowid
    
    def insert_data(self):
      try:
        self.get_connection()
  
        flight = FlightInfo()
        print("\n  Please put times are UTC in the format YYYY-MM-DD HH:MM.")
        print("  Press Esc then Enter at any question to cancel.\n")
  
        flight.set_flight_number(ask_until_valid("Enter flight number (e.g.FM201)",
                                                lambda value: check_flight_number(self.cur, value)))
        
        from_airport = ask_until_valid("Enter deprature airport code (e.g.LHR)",
                                      lambda code: find_airport(self.cur, code), "LHR")
        flight.set_from_airport(from_airport[1])
 
        to_airport = ask_until_valid("Enter arrival airport code",
                                    lambda code: check_arrival_airport(self.cur, code, from_airport))
        flight.set_to_airport(to_airport[1])
        
        flight.set_departure_time(ask_until_valid(
          "Enter departure time in the format YYYY-MM-DD HH:MM \n",
          lambda value: check_datetime(value)))
        
        flight.set_arrival_time(ask_until_valid(
          "Enter arrival time in the format YYYY-MM-DD HH:MM \n",
          lambda value: check_arrival_time(flight.get_departure_time(), value)))
        
        if input("Show all the planes first? (y/n): ").strip().lower() == "y":
          self.cur.execute(queries.sql_select_planes)
          print_table(self.cur, self.cur.fetchall())
        flight.set_aircraft(ask_until_valid(
          "Enter aircraft ID",
          lambda aircraft_id: check_aircraft(self.cur, aircraft_id)))
        
        flight.set_departure_gate(ask_until_valid("Enter departure gate (Enter to skip) ",check_gate, required=False))
        
        flight.set_arrival_gate(ask_until_valid("Enter arrival gate (Enter to skip)",check_gate, required=False))
  
        new_id = self.add_flight(flight)
        print("\nInserted data successfully (flight id " + str(new_id) + ")")
        self.cur.execute(queries.sql_search, (new_id,))
        print_table(self.cur, self.cur.fetchall())
      except CancelInput:
        print("\nCancelled - no flight was added.")
      except Exception as e:
        print("Error: " + str(e))
      finally:
        self.conn.close()
      
        
    # -------------------------------------------------------------------
    # Menu option 3: view all flights
    # -------------------------------------------------------------------
    def select_all(self):
        try:
            self.get_connection()
            self.cur.execute(queries.sql_select_all)
            result = self.cur.fetchall()
            print_table(self.cur, result)
            
        except Exception as e:
            print("Error: " + str(e))
            
        finally:
            self.conn.close()


    # -------------------------------------------------------------------
    # Menu option 4: view flights by criteria
    # -------------------------------------------------------------------
    def search_by_criteria(self):
      try:
        self.get_connection()
        print("\n  Fill in any filters you need, press Enter to skip")
        destination = input("Destination airport code:").strip()
        print("  Status: " + ", ".join(str(i + 1) + "=" + s for i, s in enumerate(flight_status)))
        status_choice = int(input("Status number: "))
        status = flight_status[status_choice - 1] if status_choice else ""
        date_from = input("Departing on or after (YYYY-MM-DD):").strip()
        date_to = input("Departing on or before (YYYY-MM-DD):").strip()
        flight_number = input("Flight number: ").strip()
  
        result = self.find_flights(destination, status, date_from, date_to, flight_number)
        print_table(self.cur, result, "No flights match those criteria.")
      except Exception as e:
        print("Error: " + str(e))
      finally:
        self.conn.close()
  
    def find_flights(self, destination="", status="", date_from="", date_to="", flight_number=""):
      # add conditions , then for each conditions add params
      conditions = []
      params = []
      if destination:      # airport code or city, e.g. 'JFK' or 'new york'
        conditions.append("(t.airport_code = ?")
        params += [destination.upper()]
      if status:
        conditions.append("f.flight_status = ?")
        params.append(status)
      if date_from:        # date() strips the time so whole days are compared
        conditions.append("date(f.departure_time) >= ?")
        params.append(check_date(date_from))
      if date_to:
        conditions.append("date(f.departure_time) <= ?")
        params.append(check_date(date_to))
      if flight_number:
        conditions.append("f.flight_number = ?")
        params.append(flight_number.upper())
  
      sql = queries.sql_select_flights
      if conditions:
        sql += " WHERE " + " AND ".join(conditions)
      sql += " ORDER BY f.departure_time"
      self.cur.execute(sql, params)
      return self.cur.fetchall()
    
  # -------------------------------------------------------------------
  # Menu option 5: update flight information
  # -------------------------------------------------------------------
    def choose_flight(self):
      """ return the list of fligth allowing user to pick"""
      self.cur.execute(queries.sql_select_all)
      matches = self.cur.fetchall()
      print_table(self.cur, matches)
      flight_id = int(input("Enter the FlightID to update: "))
      if flight_id not in [row[0] for row in matches]:
        raise ValueError("Flight " + str(flight_id) + " is not one of the flights listed.")
      return flight_id
  
    def get_flight(self, flight_id):
      """Load one flight into a FlightInfo object (None if it does not exist)."""
      self.cur.execute(queries.sql_get_flight, (flight_id,))
      row = self.cur.fetchone()
      if row is None:
        return None
      flight = FlightInfo()
      flight.set_flight_id(row[0])
      flight.set_flight_number(row[1])
      flight.set_from_airport(row[2])
      flight.set_to_airport(row[3])
      flight.set_aircraft(row[4])
      flight.set_departure_time(row[5])
      flight.set_arrival_time(row[6])
      flight.set_status(row[7])
      flight.set_departure_gate(row[8])
      flight.set_arrival_gate(row[9])
      return flight
  
    def update_flight(self, flight):
      """
      Update the flight data
      """
      gates = [None if gate in ("", "-", None) else gate
              for gate in (flight.get_departure_gate(), flight.get_arrival_gate())]
      try:
        result = self.cur.execute(queries.sql_update_data, 
                                  (flight.get_departure_time(),flight.get_arrival_time(), flight.get_status(),
                                  gates[0], gates[1], flight.get_aircraft(),flight.get_flight_id()))
        self.conn.commit()
        
      except sqlite3.IntegrityError as e:
        raise ValueError("The flight could not be updated (" + str(e) + ").")
      
      return result
 
    def update_data(self):
          try:
            self.get_connection()
            flight_id = self.choose_flight()
            if flight_id is None:
              print("No Record Found")
              return
            flight = self.get_flight(flight_id)
            print("\nFlight:", flight.get_flight_number(), flight.get_from_airport(), "->",
                  flight.get_to_airport(), flight.get_departure_time())
    
            print("  Press Enter to keep the current value shown in [brackets];")
            print("  press Esc then Enter at any question to cancel.\n")
            flight.set_departure_time(ask_until_valid(
              "Departure time",
              check_datetime,
              flight.get_departure_time()))
            flight.set_arrival_time(ask_until_valid(
              "Arrival time",
              lambda value: check_arrival_time(flight.get_departure_time(), value),
              flight.get_arrival_time()))
            print("  Status: " + ", ".join(str(i + 1) + "=" + s for i, s in enumerate(flight_status)))
            flight.set_status(ask_until_valid("Status number", check_status_number, str(flight_status.index(flight.get_status()) + 1)))
            
            flight.set_departure_gate(ask_until_valid("Departure gate", check_gate,flight.get_departure_gate() or "-", required=False))
            
            flight.set_arrival_gate(ask_until_valid("Arrival gate", check_gate,flight.get_arrival_gate() or "-", required=False))
            
            flight.set_aircraft(ask_until_valid("Aircraft ID",lambda aircraft_id: check_aircraft(self.cur, aircraft_id),
                                                str(flight.get_aircraft())))
      
            result = self.update_flight(flight)
            if result.rowcount != 0:
              print("\n" + str(result.rowcount) + " Row(s) affected.")
              self.cur.execute(queries.sql_search, (flight_id,))
              print_table(self.cur, self.cur.fetchall())
            else:
              print("No Record Found")
          except CancelInput:
            print("\nCancelled - nothing was changed.")
          except Exception as e:
            print("Error: " + str(e))
          finally:
            self.conn.close()

  # -------------------------------------------------------------------
  # Menu option 6: delete a flight. 
  # -------------------------------------------------------------------
    def delete_data(self):
      try:
        self.get_connection()
        flight_number = (input("Enter Flight Number: ")).strip().upper()
        found = self.cur.execute(queries.sql_flight_number_exists, (flight_number,)).fetchone()
        flight = self.get_flight(found[0]) if found else None
        if flight is None:
          print("No Record Found")
          return
        
        print("\nFlight:", flight.get_flight_number(), flight.get_from_airport(), "->",
              flight.get_to_airport(), flight.get_departure_time())
        if input("Delete this flight and its crew assignments? (y/n): ").strip().lower() != "y":
          print("Nothing deleted.")
          return
  
        result = self.cur.execute(queries.sql_delete_data, (flight_number,))
        self.conn.commit()
        if result.rowcount != 0:
          print(flight_number + " deleted.")
        else:
          print("No Record Found")
      except Exception as e:
        print("Error: " + str(e))
      finally:
        self.conn.close()

  # -------------------------------------------------------------------
  # Menu option 7: assign a pilot to a flight
  # -------------------------------------------------------------------
    def assign_pilot(self):
      try:
        self.get_connection()
        print("\n  Upcoming flights that still need crew:")
        self.cur.execute(queries.sql_flights_needing_crew)
        print_table(self.cur, self.cur.fetchall(), "Every upcoming flight is fully crewed.")
        flight_id = int(input("Enter FlightID: "))
  
        print("\n  Current crew:")
        self.cur.execute(queries.sql_flight_crew, (flight_id,))
        print_table(self.cur, self.cur.fetchall(), "No pilots assigned yet.")
        if input("Show the pilot list? (y/n): ").strip().lower() == "y":
          self.cur.execute(queries.sql_select_pilots)
          print_table(self.cur, self.cur.fetchall())
        pilot_id = int(input("Enter PilotID: "))
        role_choice = input("Role (1=Captain, 2=Vice Captain): ").strip()
        role = pilot_rank[int(role_choice) - 1]
  
        self.assign_pilot_to_flight(flight_id, pilot_id, role)
        print("\nPilot assigned. Updated crew:")
        self.cur.execute(queries.sql_flight_crew, (flight_id,))
        print_table(self.cur, self.cur.fetchall())
      except Exception as e:
        print("Error: " + str(e))
      finally:
        self.conn.close()
  
    def assign_pilot_to_flight(self, flight_id, pilot_id, role):
      """
      Check if pilot is free and active before assigning to flight
      """
      flight = self.get_flight(flight_id)
      if flight is None:
        raise ValueError("Flight " + str(flight_id) + " does not exist.")
      self.cur.execute(queries.sql_get_pilot, (pilot_id,))
      pilot = self.cur.fetchone()
      if pilot is None:
        raise ValueError("Pilot " + str(pilot_id) + " does not exist.")
      if not pilot[4]:
        raise ValueError(pilot[1] + " " + pilot[2] + " is not an active pilot.")
  
      self.cur.execute(queries.sql_pilot_conflicts, (pilot_id, flight_id,
                                                  flight.get_arrival_time(),
                                                  flight.get_departure_time()))
      clash = self.cur.fetchone()
      if clash:
        raise ValueError("Pilot is already flying " + clash[0] + " (" + clash[1] +
                        " to " + clash[2] + ").")
      try:
        self.cur.execute(queries.sql_insert_assignment, (flight_id, pilot_id, role))
        self.conn.commit()
      except sqlite3.IntegrityError:
        raise ValueError("This flight already has a " + role + ", or the pilot is already on it.")
  # -------------------------------------
  # Menu option 8: view a pilot's schedule
  # -------------------------------------

    def get_pilot_schedule(self, pilot_id, from_date=""):
          start = check_date(from_date) if from_date else "1900-01-01"
          self.cur.execute(queries.sql_pilot_schedule, (pilot_id, start))
          return self.cur.fetchall()
    
    def view_pilot_schedule(self):
      try:
        self.get_connection()
        if input("Show the pilot list? (y/n): ").strip().lower() == "y":
          self.cur.execute(queries.sql_select_pilots)
          print_table(self.cur, self.cur.fetchall())
        pilot_id = int(input("Enter PilotID: "))
        from_date = input("Show flights from date (YYYY-MM-DD, Enter for all): ").strip()
        result = self.get_pilot_schedule(pilot_id, from_date)
        
        print("\n  Schedule :")
        print_table(self.cur, result, "No record of flights in that period.")
        
      except Exception as e:
        print("Error: " + str(e))
        
      finally:
        self.conn.close()

    # -------------------------------------------------------------------
    # Menu option 9: view / update destination (airport) information
    # -------------------------------------------------------------------

    def update_des(self, code, new_values):
          """update airport infos"""
          result = self.cur.execute(queries.sql_update_des, tuple(new_values) + (code.upper(),))
          self.conn.commit()
          return result
      
    def manage_destinations(self):
      try:
        self.get_connection()
        print("1. View all destinations")
        print("2. Update a destination")
        choice = input("Enter your choice: ").strip()
  
        if choice == "1":
          self.cur.execute(queries.sql_select_des)
          print_table(self.cur, self.cur.fetchall())

        elif choice =="2":
          code = input("Enter airport code: ").strip().upper()
          self.cur.execute(queries.sql_select_one_des, (code,))
          airport = self.cur.fetchone()
          if airport is None:
            print("No Record Found")
            return
          print_table(self.cur, [airport])

          print("\n  Press Enter to keep the current value shown in brackets.")
          columns = [c[0] for c in self.cur.description]
          current = dict(zip(columns, airport))
          new_values = (
            ask("Airport name", current["airport_name"]),
            ask("City", current["city"]),
            ask("Country", current["country"]),
            int(ask("UTC time (hours, -12 to 14)", current["utc_timezone"])),
            int(ask("x coordinate (longitude) (up to 3-digits)", current["x_coordinate"])),
            int(ask("y coordinate (latitude) (up to 3-digits)", current["y_coordinate"])),
            int(ask("Active? (1=yes, 0=no)", current["airport_status"])),
            int(ask("Largest aircraft it can handle (seats)", current["max_flight_size"])),
          )
          result = self.update_des(code, new_values)
          print("\n" + str(result.rowcount) + " Row(s) affected.")
          self.cur.execute(queries.sql_select_one_des, (code,))
          print_table(self.cur, self.cur.fetchall())

        else:
          print("Invalid Choice ")
      except Exception as e:
        print("Error: " + str(e))
      finally:
        self.conn.close()
  
    
    
class FlightInfo:
 
  def __init__(self):
    self.flightID = 0
    self.flightNumber = ''
    self.fromAirport = ''
    self.toAirport = ''
    self.aircraft = ''
    self.departureTime = ''
    self.arrivalTime = ''
    self.status = 'Boarding'
    self.departureGate = None
    self.arrivalGate = None
 
  def set_flight_id(self, flightID):
    self.flightID = flightID
 
  def set_flight_number(self, flightNumber):
    self.flightNumber = flightNumber
 
  def set_from_airport(self, fromAirport):
    self.fromAirport = fromAirport
 
  def set_to_airport(self, toAirport):
    self.toAirport = toAirport
 
  def set_aircraft(self, aircraft):
    self.aircraft = aircraft
 
  def set_departure_time(self, departureTime):
    self.departureTime = departureTime
 
  def set_arrival_time(self, arrivalTime):
    self.arrivalTime = arrivalTime
 
  def set_status(self, status):
    self.status = status
 
  def set_departure_gate(self, departureGate):
    self.departureGate = departureGate
 
  def set_arrival_gate(self, arrivalGate):
    self.arrivalGate = arrivalGate
 
  def get_flight_id(self):
    return self.flightID
 
  def get_flight_number(self):
    return self.flightNumber
 
  def get_from_airport(self):
    return self.fromAirport
 
  def get_to_airport(self):
    return self.toAirport
 
  def get_aircraft(self):
    return self.aircraft
 
  def get_departure_time(self):
    return self.departureTime
 
  def get_arrival_time(self):
    return self.arrivalTime
 
  def get_status(self):
    return self.status
 
  def get_departure_gate(self):
    return self.departureGate
 
  def get_arrival_gate(self):
    return self.arrivalGate
 


# The main function will parse arguments.
# These argument will be definded by the users on the console.
# The user will select a choice from the menu to interact with the database.
 
if __name__ == "__main__":
  while True:
    print("\n Menu:")
    print("**********")
    print(" 1. Create/ Reset tables and load sample data")
    print(" 2. Add a new flight")
    print(" 3. View all flights")
    print(" 4. View flights by criteria")
    print(" 5. Update flight information")
    print(" 6. Delete a flight")
    print(" 7. Assign pilot to flight")
    print(" 8. View pilot schedule")
    print(" 9. View/Update destination information")
    print(" 0. Exit\n")
 
    try:
      __choose_menu = int(input("Enter your choice: "))
    except ValueError:
      print("Invalid Choice")
      continue
    db_ops = DBOperations()
    if __choose_menu == 1:
      db_ops.create_table()
      
    elif __choose_menu == 2:
      db_ops.insert_data()
      
    elif __choose_menu == 3:
      db_ops.select_all()
      
    elif __choose_menu == 4:
      db_ops.search_by_criteria()
      
    elif __choose_menu == 5:
      db_ops.update_data()
      
    elif __choose_menu == 6:
      db_ops.delete_data()
      
    elif __choose_menu == 7:
      db_ops.assign_pilot()
      
    elif __choose_menu == 8:
      db_ops.view_pilot_schedule()
      
    elif __choose_menu == 9:
      db_ops.manage_destinations()
      
    elif __choose_menu == 0:
      exit(0)
    else:
      print("Invalid Choice")