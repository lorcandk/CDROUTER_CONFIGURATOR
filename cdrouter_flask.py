from flask import Flask, render_template, request
from flask_basicauth import BasicAuth
import pandas as pd
import sys
import time
from datetime import date
from cdrouter import CDRouter
from cdrouter.configs import Testvar
from cdrouter.configs import Config
from cdrouter.jobs import Job
from cdrouter.devices import Device
from cdrouter.packages import Package

# get the DUT parameters from the csv file
DUT_parameters = pd.read_csv('~/CDROUTER_CONFIGURATOR/cdrouter_DUT.csv')
DUT_parameters_indexed = DUT_parameters.set_index('DUT')
# create the web page
app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'bblab'
app.config['BASIC_AUTH_PASSWORD'] = 'e1rc0mbblab'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

# Define a dict to store the options
options = { "DUT": {"1": "DUT1", "2": "DUT2", "3": "DUT3", "4": "DUT4", "5": "DUT5", "6": "DUT6"},
            "WAN Type": {"1": "VDSL", "2": "GE-WAN"},
            "WAN Mode": {"1": "DHCP", "2": "PPPoE"},
            "Topology": {"1": "GATEWAY", "2": "MESH"},
              "Reboot": {"1": "Yes", "2": "No"},
              "TR-069": {"1": "No", "2": "Yes"},
             "Clients": {"1": "LAN", "2": "WLAN(.11ac)", "3": "WLAN(.11ax)", "4": "MULTI"},
                "IPv6": {"1": "yes", "2": "no"} }

# Define a dict for the testvars
testvars = {
    "lan.lanClients":       "",
    "lan.lanInterface":     "",
    "lan.lanSSID":          "",
    "lan.lanSecurity":      "",
    "lan2.lanSecurity":     "",
    "lan3.lanSecurity":     "",
    "lan.wpaKey":           "",
    "lan.lanChannel":       "",
    "lan2.lanBSSID":        "",
    "lan2.lanChannel":      "",
    "lan2.lanClients":      "",
    "lan2.lanInterface":    "",
    "lan2.lanSSID":         "",
    "lan2.wpaKey":          "",
    "lan2.lanChannel":      "",
    "lan3.lanBSSID":        "",
    "lan3.lanChannel":      "",
    "lan3.lanClients":      "",
    "lan3.lanInterface":    "",
    "lan3.lanSSID":         "",
    "lan3.wpaKey":          "",
    "lan3.lanChannel":      "",
    "pppoeUser":            "",
    "pppoePassword":        "",
    "RestartDut":           "",
    "RestartDutDelay":      "",
    "testvar_group.lan2":   "",
    "testvar_group.lan3":   "",
    "wanInterface":         "",
    "wanMode":              "",
    "wanVlanId":            "",
    "supportsIPv6":         "",
    "supportsCWMP":         "",
    "acsDefaultUser":       ""
        }


@app.route('/cdrouter_configurator', methods=['GET', 'POST'])
@basic_auth.required
def cdrouter_configurator():
    if request.method == 'POST' :
        selected_options=request.form

# Get the DUT parameters
        DUT =selected_options["DUT"]
        DUT_dict = DUT_parameters_indexed.loc[:, DUT].to_dict()
#        print(DUT_dict)
# set testvars for the DUT
#        testvars["RestartDut"] = "/home/qacafe/powercycle.tcl 192.168.200.210 " + DUT_dict["PDU"] + " cyber cyber"
        testvars["lan.lanInterface"] = DUT_dict["LAN"]
        testvars["lan2.lanSSID"] = DUT_dict["SSID-5G"]
        testvars["lan.wpaKey"] = DUT_dict["WPA"]
        testvars["lan2.lanBSSID"] = DUT_dict["AP-MAC-5G"]
        testvars["lan2.wpaKey"] = DUT_dict["WPA"]
        testvars["lan3.lanBSSID"] = DUT_dict["AP-MAC-2G"]
        testvars["lan3.lanSSID"] = DUT_dict["SSID-2G"]
        testvars["lan3.wpaKey"] = DUT_dict["WPA"]
        testvars["lan3.lanChannel"] = DUT_dict["WPA"]
        testvars["wanVlanId"] = DUT_dict["VLAN"]
        testvars["acsDefaultUser"] = "8020DA-" + str(DUT_dict["GW-SERIAL"])

