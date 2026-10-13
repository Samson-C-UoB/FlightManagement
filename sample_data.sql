-- =====================================================================
-- Flight Management Database - sample data. 
-- (sample data generation was with help of AI to save time in thinking 
-- of all the airports name and locations) 
-- =====================================================================

-- ---------------------------------------------------------------------
-- AIRPORTS (15) 
-- ---------------------------------------------------------------------
INSERT INTO airports (airport_code, airport_name, city, country, utc_timezone,
                      x_coordinate, y_coordinate, airport_status, max_flight_size) VALUES
('LHR', 'Heathrow Airport',                    'London',      'United Kingdom',        0,    0,  51, 1, 550),
('JFK', 'John F. Kennedy International',       'New York',    'United States',        -5,  -74,  41, 1, 550),
('CDG', 'Charles de Gaulle Airport',           'Paris',       'France',                1,    3,  49, 1, 550),
('DXB', 'Dubai International',                 'Dubai',       'United Arab Emirates',  4,   55,  25, 1, 550),
('HKG', 'Hong Kong International',             'Hong Kong',   'Hong Kong',             8,  114,  22, 1, 550),
('NRT', 'Narita International',                'Tokyo',       'Japan',                 9,  140,  36, 1, 550),
('SIN', 'Changi Airport',                      'Singapore',   'Singapore',             8,  104,   1, 1, 550),
('YYZ', 'Toronto Pearson International',       'Toronto',     'Canada',               -5,  -80,  44, 1, 500),
('FRA', 'Frankfurt Airport',                   'Frankfurt',   'Germany',               1,    9,  50, 1, 550),
('AMS', 'Amsterdam Schiphol',                  'Amsterdam',   'Netherlands',           1,    5,  52, 1, 400),
('MAD', 'Adolfo Suarez Madrid-Barajas',        'Madrid',      'Spain',                 1,   -4,  40, 1, 400),
('FCO', 'Leonardo da Vinci-Fiumicino',         'Rome',        'Italy',                 1,   12,  42, 1, 350),
('SYD', 'Sydney Kingsford Smith',              'Sydney',      'Australia',            10,  151, -34, 0, 550),
('LAX', 'Los Angeles International',           'Los Angeles', 'United States',        -8, -118,  34, 1, 550),
('EDI', 'Edinburgh Airport',                   'Edinburgh',   'United Kingdom',        0,   -3,  56, 1, 220);

-- ---------------------------------------------------------------------
-- AIRCRAFT_MAKE (12) 
-- ---------------------------------------------------------------------
INSERT INTO aircraft_make (manufacturer, model, body_type, engine_count, seat_capacity, year_introduced, max_range_km) VALUES
('Airbus', 'A320neo',     'Narrow-body', 2, 180, 2016,  6300),
('Airbus', 'A321neo',     'Narrow-body', 2, 200, 2017,  7400),
('Airbus', 'A350-1000',   'Wide-body',   2, 331, 2018, 16100),
('Airbus', 'A330-900neo', 'Wide-body',   2, 287, 2018, 13300),
('Airbus', 'A380-800',    'Wide-body',   4, 469, 2007, 15000),
('Airbus', 'A220-300',    'Narrow-body', 2, 145, 2016,  6300),
('Boeing', '787-9',       'Wide-body',   2, 216, 2014, 14000),
('Boeing', '787-10',      'Wide-body',   2, 256, 2018, 11900),
('Boeing', '777-300ER',   'Wide-body',   2, 299, 2004, 13650),
('Boeing', '737 MAX 8',   'Narrow-body', 2, 178, 2017,  6570),
('Boeing', '767-300ER',   'Wide-body',   2, 252, 1988, 11000),
('Boeing', '747-8',       'Wide-body',   4, 410, 2012, 14300);

-- ---------------------------------------------------------------------
-- AIRCRAFT (12)
-- ---------------------------------------------------------------------
INSERT INTO aircraft (registration_id, aircraft_make_id, aircraft_status) VALUES
('G-FMAA', 1, 'Active'),        -- A320neo
('G-FMAB', 1, 'Active'),        -- A320neo
('G-FMAC', 7, 'Active'),        -- 787-9
('G-FMAD', 9, 'Active'),        -- 777-300ER
('G-FMAE', 3, 'Active'),        -- A350-1000
('G-FMAF', 3, 'Active'),        -- A350-1000
('G-FMAG', 8, 'Active'),        -- 787-10
('G-FMAH', 7, 'Active'),        -- 787-9
('G-FMAI', 2, 'Active'),        -- A321neo
('G-FMAJ', 2, 'Active'),        -- A321neo
('G-FMAK', 9, 'Active'),        -- 777-300ER
('G-FMAL', 2, 'Maintenance');   -- A321neo

