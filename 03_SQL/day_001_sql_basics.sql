-- FALCON DAY 1 - SQL Basics
-- Goal: practice basic SELECT, WHERE and ORDER BY logic

-- Example table:
-- players(player_id, name, position, team, age, goals, assists)

-- 1. Select all players
SELECT *
FROM players;

-- 2. Select only names and positions
SELECT name, position
FROM players;

-- 3. Find players from one team
SELECT name, position, team
FROM players
WHERE team = 'Example FC';

-- 4. Find attacking players
SELECT name, position, goals
FROM players
WHERE position = 'Forward';

-- 5. Sort players by goals
SELECT name, goals
FROM players
ORDER BY goals DESC;

-- 6. Find players with at least 5 goals
SELECT name, goals
FROM players
WHERE goals >= 5
ORDER BY goals DESC;