# set testvars for the WAN Type
        WAN_Type = selected_options["WAN Type"]

        if WAN_Type == "VDSL":
            testvars["wanInterface"] = "eth5"
            # shutdown all CPE and start the DUT and DSLAM
            testvars["RestartDut"] = "/home/qacafe/powercycle_VDSL.tcl 192.168.200.210 " + DUT_dict["PDU"] + " cyber cyber"
            testvars["RestartDutDelay"] = 180
            testvars["wanVlanId"] = 1000
        elif WAN_Type == "GE-WAN":
            testvars["wanInterface"] = DUT_dict["GE-WAN"]
            # shutdown all CPE and DSLAM and start the DUT
            testvars["RestartDut"] = "/home/qacafe/powercycle_GE-WAN.tcl 192.168.200.210 " + DUT_dict["PDU"] + " cyber cyber"
            testvars["RestartDutDelay"] = 60
            testvars["wanVlanId"] = 10
        else:
            print("ERROR")

# set testvars for WAN mode
        testvars["wanMode"] = selected_options["WAN Mode"]

# set testvars for CWMP
        testvars["supportsCWMP"] = selected_options["TR-069"]

# set testvars for IPv6
        testvars["supportsIPv6"] = selected_options["IPv6"]

# set testvars for reboot
        Reboot = selected_options["Reboot"]

        if Reboot == "No":
            testvars["RestartDut"] = ""

#set testvar for number of clients
        Clients = selected_options["Clients"]
        if Clients == "LAN":
            testvars["lan.lanClients"] = "1"
            testvars["lan.lanSecurity"] = "NONE"
            testvars["lan2.lanInterface"] = "none"
            testvars["lan3.lanInterface"] = "none"
        elif Clients == "WLAN(.11ac)":
            testvars["lan.lanInterface"] = "wifi0-acn"
            testvars["lan.lanChannel"] = "auto"
            testvars["lan.lanClients"] = "1"
            testvars["lan.lanSSID"] = DUT_dict["SSID-5G"]
            testvars["lan.wpaKey"] = DUT_dict["WPA"]
            testvars["lan.lanSecurity"] = "WPA"
            testvars["lan2.lanInterface"] = "none"
            testvars["lan3.lanInterface"] = "none"
        elif Clients == "WLAN(.11ax)":
            testvars["lan.lanInterface"] = "wifi1-ax"
            testvars["lan.lanChannel"] = "auto"
            testvars["lan.lanClients"] = "1"
            testvars["lan.lanSSID"] = DUT_dict["SSID-5G"]
            testvars["lan.wpaKey"] = DUT_dict["WPA"]
            testvars["lan.lanSecurity"] = "WPA"
            testvars["lan2.lanInterface"] = "none"
            testvars["lan3.lanInterface"] = "none"
        elif Clients == "MULTI":
            testvars["lan.lanInterface"] = DUT_dict["LAN"]
            testvars["lan.lanSecurity"] = "NONE"
            testvars["lan2.lanInterface"] = "wifi0-acn"
            testvars["lan3.lanInterface"] = "wifi1-ax"
            testvars["lan2.lanClients"] = "32"
            testvars["lan3.lanClients"] = "1"
            testvars["lan2.lanChannel"] = "5GHz"
            testvars["lan3.lanChannel"] = "2.4GHz"
            testvars["lan2.lanSSID"] = DUT_dict["SSID-5G"]
            testvars["lan3.lanSSID"] = DUT_dict["SSID-2G"]
            testvars["lan2.wpaKey"] = DUT_dict["WPA"]
            testvars["lan3.wpaKey"] = DUT_dict["WPA"]
            testvars["lan2.lanSecurity"] = "WPA"
            testvars["lan3.lanSecurity"] = "WPA"

# generate config name
        config_name = "Python:"
        config_name = config_name + DUT_dict['DESCRIPTION'] + "_" + DUT_dict['GW-FIRMWARE'] + "_"
        config_name = config_name + selected_options['WAN Type'] + "_"
        config_name = config_name + selected_options['WAN Mode'] + "_"
        config_name = config_name + selected_options['Topology'] + "_"
        config_name = config_name + selected_options['Clients']
        if selected_options['IPv6'] == "yes":
            config_name = config_name + "_IPv6"
        if selected_options['TR-069'] == "yes":
            config_name = config_name + "_CWMP"
        if selected_options['Reboot'] == "No":
            config_name = config_name + " (NO REBOOT)"
        if len(selected_options['notes']) > 0:
            config_name = config_name + " " + selected_options['notes']
        print(f"Config {config_name}")

