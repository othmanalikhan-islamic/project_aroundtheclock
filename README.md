Project AroundTheClock: Praying on Time!
========================================

<br>
<p align="center">
    <img align="middle" width=1280 src="docs/demo.gif">
</p>
<br>


[![Build Status](https://travis-ci.org/OthmanEmpire/project_aroundtheclock.svg?branch=master)](https://travis-ci.org/OthmanEmpire/project_aroundtheclock)
[![Code Coverage](https://codecov.io/gh/OthmanEmpire/project_aroundtheclock/branch/master/graphs/badge.svg)](https://codecov.io/gh/OthmanEmpire/project_aroundtheclock/branch/master)
[![Maintainability](https://api.codeclimate.com/v1/badges/60e535faa629e6023a5d/maintainability)](https://codeclimate.com/github/OthmanEmpire/project_aroundtheclock/maintainability)
[![Last Commit](https://img.shields.io/github/last-commit/othmanempire/project_aroundtheclock)](https://github.com/OthmanEmpire/project_aroundtheclock)
[![Issues](https://img.shields.io/github/issues-raw/othmanempire/project_aroundtheclock)](https://github.com/OthmanEmpire/project_aroundtheclock)
[![Known Vulnerabilities](https://snyk.io//test/github/OthmanEmpire/project_aroundtheclock/badge.svg?targetFile=requirements.txt)](https://snyk.io//test/github/OthmanEmpire/project_aroundtheclock?targetFile=requirements.txt)
[![License](https://img.shields.io/github/license/othmanempire/project_aroundtheclock)](https://github.com/OthmanEmpire/project_aroundtheclock)

Overview
--------

The objective of AroundTheClock is AroundTheClock is a self-improvement project 
that is aimed to help muslims regulate praying on time by temporarily disabling 
internet connectivity at each prayer (e.g. disabling internet for 10 minutes by 
default during the start of Asr). 

Above is a demo that illustrates it in action: The scenario is that it is 
approaching Asr prayer time and the internet needs to be 'paused' temporarily.
The VM on the left is running the AroundTheClock script and on the VM on the right
is a regular user on the same network. Once the time hits Asr (15:05:00), the 
internet is 'paused'. For the purposes of the demo, the the script and clock 
are manually controlled, however, in a real-world scenario is is fully automated.

This is achieved by calculating the prayer times for the geolocation 
specified in `config.json` then scheduling tasks in Python to disable the 
home internet. 

The idea is to download this repository on an Raspberry Pi device (or any 
other machine), connect it to your home network, and leave it running.


How to Use
----------
1. Clone the repository, `git clone https://github.com/OthmanEmpire/project_aroundtheclock`
2. Navigate to the root project directory, `cd project_aroundtheclock`
3. Modify `config.json` to your geolocation, `vi config.json`
4. Change permissions of the installation script, `chmod u+x install.sh`
5. Run the installation script, `./install.sh`.


Troubleshooting
---------------
- **Issue:** How do check if aroundtheclock is running?
- **Solution:** Check its daemon, `systemctl status aroundtheclock.service`.
<br>

- **Issue:** I get the error 'Unit aroundtheclock.service could not be found'!
- **Solution:** The installation process failed. Re-run the installation script, `./install.sh`.
<br>

- **Issue:** I can see aroundtheclock service but its state isn't 'active'!
- **Solution A:** Restart the service manually, `systemctl restart aroundtheclock.service`.
- **Solution B:** Check the logs of the service, `journalctl -u aroundtheclock.service`.
- **Solution C:** Check the logs of the application, `output/log.txt`.


Key Features
------------
- Calculates individual prayer times up to an accuracy of 1 minute.
- Schedules jobs to block the internet temporarily for all prayers.
- Configurable duration of block via `config.json`.
- Logs computed prayer times as well as scheduled jobs to blocking internet.
- Source code is structured via a functional approach (thus can verify formulae).


Limitations
------------
- Works only on a single subnet. If your home network spans multiple subnets 
(most home setups don't), then only the subnet of the device running the 
script will have its internet connectivity disabled.
- Some advanced configuration applied on a network device may prevent arp 
poisoning (e.g. static arp entries for default gateway). Most home setups 
don't fall under this category.
- For now, the user needs to manually specify their geolocation coordinates 
in `config.json`. The longitude and latitude need to be accurate to 0.1 degree 
in otherwise it can cause prayer times to be shifted in some cases by 
up to 3 minutes. Note that clocks on mosques follow pre-defined coordinates, 
and this sometimes varies between clocks too unfortunately (not full 
standardization). For now, `config.json` is configured for coordinates in 
Saudi Arabia, AlKhobar.


Authors
-------
|      Name      |           Email           | 
| -------------- |:-------------------------:| 
| Othman Alikhan | oz.alikhan@gmail.com      | 


Acknowledgements
----------------
##### Individals
- *AbdulAziz Almass:* For inspiring me to take on this project.

##### Derivation of Astronomical and Prayer Formulae
- https://aa.usno.navy.mil/faq/docs/SunApprox.php (see docs folder)
- http://www.astronomycenter.net/pdf/mohamoud_2017.pdf
- https://en.wikipedia.org/wiki/Salah_times#Time_calculation

##### Reference Code
- Below are scripts that heavily inspired this project:
    - Python implementation: http://praytimes.org/calculation/
    - C++ implementation: http://3adly.blogspot.com/2010/07/prayer-times-calculations-pure-c-code.html


TODO
----
- Study how input parameters (e.g. JD, LAT, LON) vary prayer times mathematically.
- Study domain and range restrictions of formulae
- Document the findings above in docstrings
- Add an uninstall script
- Add tests for deployment
