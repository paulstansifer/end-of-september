-- Table creation script for the YeabBut database.
-- > mysql -u yeahbut yb < build_db.sql

-- This is HIGHLY DESTRUCTIVE!
drop table if exists user;
drop table if exists post;
drop table if exists post_content;
drop table if exists vote;
drop table if exists cluster;
drop table if exists ticket;
drop table if exists relevance;

create table user (
    id serial primary key,
    cid integer references cluster,
    name text, -- Name uniqueness enforced with application logic
    password text,
    email text,
    date_joined timestamp default now()
    );

create table ticket (
    uid integer references user,
    ticket text,
    last_used timestamp default now()
    );

create table post (
    id serial primary key,
    uid integer references user,
    claim text,
    -- content text,
    broad_support double,
    date_posted timestamp default now()
    );

create table post_content (
    pid integer references post,
    raw text,
    safe_html text,
    tokens text
    );


create table vote (
    -- id serial primary key,
    uid integer references user,
    pid integer references post,
    date_voted timestamp default now(),
    primary key(uid, pid)
    );

create table cluster (
    id serial primary key,
    num_users integer
    );

create table relevance (
    term varchar(255),
    uid integer references user,
    pid integer references post
    );

create table pullquote (
    pid integer references post,
    start_idx integer,
    len integer,
    votes integer
    );
    