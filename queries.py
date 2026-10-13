"""
queries.py

All the SQL statement used by the Flight Management application.

Keeping the SQL in one module allows each query to be read, reviewed and edited on its own.
The main.py uses the query by queries.sql_insert , queries.sql_select_flights ,... and so on.

"""


sql_select_planes = """
  select * 
  FROM aircraft a
  JOIN aircraft_make m ON m.aircraft_make_id = a.aircraft_make_id
"""

sql_flight_number_exists = """SELECT flight_id FROM flights WHERE flight_number = ?"""


sql_select_flights = """
  SELECT  flight_id, f.flight_number, fr.airport_code AS from_airport, t.airport_code AS to_airport,
          t.city AS to_city, f.departure_time, f.arrival_time, f.flight_status,
          f.departure_gate AS dep_gate, f.arrival_gate AS arr_gate,
          a.registration_id AS aircraft,
          (SELECT count(*) from flight_assignment fa 
           WHERE fa.flight_id = f.flight_id) as crew
    from flights f
    JOIN airports fr on fr.airport_id = f.from_airport_id
    JOIN airports t on t.airport_id  = f.to_airport_id
    JOIN aircraft a on a.aircraft_id = f.aircraft_id
    """



sql_select_all = sql_select_flights + " order by departure_time"

sql_search = sql_select_flights + " WHERE f.flight_id = ?"

sql_flight_number_exists = """SELECT flight_id FROM flights WHERE flight_number = ?"""

sql_find_airport = """
  select airport_id, airport_code, airport_status, max_flight_size
  FROM airports WHERE airport_code = ?
  """

sql_find_aircraft = """
  SELECT aircraft_id, registration_id, aircraft_status
  FROM aircraft 
  WHERE aircraft_id = ?
  """

sql_insert = """
  INSERT into flights 
  (flight_number, from_airport_id, to_airport_id, aircraft_id,
    departure_time, arrival_time, flight_status,
    departure_gate, arrival_gate)
  VALUES (?,
          (SELECT airport_id FROM airports WHERE airport_code = ?),
          (SELECT airport_id FROM airports WHERE airport_code = ?),
          ?, ?, ?, 'Scheduled', ?, ?)
  """

sql_update_data = """
  UPDATE flights
  SET departure_time = ?, arrival_time = ?, flight_status = ?,
         departure_gate = ?, arrival_gate = ?,
         aircraft_id = ?
  WHERE flight_id = ?"""

sql_get_flight = """
  SELECT flight_id, flight_number, fr.airport_code, t.airport_code,
    f.aircraft_id, departure_time, arrival_time, flight_status,
    departure_gate, arrival_gate
  from flights f
  JOIN airports fr on fr.airport_id = f.from_airport_id
  JOIN airports t  on t.airport_id  = f.to_airport_id
  WHERE flight_id = ?
"""

sql_select_pilots = """
  select FIRST_NAME, LAST_NAME, RANK, PILOT_ID,
    EMAIL, PILOT_STATUS, HIRE_DATE, LICENCE_NUMBER from pilots
  order by last_name asc
"""

sql_pilot_schedule = """
  SELECT f.flight_id, f.flight_number, fr.airport_code ORIGIN,
    t.airport_code DESTINATION , f.departure_time, f.arrival_time, fa.role, f.flight_status
  FROM flight_assignment fa
  JOIN flights f   on f.flight_id   = fa.flight_id
  JOIN airports fr on fr.airport_id = f.from_airport_id
  JOIN airports t  on t.airport_id  = f.to_airport_id
  WHERE fa.pilot_id = ?
     AND date(f.departure_time) >= ?
  ORDER BY f.departure_time
"""

sql_select_des = """
  SELECT airport_code, airport_name, city, country, utc_timezone, max_flight_size,
         CASE airport_status WHEN 1 
              THEN 'Active' ELSE 'Inactive' 
              END AS status
  FROM airports
  ORDER BY airport_code
"""

sql_select_one_des = """
    SELECT * FROM airports WHERE airport_code = ?
"""

sql_update_des = """
    UPDATE airports
    SET airport_name=? , city=?, country=?, utc_timezone=?,
      x_coordinate = ? , y_coordinate=?, airport_status =?, 
      max_flight_size=?
    WHERE airport_code =?
"""

# deleting a flight by flight_number
sql_delete_data = "DELETE FROM flights WHERE flight_number = ?"

sql_get_pilot = """SELECT pilot_id, first_name, last_name, rank, pilot_status
FROM pilots WHERE pilot_id = ?"""

sql_pilot_conflicts = """
  SELECT f.flight_number, f.departure_time, f.arrival_time
  FROM flight_assignment fa
  JOIN flights f ON f.flight_id = fa.flight_id
  WHERE fa.pilot_id = ?
    AND f.flight_id <> ?
    AND f.flight_status <> 'Cancelled'
    AND f.departure_time < ?
    AND f.arrival_time   > ?
  """

sql_insert_assignment = """
INSERT INTO flight_assignment (flight_id, pilot_id, role) VALUES (?, ?, ?)"""

sql_flight_crew = """
SELECT p.pilot_id, p.first_name || ' ' || p.last_name AS name, fa.role, p.licence_number
FROM flight_assignment fa
JOIN pilots p ON p.pilot_id = fa.pilot_id
WHERE fa.flight_id = ?
ORDER BY fa.role
"""

sql_flights_needing_crew ="""
SELECT f.flight_id, f.flight_number, f.departure_time, f.flight_status,
       COUNT(fa.pilot_id) AS pilots_assigned
FROM flights f
LEFT JOIN flight_assignment fa ON fa.flight_id = f.flight_id
WHERE f.flight_status NOT IN ('Cancelled', 'Arrived', 'Departed')
GROUP BY f.flight_id
HAVING COUNT(fa.pilot_id) < 2
ORDER BY f.departure_time
"""