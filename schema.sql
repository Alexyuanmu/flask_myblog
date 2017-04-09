create table if not exists blogs(
	id integer primary key autoincrement,
	username text not null,
	title text not null,
	content text not null
);

create table if not exists users(
	id integer primary key autoincrement,
	username text not null unique,
	passwd text not null
);
