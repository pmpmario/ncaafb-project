create database ncaafb_db;


use ncaafb_db;
select database();

select * from coaches;
select * from conferences;
select * from divisions;
select * from venues;
select * from teams;
select * from seasons;
select * from players;
select * from player_statistics;
DESCRIBE player_statistics;

select * from rankings;
describe rankings;
select * from team_game_counts;
DESCRIBE teams;

SHOW PROCESSLIST;

SELECT CONCAT('KILL ',id,';')
FROM information_schema.PROCESSLIST
WHERE COMMAND = 'Sleep' AND TIME > 5;
KILL 920;
KILL 1000;
KILL 928;
KILL 1001;
KILL 924;
KILL 917;
KILL 927;


INSERT IGNORE INTO teams (
    team_id, market, name, alias
) VALUES (
    'a2ee495d-37c7-45ac-ac3d-d3a492a219c1',
    'Iowa', 'Hawkeyes', 'IOWA'
);

INSERT IGNORE INTO seasons (
    season_id, year, status, type_code
) VALUES
('ff53e5e4-10ef-4842-a0b7-b489956fa07e', 2022, 'closed', 'REG'),
('f58c6dbf-9dfe-487e-8b0b-af66af887206', 2023, 'closed', 'REG'),
('908fbc20-f5c7-11ee-a306-c311afc28263', 2024, 'closed', 'REG');


CREATE TABLE team_game_counts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    season_id CHAR(36),
    season_year INT,
    team_id CHAR(36),
    team_name VARCHAR(100),
    game_id CHAR(36),
    is_home BOOLEAN,
    FOREIGN KEY (season_id) REFERENCES seasons(season_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE TABLE most_used_venues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venue_id VARCHAR(64) NOT NULL,
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    venue_state VARCHAR(50),
    games_hosted INT NOT NULL,
    
    INDEX idx_venue_id (venue_id)
);


CREATE TABLE game_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    season_id VARCHAR(64),
    season_year INT,
    week INT,
    team_id VARCHAR(64),
    points_scored INT,
    game_id VARCHAR(64),
    INDEX(team_id),
    INDEX(season_id),
    INDEX(week)
);
