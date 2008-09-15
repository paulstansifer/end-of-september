-- Table creation script for the YeabBut database.
-- > mysql -u yeahbut yb < build_db.sql

-- This is HIGHLY DESTRUCTIVE!
drop table if exists globals;
drop table if exists user;
drop table if exists post;
drop table if exists post_content;
drop table if exists vote;
drop table if exists cluster;
drop table if exists cluster_connection;
drop table if exists ticket;
drop table if exists relevance;
drop table if exists callout_votes;
drop table if exists history;

--todo: should we declare everything NOT NULL?

create table globals (
    active_cid integer     not null default 0
    ) engine=InnoDB;

create table user (
    id serial              not null primary key,
    cid0 integer           not null references cluster,
    cid1 integer           not null references cluster,
    name varchar(32)       not null,
    password varchar(64)   not null,
    email varchar(64)      not null,
    date_joined timestamp  not null default now(),
    current_batch integer  not null,
    constraint name_unique unique(name),
    constraint email_unique unique(email)
    ) engine=InnoDB;  
--we use InnoDB so we can have transactions
--InnoDB uses fsync a lot, so reiserfs will likely be faster than ext3

create table ticket (
    uid integer            not null references user,
    ticket text            not null,
    last_used timestamp    not null default now()
    ) engine=InnoDB;

create table post (
    id serial              not null primary key,
    uid integer            not null references user,
    claim text             not null,
    broad_support double   not null,
    date_posted timestamp  not null default now(),
    callout_start integer  default null,
    callout_len integer    default null
    ) engine=InnoDB;

create table post_content (
    pid integer            not null references post,
    raw text               not null,
    safe_html text,
    tokens text
    ) engine=InnoDB;

create table vote (
    -- id serial primary key,
    uid integer            not null references user,
    pid integer            not null references post,
    date_voted timestamp   not null default now(),
    primary key(uid, pid)
    ) engine=InnoDB;

create table cluster (
    -- num_users is probably not null also
    id serial              not null primary key,
    num_users integer 
    ) engine=InnoDB;

create table cluster_connection (
    cid_from integer       not null references cluster,
    cid_to integer         not null references cluster,
    primary key(cid_from, cid_to)
    -- connection strength?
    ) engine=InnoDB;

create table relevance (
    term varchar(80),
    uid integer references user,
    pid integer references post
    ) engine=InnoDB;

create table callout_votes (
    pid integer references post,
    start_idx integer,
    end_idx integer,
    uid integer references user,
    primary key(pid, uid)
    ) engine=InnoDB;

create table history (
    uid integer references user,
    pid integer references post,
    -- date_viewed timestamp default now(),
    position integer,
    batch integer,
    primary key(uid, pid)
    ) engine=InnoDB;