# connect to CDRouter

        base = sys.argv[1]
        token = sys.argv[2]

        print(f"Opening connection to CDRouter {base} with token {token}...")

        c = CDRouter(base, token=token)
# get default config
        cfg_default = c.configs.get(1072)
#update config notes
        print(f"Updating notes in {cfg_default.name} ...")
        config_notes = cfg_default.note
        config_notes = config_name + " - " + str(date.today()) + "\n" + config_notes
        c.configs.edit(Config(id='1072', note=config_notes))

# create device
        dut_name = DUT_dict['GW-VENDOR'] + "_" + DUT_dict["GW-MODEL"] + "_" + DUT_dict["GW-FIRMWARE"]
        if selected_options['Topology'] == "MESH":
            dut_name = dut_name + "_" + DUT_dict["AP-MODEL"] + "_" + DUT_dict["AP-FIRMWARE"]

        try:
            dut_device = c.devices.get_by_name(dut_name)
            if dut_device is not None:
                print(f"Device {dut_name} exists.")
        except:
            dut_device = c.devices.create(Device(name=dut_name))
            print(f"Device {dut_name} created.")

# update testvar
        print("Updating testvars...")
        c.configs.edit_testvar("1072", Testvar(name='wanInterface', value=testvars['wanInterface']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='wanMode', value=testvars['wanMode']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='RestartDut', value=testvars['RestartDut']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='supportsIPv6', value=testvars['supportsIPv6']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='lanInterface', value=testvars['lan.lanInterface']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='lanSSID', value=testvars['lan.lanSSID']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='wpaKey', value=testvars['lan.wpaKey']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='lanSSID', group='lan2', value=testvars['lan2.lanSSID']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='lanSSID', group='lan3', value=testvars['lan3.lanSSID']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='wpaKey', group='lan2', value=testvars['lan2.wpaKey']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='wpaKey', group='lan3', value=testvars['lan2.wpaKey']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='lanClients', group='lan2', value=testvars['lan2.lanClients']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='lanInterface', group='lan2', value=testvars['lan2.lanInterface']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='lanInterface', group='lan3', value=testvars['lan3.lanInterface']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='lanSecurity', group='main', value=testvars['lan.lanSecurity']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='lanSecurity', group='lan2', value=testvars['lan2.lanSecurity']))
        print("...working...")
        c.configs.edit_testvar("1072", Testvar(name='lanSecurity', group='lan3', value=testvars['lan3.lanSecurity']))

        print("Finished updating testvars.")

### set package associated device name        
        pkg = c.packages.get(1056)
#        pkg_device_id = c.devices.get(pkg.device_id)
#        print(f"Package current device id: {pkg.device_id}")
#        pkg_dvc = c.devices.get(pkg.device_id)
#        print(f"Package current device name: {pkg_dvc.name}")
 #      dvc = c.devices.get_by_name(device_name)
        print(f"DUT Device id: {dut_device.id}")
        print(f"DUT Device name: {dut_device.name}")

        pkg_base = c.packages.get(808)
        print(f"Base test package has {pkg_base.test_count} tests")
 #       print(f"{pkg_base.testlist}")
        tl_base = pkg_base.testlist 

        pkg_sec = c.packages.get(825)
        print(f"Security test package has {pkg_sec.test_count} tests")
#        print(f"{pkg_sec.testlist}")
        tl_sec = pkg_sec.testlist 

        tl = tl_base + tl_sec

        print(f"Updating package {pkg.name} with device {dut_device.name} and adding testlists...")
        c.packages.edit(Package(id='1056', device_id=dut_device.id, testlist=tl))
        print('Checking config for errors...')
        check = c.configs.check_config(cfg_default.contents)
        if len(check.errors) > 0:
            print('config errors:'.format(pkg.name))
            for e in check.errors:
                print('        {0}'.format(e.error))
                print('')
                continue
        print(f"Launching package {pkg.name} with associated device {dut_device.name}...")
        j = c.jobs.launch(Job(package_id='1056'))

# working for job to be assigned a result ID
        print("Running startup procedure. This may take a few minutes...")
        while j.result_id is None:
            time.sleep(1)
            j = c.jobs.get(j.id)

        print('        Result-ID: {0}'.format(j.result_id))
        print('')
        print(f"Package {pkg.name} launched!")

        return f"Launched package {pkg.name} with config {config_name}"

    else:
        return render_template('cdrouter_configurator.html', options=options)

app.run(debug=True, port=5000, host='0.0.0.0')



