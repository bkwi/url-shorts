CREATE DATABASE shorts_db;
\c shorts_db

CREATE TABLE short_urls (
    id serial PRIMARY KEY,
    short_id varchar(16) NOT NULL,
    url text
)
