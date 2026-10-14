-- Flight Management Database - schema (SQLite)

-- ---------------------------------------------------------------------
-- AIRPORTS
-- ---------------------------------------------------------------------
CREATE TABLE airports (
    airport_id      INTEGER      PRIMARY KEY AUTOINCREMENT,
    airport_code    CHAR(3)      NOT NULL UNIQUE
                    CHECK (length(airport_code) = 3 AND airport_code = upper(airport_code)),
    airport_name    VARCHAR(100) NOT NULL,
    city            VARCHAR(50)  NOT NULL,
    country         VARCHAR(50)  NOT NULL,
    utc_timezone    INT          NOT NULL
                    CHECK (utc_timezone BETWEEN -12 AND 14),    -- e.g. '8 for +8 and -12 for -12'
    x_coordinate    INT          NOT NULL,                  
    y_coordinate    INT          NOT NULL,                  
    airport_status  BOOLEAN      NOT NULL DEFAULT 1 CHECK (airport_status IN (0, 1)),
    max_flight_size INT          NOT NULL CHECK (max_flight_size > 0)
);

-- ---------------------------------------------------------------------
-- AIRCRAFT_MAKE: the different types of aircraft in the fleet. Each aircraft is of a single make.
-- ---------------------------------------------------------------------
CREATE TABLE aircraft_make (
    aircraft_make_id    INTEGER     PRIMARY KEY AUTOINCREMENT,
    manufacturer        VARCHAR(30)  NOT NULL,             -- e.g. 'Airbus'
    model               VARCHAR(30)  NOT NULL,             -- e.g. 'A350-1000'
    body_type           VARCHAR(12)  NOT NULL,
    engine_count        SMALLINT     NOT NULL CHECK (engine_count BETWEEN 1 AND 4),
    seat_capacity       SMALLINT     NOT NULL CHECK (seat_capacity > 0),
    year_introduced     SMALLINT     NOT NULL CHECK (year_introduced BETWEEN 1900 AND 2100),         
    max_range_km        SMALLINT     NOT NULL CHECK (max_range_km > 0),
);


-- ---------------------------------------------------------------------
-- AIRCRAFT: the individual planes
-- ---------------------------------------------------------------------
CREATE TABLE aircraft (
    aircraft_id         INTEGER         PRIMARY KEY AUTOINCREMENT,
    registration_id     VARCHAR(10)     NOT NULL UNIQUE,      
    aircraft_make_id    INT             NOT NULL,
    aircraft_status     VARCHAR(20)     NOT NULL DEFAULT 'Active',
    FOREIGN KEY (aircraft_make_id) REFERENCES aircraft_make (aircraft_make_id)
                                   ON UPDATE CASCADE ON DELETE RESTRICT
);


-- ---------------------------------------------------------------------
-- PILOTS
-- ---------------------------------------------------------------------
CREATE TABLE pilots (
    pilot_id        INTEGER      PRIMARY KEY AUTOINCREMENT,
    licence_number  VARCHAR(20)  NOT NULL UNIQUE,
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    rank            VARCHAR(20)  NOT NULL 
    email           VARCHAR(100) NOT NULL UNIQUE,
    hire_date       DATE         NOT NULL,             -- 'YYYY-MM-DD'
    flight_hours    INT          NOT NULL DEFAULT 0,
    pilot_status    BOOLEAN      NOT NULL DEFAULT 1 CHECK (pilot_status IN (0, 1))
);



-- ---------------------------------------------------------------------
-- FLIGHTS
-- ---------------------------------------------------------------------
CREATE TABLE flights (
    flight_id       INTEGER      PRIMARY KEY AUTOINCREMENT,
    flight_number   VARCHAR(8)   NOT NULL UNIQUE,             
    from_airport_id INT          NOT NULL,
    to_airport_id   INT          NOT NULL,
    aircraft_id     INT          NOT NULL,
    departure_time  DATETIMENOT NULL,
    arrival_time    DATETIME     NOT NULL,
    flight_status   VARCHAR(10)  NOT NULL DEFAULT 'Arrived'
                    CHECK (flight_status IN  ("Scheduled", "Boarding", "Departed", "Arrived", "Delayed", "Cancelled")),
    departure_gate  VARCHAR(5),
    arrival_gate    VARCHAR(5),
    FOREIGN KEY (from_airport_id) REFERENCES airports (airport_id)
                                  ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (to_airport_id)   REFERENCES airports (airport_id)
                                  ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (aircraft_id)     REFERENCES aircraft (aircraft_id)
                                  ON UPDATE CASCADE ON DELETE RESTRICT,
    CHECK (from_airport_id <> to_airport_id),
    CHECK (arrival_time > departure_time),
    UNIQUE (flight_number, departure_time)
);


-- ---------------------------------------------------------------------
-- FLIGHT_ASSIGNMENT
-- ---------------------------------------------------------------------
CREATE TABLE flight_assignment (
    assignment_id   INTEGER      PRIMARY KEY AUTOINCREMENT,
    flight_id       INT          NOT NULL,
    pilot_id        INT          NOT NULL,
    role            VARCHAR(15)  NOT NULL
                    CHECK (role IN ('Captain', 'Vice Captain')),
    assigned_at     DATETIME     NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (flight_id) REFERENCES flights (flight_id)
                            ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (pilot_id)  REFERENCES pilots (pilot_id)
                            ON UPDATE CASCADE ON DELETE RESTRICT,
);

