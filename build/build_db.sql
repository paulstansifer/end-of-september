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
drop table if exists pull_quote;
drop table if exists history;

--todo: should we declare everything NOT NULL?

create table user (
    id serial primary key,
    cid integer references cluster,
    name text, -- Name uniqueness enforced with application logic
    password text,
    email text,
    date_joined timestamp default now()
    ) engine=InnoDB;  
--we use InnoDB so we can have transactions
--InnoDB uses fsync a lot, so reiserfs will likely be faster than ext3

create table ticket (
    uid integer references user,
    ticket text,
    last_used timestamp default now()
    ) engine=InnoDB;

create table post (
    id serial primary key,
    uid integer references user,
    claim text,
    -- content text,
    broad_support double,
    date_posted timestamp default now()
    ) engine=InnoDB;

create table post_content (
    pid integer references post,
    raw text,
    safe_html text,
    tokens text
    ) engine=InnoDB;


create table vote (
    -- id serial primary key,
    uid integer references user,
    pid integer references post,
    date_voted timestamp default now(),
    primary key(uid, pid)
    ) engine=InnoDB;

create table cluster (
    id serial primary key,
    num_users integer
    ) engine=InnoDB;

create table cluster_connection (
    cid_from integer references cluster,
    cid_to integer references cluster,
    primary key(cid_from, cid_to)
    -- connection strength?
    ) engine=InnoDB;

create table relevance (
    term varchar(255),
    uid integer references user,
    pid integer references post
    ) engine=InnoDB;

create table pull_quote (
    pid integer references post,
    start_idx integer,
    len integer,
    votes integer
    ) engine=InnoDB;

create table history (
    uid integer references user,
    pid integer references post,
    date_viewed timestamp default now(),
    primary key(uid, pid)
    ) engine=InnoDB;