-- ---------------------------------------------------------------------
-- PILOTS
-- ---------------------------------------------------------------------
INSERT INTO pilots (licence_number, first_name, last_name, rank, email, hire_date, flight_hours, pilot_status) VALUES
('UK-ATPL-10231', 'Sarah',    'Mitchell',  'Captain',       'sarah.mitchell@flymanage.co.uk',  '2009-03-16', 14250, 1),
('UK-ATPL-10544', 'James',    'Okafor',    'Captain',       'james.okafor@flymanage.co.uk',    '2011-07-04', 12100, 1),
('UK-ATPL-11002', 'Wei',      'Chen',      'Captain',       'wei.chen@flymanage.co.uk',        '2012-01-09', 11380, 1),
('UK-ATPL-11870', 'Priya',    'Sharma',    'Captain',       'priya.sharma@flymanage.co.uk',    '2013-09-23', 10020, 1),
('UK-ATPL-12215', 'Thomas',   'Byrne',     'Captain',       'thomas.byrne@flymanage.co.uk',    '2014-05-12',  9310, 1),
('UK-ATPL-12690', 'Elena',    'Rossi',     'Captain',       'elena.rossi@flymanage.co.uk',     '2015-02-02',  8740, 1),
('UK-ATPL-13104', 'David',    'Kowalski',  'Captain',       'david.kowalski@flymanage.co.uk',  '2016-10-17',  8015, 1),
('UK-CPL-20117',  'Hannah',   'Wright',    'First Officer', 'hannah.wright@flymanage.co.uk',   '2018-04-30',  4120, 1),
('UK-CPL-20389',  'Kwame',    'Mensah',    'First Officer', 'kwame.mensah@flymanage.co.uk',    '2019-01-21',  3650, 1),
('UK-CPL-20642',  'Sofia',    'Martinez',  'First Officer', 'sofia.martinez@flymanage.co.uk',  '2019-08-05',  3210, 1),
('UK-CPL-20958',  'Liam',     'O''Connor', 'First Officer', 'liam.oconnor@flymanage.co.uk',    '2020-11-09',  2480, 1),
('UK-CPL-21233',  'Aisha',    'Rahman',    'First Officer', 'aisha.rahman@flymanage.co.uk',    '2021-06-14',  1975, 1),
('UK-CPL-21507',  'Kenji',    'Tanaka',    'First Officer', 'kenji.tanaka@flymanage.co.uk',    '2022-03-07',  1540, 1),
('UK-CPL-21816',  'Olivia',   'Hughes',    'First Officer', 'olivia.hughes@flymanage.co.uk',   '2023-02-27',  1120, 1),
('UK-CPL-22090',  'Marcus',   'Lindqvist', 'First Officer', 'marcus.lindqvist@flymanage.co.uk','2024-01-15',   640, 0);

-- ---------------------------------------------------------------------
-- FLIGHTS - from_airport_id / to_airport_id reference airports.
-- ---------------------------------------------------------------------
INSERT INTO flights (flight_number, from_airport_id, to_airport_id, aircraft_id, departure_time, arrival_time,
                     flight_status, departure_gate, arrival_gate) VALUES
('FM201', 1,  3,  1,  '2026-10-09 07:30', '2026-10-09 08:45', 'Arrived',   'B12', 'K32'),
('FM301', 1,  4,  4,  '2026-10-09 21:00', '2026-10-10 04:00', 'Arrived',   'C20', 'A14'),
('FM101', 1,  2,  3,  '2026-10-12 09:00', '2026-10-12 17:00', 'Scheduled', 'A10', 'B22'),
('FM102', 2,  1,  3,  '2026-10-12 20:00', '2026-10-13 03:00', 'Scheduled', NULL,  'A11'),
('FM401', 1,  5,  5,  '2026-10-12 18:00', '2026-10-13 06:00', 'Scheduled', 'C05', 'W51'),
('FM202', 1,  3,  1,  '2026-10-12 14:00', '2026-10-12 15:15', 'Delayed',   'B14', 'K40'),
('FM501', 1,  6,  6,  '2026-10-13 10:00', '2026-10-13 23:45', 'Scheduled', 'C11', 'N62'),
('FM601', 1,  7,  7,  '2026-10-13 20:30', '2026-10-14 10:00', 'Scheduled', 'C02', 'D41'),
('FM701', 1,  8,  8,  '2026-10-13 12:00', '2026-10-13 19:45', 'Scheduled', 'A04', 'E73'),
('FM211', 1,  9,  2,  '2026-10-13 08:00', '2026-10-13 09:30', 'Cancelled', 'B03', 'A26'),
('FM221', 1,  10, 2,  '2026-10-14 06:45', '2026-10-14 07:50', 'Scheduled', 'B05', 'D07'),
('FM231', 1,  11, 9,  '2026-10-14 11:15', '2026-10-14 13:35', 'Scheduled', 'B08', 'J41'),
('FM241', 1,  12, 10, '2026-10-14 15:00', '2026-10-14 17:35', 'Scheduled', 'B09', 'E12'),
('FM801', 1,  14, 11, '2026-10-15 10:30', '2026-10-15 21:40', 'Scheduled', 'A12', 'T50'),
('FM251', 1,  15, 1,  '2026-10-15 07:00', '2026-10-15 08:25', 'Scheduled', 'D01', '04');

-- ---------------------------------------------------------------------
-- FLIGHT_ASSIGNMENT (15)
-- ---------------------------------------------------------------------
INSERT INTO flight_assignment (flight_id, pilot_id, role, assigned_at) VALUES
(1,  1,  'Captain',       '2026-09-20 10:00'),
(1,  8,  'First Officer', '2026-09-20 10:00'),
(2,  2,  'Captain',       '2026-09-20 10:05'),
(2,  9,  'First Officer', '2026-09-20 10:05'),
(3,  3,  'Captain',       '2026-09-25 09:30'),
(3,  10, 'First Officer', '2026-09-25 09:30'),
(4,  3,  'Captain',       '2026-09-25 09:35'),
(4,  10, 'First Officer', '2026-09-25 09:35'),
(5,  4,  'Captain',       '2026-09-26 14:10'),
(5,  11, 'First Officer', '2026-09-26 14:10'),
(6,  1,  'Captain',       '2026-09-27 08:00'),
(6,  12, 'First Officer', '2026-09-27 08:00'),
(7,  5,  'Captain',       '2026-09-28 16:20'),
(7,  13, 'First Officer', '2026-09-28 16:20'),
(15, 5,  'Captain',       '2026-10-01 11:45');
