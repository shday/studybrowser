# Animal Study Browser

## About this app
This app displays the results of a study comparing several treatment 
groups and optionally calculates p-values. Data from one or more
studies are loaded from a csv file containing the following 
column headers (case sensitive):

* study_id
* group_id
* group_type
* reading_value

The file should have one row for each subject. If a group has
group_type "control", it will be compared to the other groups using a t-test.
The group_type "reference" will suppress this calculation. 

The app will also recognize the following columns, providing
some enhanced functionality:

* subject_id - displayed on hover-over of data points
* test_article - displayed in the study selection drop-down
* group_name - replaces group_id on the x-axis
* reading_name - y-axis title 


### Animal Studies in drug discovery


## How to run this app

(The following instructions apply to Posix/bash. Windows users should check
[here](https://docs.python.org/3/library/venv.html).)

First, clone this repository and open a terminal inside the root folder.

Create and activate a new virtual environment (recommended) by running
the following:

```bash

python3 -m venv myvenv

source myvenv/bin/activate

```

Install the requirements:

```bash
pip install -r requirements.txt
```
Run the app:

```bash
python app.py
```
Open a browser at http://127.0.0.1:8050

## Screenshots

