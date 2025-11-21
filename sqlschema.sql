CREATE TABLE IF NOT EXISTS conferences (
    conference_id   CHAR(36) PRIMARY KEY,
    name            VARCHAR(100),
    alias           VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS divisions (
    division_id     CHAR(36) PRIMARY KEY,
    name            VARCHAR(100),
    alias           VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS venues (
    venue_id        CHAR(36) PRIMARY KEY,
    name            VARCHAR(150),
    city            VARCHAR(100),
    state           VARCHAR(50),
    country         VARCHAR(50),
    zip             VARCHAR(20),
    address         VARCHAR(200),
    capacity        INT,
    surface         VARCHAR(50),
    roof_type       VARCHAR(50),
    latitude        DECIMAL(10,6),
    longitude       DECIMAL(10,6)
);


CREATE TABLE IF NOT EXISTS teams (
    team_id            CHAR(36) PRIMARY KEY,
    market             VARCHAR(100) NOT NULL,
    name               VARCHAR(100) NOT NULL,
    alias              VARCHAR(20),
    founded            INT,
    mascot             VARCHAR(100),
    fight_song         VARCHAR(200),
    championships_won  INT,

    conference_id      CHAR(36),
    division_id        CHAR(36),
    venue_id           CHAR(36),

    CONSTRAINT fk_team_conference
        FOREIGN KEY (conference_id) REFERENCES conferences(conference_id),

    CONSTRAINT fk_team_division
        FOREIGN KEY (division_id) REFERENCES divisions(division_id),

    CONSTRAINT fk_team_venue
        FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);


CREATE TABLE IF NOT EXISTS seasons (
    season_id      CHAR(36) PRIMARY KEY,
    year           INT,
    start_date     DATE,
    end_date       DATE,
    status         VARCHAR(50),
    type_code      VARCHAR(20)
);



CREATE TABLE IF NOT EXISTS players (
    player_id       CHAR(36) PRIMARY KEY,
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    abbr_name       VARCHAR(50),
    birth_place     VARCHAR(200),
    position        VARCHAR(20),
    height          INT,
    weight          INT,
    status          VARCHAR(50),
    eligibility     VARCHAR(20),
    
    team_id         CHAR(36),

    CONSTRAINT fk_player_team
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
);



CREATE TABLE IF NOT EXISTS player_statistics (
    stat_id              INT AUTO_INCREMENT PRIMARY KEY,
    player_id            CHAR(36),
    team_id              CHAR(36),
    season_id            CHAR(36),

    games_played         INT,
    games_started        INT,
    rushing_yards        INT,
    rushing_touchdowns   INT,
    receiving_yards      INT,
    receiving_touchdowns INT,
    kick_return_yards    INT,
    fumbles              INT,

    CONSTRAINT fk_stat_player
        FOREIGN KEY (player_id) REFERENCES players(player_id),

    CONSTRAINT fk_stat_team
        FOREIGN KEY (team_id) REFERENCES teams(team_id),

    CONSTRAINT fk_stat_season
        FOREIGN KEY (season_id) REFERENCES seasons(season_id)
);



CREATE TABLE IF NOT EXISTS rankings (
    ranking_id       INT AUTO_INCREMENT PRIMARY KEY,
    poll_id          VARCHAR(50),
    poll_name        VARCHAR(100),
    
    season_id        CHAR(36),
    week             INT,
    effective_time   TIMESTAMP,

    team_id          CHAR(36),
    `rank`             INT,
    prev_rank        INT,
    points           INT,
    fp_votes         INT,
    wins             INT,
    losses           INT,
    ties             INT,

    CONSTRAINT fk_rank_season
        FOREIGN KEY (season_id) REFERENCES seasons(season_id),

    CONSTRAINT fk_rank_team
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
);


CREATE TABLE IF NOT EXISTS coaches (
    coach_id         CHAR(36) PRIMARY KEY,
    full_name        VARCHAR(200),
    position         VARCHAR(100),
    
    team_id          CHAR(36),

    CONSTRAINT fk_coach_team
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
);



✅ Execution Order (VERY IMPORTANT)

Run in this order to avoid FK errors:

1️⃣ conferences
2️⃣ divisions
3️⃣ venues
4️⃣ teams
5️⃣ seasons
6️⃣ players
7️⃣ player_statistics
8️⃣ rankings
9️⃣ coaches



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
