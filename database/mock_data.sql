use user_listing

INSERT INTO `listing` (`listing_id`, `owner_id`, `brand`, `model`, `price`, `image_url`, `availabiltity`, `listing_description`, `daily_rate`) VALUES
(1, 1, 'Canon', 'Canon EOS 2000D DSLR Camera and EF-S 18-55 mm f/3.5-5.6 is II Lens, Black', 626, 'https://m.media-amazon.com/images/I/613WC3OoLFL._AC_SX679_.jpg', 1, '1 Lithium ion batteries required', 25),
(2, 2, 'Nikkon', 'Z 5 w/NIKKOR Z 24-50mm f/4-6.3', 1600, 'https://m.media-amazon.com/images/I/91wH3EeK7XL._AC_SX679_.jpg', 1, 'Includes the ultra-compact NIKKOR Z 24-50mm f/4-6. 3 standard zoom lens', 15),
(3, 3, 'Fujifilm', 'Fujifilm X-S10 Mirrorless Camera Body- Black, X-S10 Body- Black', 999, 'https://m.media-amazon.com/images/I/81HWDUTDpvL._AC_SX679_.jpg', 1, 'It’s All About How It Feels: X-S10 has been designed to provide on-the-go photographers with maximum control. Its deep handgrip affords solid, confident handling with any kind of lens attached, while the intuitive controls ensure effortless operation, no matter what camera system you are used to. When you also consider the 180° vari-angle LCD touchscreen and up to 20fps uncropped continuous shooting, with X-S10 you will be ready to unleash Fujifilm’s acclaimed color science for any and every photo opportunity.', 15);


INSERT INTO `user_info` (`user_id`, `user_name`, `phone`, `email`, `residential_address`) VALUES
(1, 'John', 90218888, 'John@gmail.com', 'Ang Mo Kio Ave 5'),
(2, 'Paul', 90218887, 'Paul@gmail.com', 'Jurong East Ave 2'),
(3, 'Ben', 90218886, 'Ben@gmail.com', 'Bishan Ave 5'),
(4, 'Ken', 90218885, 'Ken@gmail.com', 'Tampines Ave 9'),
(5, 'Noah', 90218884, 'Noah@gmail.com', 'Hougang Ave 8');
