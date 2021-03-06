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
DROP TABLE bestof CASCADE;

--all dates and times are local, which is the default of both Python
--and PostgreSQL

CREATE TABLE globals (
    active_cid integer     NOT NULL DEFAULT 0
    );

CREATE TABLE cluster (
    id serial              PRIMARY KEY,
    num_users integer      NOT NULL DEFAULT 0
    );

CREATE TABLE cluster_connection (
    cid_from integer       NOT NULL REFERENCES cluster,
    cid_to integer         NOT NULL REFERENCES cluster,
    PRIMARY KEY(cid_from, cid_to)
    -- connection strength?
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
CREATE INDEX ticket_idx ON ticket(uid);

CREATE TABLE post (
    id serial              PRIMARY KEY,
    uid integer            NOT NULL REFERENCES usr,
    claim text             NOT NULL,
    published boolean      NOT NULL DEFAULT FALSE,
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
CREATE INDEX post_content_idx ON post_content(pid);

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

CREATE TABLE relevance (
    term varchar(80)       NOT NULL,
    uid integer            NOT NULL REFERENCES usr,
    pid integer            NOT NULL REFERENCES post
    );
CREATE INDEX relevance_term ON relevance(term);
CREATE INDEX relevance_term ON relevance(uid);

CREATE TABLE history (
    uid integer            NOT NULL REFERENCES usr,
    pid integer            NOT NULL REFERENCES post,
    -- date_viewed timestamp NOT NULL DEFAULT now(),
    position integer       NOT NULL,
    batch integer          NOT NULL,
    PRIMARY KEY(uid, pid)
    );
CREATE INDEX history_idx ON history(uid, pid);

CREATE TABLE bestof (
    pos serial             PRIMARY KEY,
    pid integer            NOT NULL REFERENCES usr,
    date_promoted timestamp NOT NULL DEFAULT now()
    );
CREATE INDEX bestof_date ON bestof(date_promoted);

--based on http://archives.postgresql.org/pgsql-general/2007-08/msg00702.php
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
