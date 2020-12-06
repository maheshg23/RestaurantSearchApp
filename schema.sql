DROP TABLE reviews;
DROP TABLE photos;
DROP TABLE restaurant_tags_mapping;
DROP TABLE restaurant_payments_mapping;
DROP TABLE restaurants;
DROP TABLE status;
DROP TABLE location;
DROP TABLE tags;
DROP TABLE users;
DROP TABLE payment_methods;

CREATE TABLE status (
  sid   INTEGER     PRIMARY KEY,
  name  VARCHAR(64) NOT NULL
);

CREATE TABLE location (
  lid   INTEGER			PRIMARY KEY,
  city  VARCHAR(64) 	NOT NULL,
  country VARCHAR(64)	NOT NULL,
  UNIQUE(city, country)
);

CREATE TABLE tags (
  tid   INTEGER     PRIMARY KEY,
  name  VARCHAR(64) NOT NULL
);

CREATE TABLE payment_methods (
  pmid  INTEGER     PRIMARY KEY,
  name  VARCHAR(64) NOT NULL
);

CREATE TABLE users (
  uid       INTEGER       PRIMARY KEY,
  name      VARCHAR(128)  NOT NULL,
  username  VARCHAR(64)   UNIQUE,
  password  VARCHAR(128)  NOT NULL
);

CREATE TABLE restaurants (
  id        INTEGER       PRIMARY KEY,
  name      VARCHAR(128)  NOT NULL,
  address   VARCHAR(128)  NOT NULL,
  phone     VARCHAR(32),
  website   VARCHAR(128),
  latitude  DECIMAL       NOT NULL,
  longitude DECIMAL       NOT NULL,
  status    INTEGER       NOT NULL,
  location  INTEGER       NOT NULL,
  owner_id  INTEGER,
  FOREIGN KEY (status) REFERENCES status (sid),
  FOREIGN KEY (location) REFERENCES location (lid),
  FOREIGN KEY (owner_id) REFERENCES users (uid) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE photos (
  pid       INTEGER       PRIMARY KEY,
  url       VARCHAR(512)  NOT NULL,
  timestamp TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
  user_id   INTEGER       NOT NULL,
  res_id    INTEGER       NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (res_id) REFERENCES restaurants (id)
);

CREATE TABLE reviews (
  rid        INTEGER         PRIMARY KEY,
  text      VARCHAR(1024),
  rating    INTEGER         NOT NULL,
  timestamp TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
  user_id   INTEGER         NOT NULL,
  res_id    INTEGER         NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (uid) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (res_id) REFERENCES restaurants (id)
);

CREATE TABLE restaurant_tags_mapping (
  res_id  INTEGER,
  tag_id  INTEGER,
  PRIMARY KEY (res_id, tag_id),
  FOREIGN KEY (res_id) REFERENCES restaurants (id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags (tid)
);

CREATE TABLE restaurant_Payments_Mapping (
  res_id  INTEGER,
  payment_id  INTEGER,
  PRIMARY KEY (res_id, payment_id),
  FOREIGN KEY (res_id) REFERENCES restaurants (id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (payment_id) REFERENCES payment_methods (pmid) 
);


INSERT INTO status VALUES (11,'Closed');
INSERT INTO status VALUES (12,'Open');

INSERT INTO location VALUES (21,'New York','USA');
INSERT INTO location VALUES (22,'SF','USA');
INSERT INTO location VALUES (23,'Seattle','USA');

INSERT INTO tags VALUES (31,'Indian');
INSERT INTO tags VALUES (32,'American');

INSERT INTO payment_methods VALUES (41,'Cash');
INSERT INTO payment_methods VALUES (42,'Debit Card');
INSERT INTO payment_methods VALUES (43,'Credit Card');

INSERT INTO users VALUES (51,'John','john123','password');
INSERT INTO users VALUES (52,'Mark','mark123','password');

INSERT INTO restaurants VALUES (101,'Burger King','5th Avenue','333-444-5555','burgerking.com',123123,123123,12,21,51);
INSERT INTO restaurants VALUES (102,'KFC','4th Avenue','333-444-6666','kfc.com',123124,123124,11,22,52);
INSERT INTO restaurants VALUES (103,'MCD','9th Avenue','333-444-7777','mcd.com',123125,123125,12,22,51);
INSERT INTO restaurants VALUES (104,'Dominos','10th Avenue','333-444-8888','dominos.com',28.6015914075,77.1860203519,11,22,51);
INSERT INTO restaurants VALUES (105,'Biryani Zone','54th Stret','333-444-9999','biryani.com',28.6015914075,77.1860203519,12,23,52);

INSERT INTO photos (pid, url, user_id, res_id) VALUES (201,'url',51,101);
INSERT INTO photos (pid, url, user_id, res_id) VALUES (202,'url',52,102);

INSERT INTO reviews (rid, text, rating, user_id, res_id) VALUES (301,'Good Restaurant',5,51,101);
INSERT INTO reviews (rid, text, rating, user_id, res_id) VALUES (302,'Good Restaurant',5,52,102);

INSERT INTO reviews (rid, text, rating, user_id, res_id) VALUES (303,'Good Restaurant',8,51,101);
INSERT INTO reviews (rid, text, rating, user_id, res_id) VALUES (304,'Good Restaurant',2,52,102);


INSERT INTO restaurant_tags_mapping VALUES (101,31);
INSERT INTO restaurant_tags_mapping VALUES (101,32);
INSERT INTO restaurant_tags_mapping VALUES (102,32);
INSERT INTO restaurant_tags_mapping VALUES (103,31);

INSERT INTO restaurant_Payments_Mapping VALUES (101,41);
INSERT INTO restaurant_Payments_Mapping VALUES (102,42);
INSERT INTO restaurant_Payments_Mapping VALUES (103,41);