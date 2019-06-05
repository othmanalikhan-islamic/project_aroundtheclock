Project: AroundTheClock
-----------------------

<br>
<p align="center">
    <img align="middle" width=1280 src="docs/demo.gif">
</p>
<br>


The objective of AroundTheClock is AroundTheClock is a self-improvement project 
that is aimed to help muslims regulate praying on time by temporarily disabling 
internet connectivity at each prayer (e.g. disabling internet for 10 minutes by 
default during the start of Asr). 

Above is a demo that illustrates it in action: The scenario is that it is 
approaching Maghrib prayer time and the internet needs to be 'paused' temporarily.
The VM on the left is running the AroundTheClock script and on the VM on the right
is a regular user on the same network. Once the time hits Maghrib (18:29:00), the 
internet is 'paused'. For the purposes of the demo, the clock is manually set.

This is achieved by calculating the prayer times for the geolocation 
specified in `config.json` then scheduling tasks in Python to disable the 
home internet. 

The idea is to download this repository on an Raspberry Pi device (or any 
other machine), connect it to your home network, and leave it running.


How to Use
----------
1. Download or clone the repository.
2. Run `install.sh`.
3. Modify `config.json` to your geolocation.
4. Run `run.sh` to start the script and enable it at boot time.
5. Use `systemctl status` and/or navigate to `output/` for more details.


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
in `config.json`. This needs to be accurate as an error of .1 degree in 
longitude or latitiude can cause prayer times to be shifted in some cases by 
up to 3 minutes. Note that clocks on mosques follow pre-defined coordinates, 
and this sometimes varies between clocks too unfortunately (not full 
standardization).


Authors
-------
|      Name      |           Email           | 
| -------------- |:-------------------------:| 
| Othman Alikhan | oz.alikhan@gmail.com      | 


Credits
-------
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
