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
            "Reboot": {"1": "yes", "2": "no", "3": "quick"},
              "TR-069": {"1": "no", "2": "yes"},
             "Clients": {"1": "LAN", "2": "WLAN(.11ac)", "3": "WLAN(.11ax)", "4": "MULTI"},
                "IPv6": {"1": "yes", "2": "no"}, 
                "Package": {"1": "Base", "2": "Sanity", "3": "Security", "4": "Performance/Stability", "5": "DOS", "6": "Performance", "7": "Mgmt: TR-069"} }
                
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
    "tr69DownloadImage":    "",
    "tr69DownloadOriginalImage":         "",
    "acsDefaultUser":       ""
        }


@app.route('/cdrouter_configurator', methods=['GET', 'POST'])
@basic_auth.required
def cdrouter_configurator_test():
    if request.method == 'POST' :
        selected_options=request.form

# Get the DUT parameters
        DUT =selected_options["DUT"]
        DUT_dict = DUT_parameters_indexed.loc[:, DUT].to_dict()
# set testvars for the DUT
        testvars["lan.lanInterface"] = DUT_dict["LAN"]
        testvars["lan.wpaKey"] = DUT_dict["WPA"]
        testvars["lan2.lanSSID"] = DUT_dict["SSID-5G"]
        testvars["lan2.wpaKey"] = DUT_dict["WPA"]
        testvars["lan3.lanSSID"] = DUT_dict["SSID-2G"]
        testvars["lan3.wpaKey"] = DUT_dict["WPA"]
        testvars["wanVlanId"] = DUT_dict["VLAN"]
        testvars["acsDefaultUser"] = DUT_dict["GW-OUI"] + "-" + DUT_dict["GW-SERIAL"]

#create tag list
        tag_list = list()
        tag_list.append("python")
        tag_list.append(DUT_dict["GW-NAME"])

# set testvars for the selected WAN Type
        WAN_Type = selected_options["WAN Type"]

        if WAN_Type == "VDSL":
            testvars["wanInterface"] = "eth5"
            # shutdown all CPE and the WAN switch and start the DUT and DSLAM
            testvars["RestartDut"] = "/home/qacafe/powercycle_VDSL.tcl 192.168.200.210 " + DUT_dict["PDU"] + " cyber cyber"
            testvars["RestartDutDelay"] = 180
            testvars["wanVlanId"] = 1000
            tag_list.append("VDSL")
        elif WAN_Type == "GE-WAN":
            testvars["wanInterface"] = DUT_dict["GE-WAN"]
            # shutdown all CPE and DSLAM and start the DUT and the WAN switch
            testvars["RestartDut"] = "/home/qacafe/powercycle_GE-WAN2.tcl 192.168.200.210 " + DUT_dict["PDU"] + " cyber cyber"
            testvars["RestartDutDelay"] = 90
            testvars["wanVlanId"] = 10
            tag_list.append("FTTH")
        else:
            print("ERROR")

# set testvars for the selected WAN mode
        testvars["wanMode"] = selected_options["WAN Mode"]
        tag_list.append(testvars["wanMode"])

# set testvars for CWMP
        tr69_option = selected_options["TR-069"]
        testvars["supportsCWMP"] = tr69_option

        if tr69_option == "yes":
            testvars["tr69DownloadImage"] = "/home/qacafe/" + DUT_dict["GW-FW-MIRROR"]
            testvars["tr69DownloadOriginalImage"] = "/home/qacafe/" + DUT_dict["GW-FW-IMAGE"]

# set testvars for IPv6
        testvars["supportsIPv6"] = selected_options["IPv6"]

# set testvars for reboot
        Reboot = selected_options["Reboot"]

        if Reboot == "no":
            testvars["RestartDut"] = ""
        elif Reboot == "quick":
            testvars["RestartDut"] = "/home/qacafe/powercycle_QUICK.tcl 192.168.200.210 " + DUT_dict["PDU"] + " cyber cyber"

