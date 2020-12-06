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
  address   VARCHAR(1024)  NOT NULL,
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
  url       VARCHAR(1024)  NOT NULL,
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
