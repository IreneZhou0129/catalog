# Catalog Project
## Installaiton
* Environement Setup
    * After access the vagrant VM with `vagrant ssh`. Simply run `pip install -r requirements.txt`

## Build
* Run `python models.py` to setup all of the tables
* Run `python taser.py` to inserting dummy data to the tables 

* Run `python model.py` to run the server visit `localhost:8000` to access the webpage

## Solutions

* API endpoints for JSON enter `http://localhost:8000/$(table_name)_json` would obtain the jsonify result 
    * IE: visit webpage with `http://localhost:8000/category_json`     
        ```json 
            {
            "Categories": [
                {
                "id": 1, 
                "name": "Dining Room", 
                "user_id": 1
                }, 
                {
                "id": 2, 
                "name": "Bath Room", 
                "user_id": 2
                }, 
                {
                "id": 3, 
                "name": "how ", 
                "user_id": 3
                }
            ]
            }
        ```
* All RESTful API are specific written in `actionModelName` in `application.py`


    


