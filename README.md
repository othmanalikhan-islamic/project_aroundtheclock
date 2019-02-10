Project: AroundTheClock
-----------------------
The objective of AroundTheClock is to help muslims regulate praying on time by
temporarily disabling internet connectivity around each prayer (e.g. for 10 
minutes). 

This is achieved by calculating the prayer times for a given location then
scheduling a bash script through `cron` to disable the home internet 
(arp poisoning).

How to Use
----------
1. Download or clone the repository.
2. `pip install -r requirements` to install dependencies.
3. ???


Key Features
------------
- Calculates prayer times up to an accuracy of 1 minute


Limitations
------------
- Will only work on a LAN level. If your home network has multiple subnets, 
then it will only disable internet connectivity on the same LAN that the script
is runs on.
- Some advanced network devices may prevent arp poisoning.


Authors
-------
|      Name      |           Email           | 
| -------------- |:-------------------------:| 
| Othman Alikhan | oz.alikhan@gmail.com      | 


Credits
-------
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
- Study how input parameters (e.g. JD, LAT, LON) vary prayer times
- Specify restrictions of formula in docstring