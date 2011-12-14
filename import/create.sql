create table Work (
       ID varchar(512) not null,
       Title varchar(512) not null,
       Year integer not null,
       Note integer,
       primary key (ID)
);

create table Movie (
       ID varchar(512) not null,
       primary key (ID),
       foreign key (ID) references Work(ID)
);

create table Serie (
       ID varchar(512) not null,
       EndYear integer,
       primary key (ID),
       foreign key (ID) references Work(ID)
);

create table Episode (
       ID varchar(512) not null,
       Season integer,
       EpisodeNum integer,
       Date integer,
       EpisodeTitle varchar(512),
       SID varchar(512) not null,
       primary key (ID),
       foreign key (ID) references Work(ID)
       foreign key (SID) references Serie(ID)
);

create table Genre (
       ID varchar(512) not null ,
       Genre varchar(64) not null,
       primary key (ID, Genre),
       foreign key (ID) references Work(ID)
);

create table Country (
       ID varchar(512) not null,
       Country varchar(64) not null,
       primary key (ID, Country),
       foreign key (ID) references Work(ID)
);

create table Language (
       ID varchar(512) not null,
       Language varchar(64) not null,
       primary key (ID, Language),
       foreign key (ID) references Work(ID)
);

create table Person (
       FirstName varchar(512) not null,
       LastName varchar(512) not null,
       Num integer not null,
       Gender char(1),
       primary key (FirstName, LastName, Num)
);

create table Actor (
       FirstName varchar(256) not null,
       LastName varchar(256) not null,
       Num varchar(16) not null,
       ID varchar(512) not null,
       Role varchar(512) not null,
       primary key (FirstName, LastName, Num, ID, Role),
       foreign key (FirstName, LastName, Num) references Person(FirstName, LastName, Num),
       foreign key (ID) references Work(ID)
);

create table Writer (
       FirstName varchar(256) not null,
       LastName varchar(256) not null,
       Num varchar(16) not null,
       ID varchar(512) not null,
       primary key (FirstName, LastName, Num, ID),
       foreign key (FirstName, LastName, Num) references Person(FirstName, LastName, Num),
       foreign key (ID) references Work(ID)
);

create table Director (
       FirstName varchar(256) not null,
       LastName varchar(256) not null,
       Num varchar(16) not null,
       ID varchar(512) not null,
       primary key (FirstName, LastName, Num, ID),
       foreign key (FirstName, LastName, Num) references Person(FirstName, LastName, Num),
       foreign key (ID) references Work(ID)
);

create table Admin (
       Mail varchar(256) not null,
       Pass char(65) not null, -- The SHA256-sum of the pass
       primary key (Mail)
);

create table Votes (
      ID varchar(512) not null,
      Up integer not null,
      Down integer not null,
      primary key (ID),
      foreign key (ID) references Work(ID)
);
