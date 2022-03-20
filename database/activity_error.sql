drop database if exists data_logging; 
create database data_logging; 

use data_logging; 

-- Table 1
drop table if exists activity; 
create table activity(
    activity_id int not null auto_increment,
    date_time datetime DEFAULT CURRENT_TIMESTAMP, 
    activity_discription varchar(1023), 
    is_error boolean, 

    constraint activity_pk primary key (activity_id)
);


-- Table 2
drop table if exists error; 
create table error(
    error_id int not null,
    error_message varchar(1023), 
    constraint error_pk primary key (error_id), 
    constraint error_fk1 foreign key (error_id) references activity(activity_id)
); 