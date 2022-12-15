-- Creation of dim teams
CREATE TABLE IF NOT EXISTS dim_teams (
    id integer NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

-- Creation of dim competitions
CREATE TABLE IF NOT EXISTS dim_competitions (
    id integer NOT NULL,
    name text NOT NULL,
    PRIMARY KEY (id)
);

-- Creation of fact competitions
CREATE TABLE IF NOT EXISTS fact_competitions (
    competition_id integer NOT NULL,
    team_id integer NOT NULL,
        PRIMARY KEY (competition_id, team_id)
        -- CONSTRAINT fk_team
        -- FOREIGN KEY(team_id)
	    -- REFERENCES dim_teams(id),
        -- CONSTRAINT fk_competition
        -- FOREIGN KEY(competition_id)
	    -- REFERENCES dim_competitions(id)
);
