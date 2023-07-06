# CDROUTER_CONFIGURATOR

This is a configurator tool for CDRouter

To start with web front end:
python ~/cdrouter_flask.py

To use, browse to:
#ldkcloud.ddns.net:5000/CDROUTER_CONFIGURATOR
broadbandlab.ddns.net:5000/CDROUTER_CONFIGURATOR

Select DUT# for the specific device under test.
Data source for DUT parameters is cdrouter_DUT.csv

Select other test options.
Submit.

App will open a connection to CDRouter and generate a Config and Device ID based on the input test options. Then it will run the test package "Python Base".

