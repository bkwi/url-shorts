CREATE DATABASE shorts_db;
\c shorts_db

CREATE TABLE short_urls (
    short_id varchar(32) NOT NULL,
    url text,
    UNIQUE(short_id)
);

CREATE INDEX short_id_index ON short_urls USING hash (short_id);
