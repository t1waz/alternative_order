ALTERNATIVE STATION
===================

App purpose's to send barcode scans from production to alternative 
backend system. App operate on working stations present on each 
production step.

How to setup
------------

Install project venv:
        python3.6 -m venv .venv

Activate venv env:
        source .venv/bin/activate

Install Kivy:
	sudo add-apt-repository ppa:kivy-team/kivy

	sudo apt-get install python3-kivy

Install packages:
	pip install -r requirements.txt

Run project:
	cd alternative_station/

	sudo python main.py
