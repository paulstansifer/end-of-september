-- Table creation script for the YeabBut database.
-- > psql yb -U yb -f build_db.sql

-- This is HIGHLY DESTRUCTIVE!
DROP TABLE globals CASCADE;
DROP TABLE usr CASCADE;
DROP TABLE post CASCADE;
DROP TABLE post_content CASCADE;
DROP TABLE vote CASCADE;
DROP TABLE cluster CASCADE;
DROP TABLE cluster_connection CASCADE;
DROP TABLE ticket CASCADE;
DROP TABLE relevance CASCADE;
DROP TABLE quote CASCADE;
DROP TABLE history CASCADE;

CREATE TABLE globals (
    active_cid integer     NOT NULL DEFAULT 0
    );

CREATE TABLE cluster (
    id serial              PRIMARY KEY,
    num_users integer      NOT NULL DEFAULT 0
    );

CREATE TABLE usr (
    id serial              PRIMARY KEY,
    cid0 integer           NOT NULL REFERENCES cluster,
    cid1 integer           NOT NULL REFERENCES cluster,
    name varchar(32)       NOT NULL,
    password varchar(64)   NOT NULL,
    email varchar(64)      NOT NULL,
    date_joined timestamp  NOT NULL DEFAULT now(),
    latest_batch integer   NOT NULL,
    constraint name_unique unique(name),
    constraint email_unique unique(email)
    );

CREATE TABLE ticket (
    uid integer            NOT NULL REFERENCES usr,
    ticket text            NOT NULL,
    last_used timestamp    NOT NULL DEFAULT now()
    );

CREATE TABLE post (
    id serial              PRIMARY KEY,
    uid integer            NOT NULL REFERENCES usr,
    claim text             NOT NULL,
    broad_support real     NOT NULL,
    date_posted timestamp  NOT NULL DEFAULT now(),
    callout_start integer  DEFAULT NULL,
    callout_len integer    DEFAULT NULL
    );

CREATE TABLE post_content (
    pid integer            NOT NULL REFERENCES post,
    raw text               NOT NULL,
    rendered text
    );

--just add things to this, and PostgreSQL will update the counts
CREATE TABLE quote (
    id serial              PRIMARY KEY,
    pid integer            NOT NULL REFERENCES post,
    start_idx integer      NOT NULL,
    end_idx integer        NOT NULL,
    votes_for integer      NOT NULL DEFAULT 1
    );

CREATE TABLE vote (
    -- id serial PRIMARY KEY,
    uid integer            NOT NULL REFERENCES usr,
    pid integer            NOT NULL REFERENCES post,
    date_voted timestamp   NOT NULL DEFAULT now(),
    qid integer            DEFAULT NULL REFERENCES quote,
    PRIMARY KEY(uid, pid)
    );

CREATE TABLE cluster_connection (
    cid_from integer       NOT NULL REFERENCES cluster,
    cid_to integer         NOT NULL REFERENCES cluster,
    PRIMARY KEY(cid_from, cid_to)
    -- connection strength?
    );

CREATE TABLE relevance (
    term varchar(80)       NOT NULL,
    uid integer            NOT NULL REFERENCES usr,
    pid integer            NOT NULL REFERENCES post
    );


CREATE TABLE history (
    uid integer            NOT NULL REFERENCES usr,
    pid integer            NOT NULL REFERENCES post,
    -- date_viewed timestamp NOT NULL DEFAULT now(),
    position integer       NOT NULL,
    batch integer          NOT NULL,
    PRIMARY KEY(uid, pid)
    );


--http://archives.postgresql.org/pgsql-general/2007-08/msg00702.php
CREATE RULE "replace_quote" AS
  ON INSERT TO "quote"
  WHERE
    EXISTS(
      SELECT 1 FROM quote 
        WHERE pid=NEW.pid and
              start_idx=NEW.start_idx and
              end_idx=NEW.end_idx)
  DO INSTEAD(
     UPDATE quote SET votes_for=votes_for+1
       WHERE pid=NEW.pid and
             start_idx=NEW.start_idx and
             end_idx=NEW.end_idx)