#set testvar for number of clients
        Clients = selected_options["Clients"]
        if Clients == "LAN":
            testvars["lan.lanClients"] = "1"
            testvars["lan.lanSecurity"] = "NONE"
            testvars["lan2.lanInterface"] = "none"
            testvars["lan3.lanInterface"] = "none"
            tag_list.append("LAN")
        elif Clients == "WLAN(.11ac)":
            testvars["lan.lanInterface"] = "wifi0-acn"
            testvars["lan.lanChannel"] = "5GHz"
            testvars["lan.lanClients"] = "1"
            testvars["lan.lanSSID"] = DUT_dict["SSID-5G"]
            testvars["lan.wpaKey"] = DUT_dict["WPA"]
            testvars["lan.lanSecurity"] = "WPA"
            testvars["lan2.lanInterface"] = "none"
            testvars["lan3.lanInterface"] = "none"
            testvars["lan2.lanSecurity"] = "NONE"
            testvars["lan3.lanSecurity"] = "NONE"
            tag_list.append("WLAN")
        elif Clients == "WLAN(.11ax)":
            testvars["lan.lanInterface"] = "wifi1-ax"
            testvars["lan.lanChannel"] = "5GHz"
            testvars["lan.lanClients"] = "1"
            testvars["lan.lanSSID"] = DUT_dict["SSID-5G"]
            testvars["lan.wpaKey"] = DUT_dict["WPA"]
            testvars["lan.lanSecurity"] = "WPA"
            testvars["lan2.lanInterface"] = "none"
            testvars["lan3.lanInterface"] = "none"
            testvars["lan2.lanSecurity"] = "NONE"
            testvars["lan3.lanSecurity"] = "NONE"
            tag_list.append("WLAN")
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
            tag_list.append("LAN")
            tag_list.append("WLAN")

#set testvars for topology
        Topology = selected_options["Topology"]
        if Topology == "MESH":
            testvars["lan2.lanBSSID"] = DUT_dict["AP-MAC-5G"]
            testvars["lan3.lanBSSID"] = DUT_dict["AP-MAC-2G"]
            tag_list.append("MESH")
        elif Topology == "GATEWAY":
            testvars["lan2.lanBSSID"] = DUT_dict["GW-MAC-5G"]
            testvars["lan3.lanBSSID"] = DUT_dict["GW-MAC-2G"]

# generate config name
        config_name = "Python:"
        config_name = config_name + DUT_dict['GW-NAME'] + "_" + DUT_dict['GW-FIRMWARE'] + "_"
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

#update config tags
        print(f"Updating tags in config {cfg_default.name} ...")
        c.configs.edit(Config(id='1072', tags=tag_list))

# create device
        dut_name = DUT_dict['GW-VENDOR'] + "_" + DUT_dict["GW-MODEL"] + "_" + DUT_dict["GW-FIRMWARE"]
        dut_description = "Created by Python"
        if selected_options['Topology'] == "MESH":
            dut_name = dut_name + "_" + DUT_dict["AP-MODEL"] + "_" + DUT_dict["AP-FIRMWARE"]

        try:
            dut_device = c.devices.get_by_name(dut_name)
            if dut_device is not None:
                print(f"Device {dut_name} exists.")
        except:
            dut_device = c.devices.create(Device(name=dut_name, description=dut_description))
            print(f"Device {dut_name} created.")

