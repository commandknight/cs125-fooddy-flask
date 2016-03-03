drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);
DROP TABLE IF EXISTS UserProfile;
CREATE TABLE IF NOT EXISTS UserProfile(
  user_id INTEGER PRIMARY KEY AUTOINCREMENT ,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL
);
DROP TABLE IF EXISTS UserWeights;
CREATE TABLE IF NOT EXISTS UserWeights(
  user_id INTEGER,
  category_id INTEGER,
  weight DOUBLE NOT NULL,
  FOREIGN KEY (user_id) REFERENCES UserProfile(user_id),
  FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);
DROP TABLE IF EXISTS Categories;
CREATE TABLE IF NOT EXISTS Categories(
  category_id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_name TEXT NOT NULL,
  category_alias TEXT NOT NULL
);