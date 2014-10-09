-- id	The item's unique id. Required.
-- deleted	true if the item is deleted.
-- type	The type of item. One of "job", "story", "comment", "poll", or "pollopt".
-- by	The username of the item's author.
-- time	Creation date of the item, in Unix Time.
-- text	The comment, Ask HN, or poll text. HTML.
-- dead	true if the item is dead.
-- parent	The item's parent. For comments, either another comment or the relevant story. For pollopts, the relevant poll.
-- kids	The ids of the item's comments, in ranked display order.
-- url	The URL of the story.
-- score	The story's score, or the votes for a pollopt.
-- title	The title of the story or poll.
-- parts	A list of related pollopts, in display order.

CREATE TABLE items (
    id      integer PRIMARY KEY,
    deleted boolean,
    type    varchar(40),
    by      varchar(30),
    time    timestamp,
    text    text,
    dead    boolean,
    parent  integer,
    url     varchar(500),
    score   integer,
    title   varchar(400)
);