# update testvar

        print("Updating testvars...")

        c.configs.edit_testvar("1072", Testvar(name='wanInterface', value=testvars['wanInterface']))
        print(f"...updated wanInterface {testvars['wanInterface']}...")

        c.configs.edit_testvar("1072", Testvar(name='wanMode', value=testvars['wanMode']))
        print(f"...updated wanMode {testvars['wanMode']}...")

        c.configs.edit_testvar("1072", Testvar(name='wanVlanId', value=testvars['wanVlanId']))
        print(f"...updated wanVlanId {testvars['wanVlanId']}...")

        c.configs.edit_testvar("1072", Testvar(name='RestartDutDelay', value=testvars['RestartDutDelay']))
        print(f"...updated RestartDutDelay {testvars['RestartDutDelay']}...")

        c.configs.edit_testvar("1072", Testvar(name='RestartDut', value=testvars['RestartDut']))
        print(f"...updated RestartDut {testvars['RestartDut']}...")

        c.configs.edit_testvar("1072", Testvar(name='supportsIPv6', value=testvars['supportsIPv6']))
        print(f"...updated supportsIPv6 {testvars['supportsIPv6']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanInterface', value=testvars['lan.lanInterface']))
        print(f"...updated lanInterface {testvars['lan.lanInterface']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanSSID', value=testvars['lan.lanSSID']))
        print(f"...updated lan.lanSSID {testvars['lan.lanSSID']}...")

        c.configs.edit_testvar("1072", Testvar(name='wpaKey', value=testvars['lan.wpaKey']))
        print(f"...updated wpaKey {testvars['lan.wpaKey']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanChannel', value=testvars['lan.lanChannel']))
        print(f"...updated lanChannel {testvars['lan.lanChannel']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanSSID', group='lan2', value=testvars['lan2.lanSSID']))
        print(f"...updated lan2.lanSSID {testvars['lan2.lanSSID']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanSSID', group='lan3', value=testvars['lan3.lanSSID']))
        print(f"...updated lan3.lanSSID {testvars['lan3.lanSSID']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanBSSID', group='lan2', value=testvars['lan2.lanBSSID']))
        print(f"...updated lan2.lanBSSID {testvars['lan2.lanBSSID']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanBSSID', group='lan3', value=testvars['lan3.lanBSSID']))
        print(f"...updated lan3.lanBSSID {testvars['lan3.lanBSSID']}...")

        c.configs.edit_testvar("1072", Testvar(name='wpaKey', group='lan2', value=testvars['lan2.wpaKey']))
        print(f"...updated lan2.wpaKey {testvars['lan2.wpaKey']}...")

        c.configs.edit_testvar("1072", Testvar(name='wpaKey', group='lan3', value=testvars['lan3.wpaKey']))
        print(f"...updated lan3.wpaKey {testvars['lan3.wpaKey']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanClients', group='lan2', value=testvars['lan2.lanClients']))
        print(f"...updated lan2.lanClients {testvars['lan2.lanClients']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanClients', group='lan3', value=testvars['lan3.lanClients']))
        print(f"...updated lan3.lanClients {testvars['lan3.lanClients']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanChannel', group='lan2', value=testvars['lan2.lanChannel']))
        print(f"...updated lan2.lanChannel {testvars['lan2.lanChannel']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanChannel', group='lan3', value=testvars['lan3.lanChannel']))
        print(f"...updated lan3.lanChannel {testvars['lan3.lanChannel']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanInterface', group='lan2', value=testvars['lan2.lanInterface']))
        print(f"...updated lan2.lanInterface {testvars['lan2.lanInterface']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanInterface', group='lan3', value=testvars['lan3.lanInterface']))
        print(f"...updated lan3.lanInterface {testvars['lan3.lanInterface']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanSecurity', group='main', value=testvars['lan.lanSecurity']))
        print(f"...updated lan.lanSecurity {testvars['lan.lanSecurity']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanSecurity', group='lan2', value=testvars['lan2.lanSecurity']))
        print(f"...updated lan2.lanSecurity {testvars['lan2.lanSecurity']}...")

        c.configs.edit_testvar("1072", Testvar(name='lanSecurity', group='lan3', value=testvars['lan3.lanSecurity']))
        print(f"...updated lan3.lanSecurity {testvars['lan3.lanSecurity']}...")

        c.configs.edit_testvar("1072", Testvar(name='tr69DownloadImage', value=testvars['tr69DownloadImage']))
        print(f"...updated tr69DownloadImage {testvars['tr69DownloadImage']}...")

        c.configs.edit_testvar("1072", Testvar(name='tr69DownloadOriginalImage', value=testvars['tr69DownloadOriginalImage']))
        print(f"...updated tr69DownloadOriginalImage {testvars['tr69DownloadOriginalImage']}...")

        c.configs.edit_testvar("1072", Testvar(name='supportsCWMP', value=testvars['supportsCWMP']))
        print(f"...updated supportsCWMP {testvars['supportsCWMP']}...")

        c.configs.edit_testvar("1072", Testvar(name='acsDefaultUser', value=testvars['acsDefaultUser']))
        print(f"...updated acsDefaultUser {testvars['acsDefaultUser']}...")

        print("Finished updating testvars.")


### set package associated device name        

        #pkg = c.packages.get(1056)
        #pkg = c.packages.get_by_name("Python Base")
#        pkg_name = selected_options["Package"] 
#        pkg = c.packages.get_by_name(pkg_name)
       # print(f"Got package name {pkg.name} with ID {pkg.id}")
#       # pkg_device_id = c.devices.get(pkg.device_id)
#        print(f"Package current device id: {pkg.device_id}")
#        pkg_dvc = c.devices.get(pkg.device_id)
#        print(f"Package current device name: {pkg_dvc.name}")
 #      dvc = c.devices.get_by_name(device_name)
        print(f"DUT Device id: {dut_device.id}")
        print(f"DUT Device name: {dut_device.name}")

        pkg_base = c.packages.get_by_name("Base")
        print(f"Base test package has {pkg_base.test_count} tests")
        tl_base = pkg_base.testlist 

        pkg_sec = c.packages.get_by_name("Security")
        print(f"Security test package has {pkg_sec.test_count} tests")
        tl_sec = pkg_sec.testlist 

        pkg_sanity = c.packages.get_by_name("Sanity check")
        print(f"Sanity test package has {pkg_sanity.test_count} tests")
        tl_sanity = pkg_sanity.testlist

        pkg_perfstab = c.packages.get_by_name("Performance/Stability")
        print(f"Performance/Stability test package has {pkg_perfstab.test_count} tests")
        tl_perfstab = pkg_perfstab.testlist

        pkg_dos = c.packages.get_by_name("DOS")
        print(f"DOS test package has {pkg_dos.test_count} tests")
        tl_dos = pkg_dos.testlist

        pkg_perf = c.packages.get_by_name("Performance")
        print(f"Performance test package has {pkg_perf.test_count} tests")
        tl_perf = pkg_perf.testlist

        pkg_tr69 = c.packages.get_by_name("Mgmt: TR-069")
        print(f"Mgmt: TR-069 test package has {pkg_tr69.test_count} tests")
        tl_tr69 = pkg_tr69.testlist

#get python base package
        pkg = c.packages.get_by_name("Python")
        pkg_opt=pkg.options
        pkg_opt.forever="true"

#set test lists 
        pkg_tag_list = list()
        pkg_tag_list.append("python")

        pkg_option = selected_options["Package"]
        if pkg_option == "Base":
            tl=tl_base
            pkg_tag="Base"
            pkg_tag_list.append("Base")
            pkg_opt.forever="false"
        elif pkg_option == "Sanity":
            tl=tl_sanity
            pkg_tag_list.append("SANITY")
            pkg_opt.forever="false"
        elif pkg_option == "Security":
            tl=tl_sec
            pkg_tag_list.append("SECURITY")
            pkg_opt.forever="false"
        elif pkg_option == "Performance":
            tl=tl_perf
            pkg_tag_list.append("PERFORMANCE")
            pkg_opt.forever="false"
        elif pkg_option == "Performance/Stability":
            tl=tl_perfstab
            pkg_tag_list.append("PERFORMANCE")
            pkg_tag_list.append("STABILITY")
            pkg_opt.forever="true"
        elif pkg_option == "DOS":
            tl=tl_dos
            pkg_tag_list.append("DOS")
            pkg_opt.forever="false"
        elif pkg_option == "Performance":
            tl=tl_perf
            pkg_tag_list.append("PERFORMANCE")
            pkg_opt.forever="false"
        elif pkg_option == "Mgmt: TR-069":
            tl=tl_tr69
            pkg_tag_list.append("MGMT")
            pkg_opt.forever="false"

        pkg_notes = pkg_option + " Package" + " - " + str(date.today()) 

        print(f"Updating package {pkg.name} with device {dut_device.name} and adding testlists...")
        #c.packages.edit(Package(id='1056', device_id=dut_device.id, testlist=tl))
        c.packages.edit(Package(id=pkg.id, device_id=dut_device.id, testlist=tl, tags=pkg_tag_list, note=pkg_notes, options=pkg_opt))

        print('Checking config for errors...')
        check = c.configs.check_config(cfg_default.contents)
        if len(check.errors) > 0:
            print('config errors:'.format(pkg.name))
            for e in check.errors:
                print('        {0}'.format(e.error))
                print('')
                continue
        print(f"Launching package {pkg.name} with associated device {dut_device.name}...")
        #j = c.jobs.launch(Job(package_id='1056'))
        j = c.jobs.launch(Job(package_id=pkg.id))

# working for job to be assigned a result ID
        print("Running startup procedure. This may take a few minutes...")
        while j.result_id is None:
            time.sleep(1)
            j = c.jobs.get(j.id)

        print('        Result-ID: {0}'.format(j.result_id))
        print('')
        print(f"Package {pkg.name} launched!")

        rslt = c.results.get(j.result_id)
        print(f"Result ID is {rslt.id}")
        print(f"Result Device is {rslt.device_id}")
        print(f"Result Note is {rslt.note}")

        return f"Launched package {pkg.name} with config {config_name}"

    else:
        return render_template('cdrouter_configurator.html', options=options)

app.run(debug=True, port=5000, host='0.0.0.0')



