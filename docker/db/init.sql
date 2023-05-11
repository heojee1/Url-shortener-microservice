-- Create a users table 
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR (50) UNIQUE NOT NULL,
    password VARCHAR NOT NULL
);

-- Create a urls table
CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    original VARCHAR NOT NULL,
    short VARCHAR (50) UNIQUE NOT NULL,
    username VARCHAR (50) NOT NULL,
    FOREIGN KEY (username)
        REFERENCES users(username)
);
