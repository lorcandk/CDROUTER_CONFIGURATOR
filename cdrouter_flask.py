from flask import Flask, render_template, request
import pandas as pd
import sys
import time
from datetime import date
from cdrouter import CDRouter
from cdrouter.configs import Testvar
from cdrouter.configs import Config
from cdrouter.jobs import Job

# get the DUT parameters from the csv file
DUT_parameters = pd.read_csv('DUT_parameters.csv')
DUT_parameters_indexed = DUT_parameters.set_index('DUT')

# Define a dict to store the options

# create the web page
app = Flask(__name__)

options = { "DUT": {"1": "DUT1", "2": "DUT2", "3": "DUT3", "4": "DUT4"},
            "WAN Type": {"1": "VDSL", "2": "GE-WAN"},
            "WAN Mode": {"1": "DHCP", "2": "PPPoE"},
            "Topology": {"1": "GATEWAY", "2": "MESH"},
              "Reboot": {"1": "Yes", "2": "No"},
             "Clients": {"1": "LAN", "2": "WLAN(.11ac)", "3": "WLAN(.11ax)", "4": "MULTI"},
                "IPv6": {"1": "yes", "2": "no"} }

        
@app.route('/cdrouter_configurator', methods=['GET', 'POST'])
def cdrouter_configurator():
    if request.method == 'POST' :
        return request.form
    else:
        return render_template('cdrouter_configurator.html', options=options)


app.run(debug=True, port=5000, host='0.0.0.0')



