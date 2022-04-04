# ESD-G1T3-Camera-Rental-Platform
The group project by IS213 Enterprise Solution G1 Team 3

### Description



### Instructions 
_The following assumes you are a Windows User_

1. Start WAMP and Docker 

2. Create MYSQL tables with all files in **database** folder
    * From phpMyAdmin > Click “home” icon > tab “Import” 
    * Choose File > `user_listing_database.sql`
    * Click “Go”
    * Repeat for `activity_error.sql`, before doing the same for `mock_data.sql`

3. Install `requirements.txt` in **userview** folder
    * Enter the command `pip install -r requirements.txt`

4. Run `userview.py` 
    * Execute the command `python userview.py` in CMD
    * Make sure you are executing in the correct directory e.g. C:\ESD\ESD-G1T3-Camera-Rental-Platform\view

5. Open `docker-compose.yml` file, replace all the _dockerid_ with your own 

6. In a CMD window, run the following command:
    * `docker-compose up`
    * Ensure your directory points to the folder containing `docker-compose.yml` 




_Special Note_
* The trial account of Twillio only allows one phone number to be linked to receive the SMS
* Please Log In using **only** the following:
* email: ningzhi.ma.2018@scis.smu.edu.sg
* pw: ningzhi
