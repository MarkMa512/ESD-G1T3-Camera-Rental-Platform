drop database if exists user_listing; 
create database user_listing; 

use user_listing; 

-- Table 1 : USER_INFO
drop table if exists user_info; 
-- create table user_info(
--     user_id int not null auto_increment,
--     user_name varchar(255),
--     phone int, 
--     email varchar(255), 
--     residential_address varchar(255),  

--     constraint user_info_pk primary key (user_id)
-- );

-- Table 2 : LISTING
drop table if exists listing; 
create table listing(
    listing_id int not null auto_increment,
    owner_id varchar(255), 
    brand varchar(255),
    model varchar(255),
    price double,
    image_url varchar(255), 
    availabiltity int not null,
    listing_description varchar(1023), 
    daily_rate double, 
    
    constraint listing_pk primary key (listing_id)
    -- constraint listing_fk1 foreign key (owner_id) references user_info(user_id)
); 

-- Table 3 : RENTAL 
drop table if exists rental; 
create table rental(
    rental_id int not null auto_increment, 
    listing_id int not null,
    owner_id varchar(255),
    renter_id varchar(255),
    rent_start_date date, 
    rent_end_date date,  
    total_price double,  
    rental_status varchar(255), -- approved, delivered/recieved, returned  

    constraint rental_pk primary key (rental_id), 
    -- constraint rental_fk1 foreign key (owner_id) references user_info(user_id), 
    -- constraint rental_fk2 foreign key (renter_id) references user_info(user_id),
    constraint rental_fk3 foreign key (listing_id) references listing(listing_id)
);