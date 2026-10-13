# Flight Management Database

A CLI application for airline staff to manage flights, pilots and
destinations (airports) stored in an SQLite database. 


## To start 

Open a terminal in the repository folder and run:

`
python3 main.py
`

On the first run the database is built automatically from `schema.sql` and
`sample_data.sql`. 


## Functionality


| Option | What it does |
|---|---|
| 1. Create/ Reset tables and load sample data | Runs `schema.sql` and `sample_data.sql` through `database_setup.py` |
| 2. Add a new flight |
| 3. View all flights | Return all flight with details such as airports, times, status, gates|
| 4. View flights by criteria | Filter by various features , such as destination date range and flight number |
| 5. Update flight information | Pick one flight by FlightID, then change different features of it|
| 6. Delete a flight | Remove a flight by flight number |
| 7. Assign pilot to flight | Show the flights still needing crew, then assign active pilot to it|
| 8. View pilot schedule | Show ll flights for one pilot |
| 9. View/Update destination information | View all airports, or update one |
| 0. Exit | |

## Documentations
Please refer to `FlightManagement_Document.pdf` for further details