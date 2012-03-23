modgen - Module Generator Program for Kicad PCBnew V0.2
===========================================================

This *Python & Tkinter* based GUI tool designed to create Modules
(PCB Footprints or Land Pattens) for Kicad PCB.
The output from the generation is a `.emp file` that can be imported into the `PCB board`.
The examples in the subsequemt sections show this.
A [`Tutorial`](https://github.com/AdharLabs/Kicad-tools/wiki/Tutorial-for-modgen)
for this tool is also available.

![Picture](https://github.com/AdharLabs/Kicad-tools/raw/master/modgen/modgenui.PNG)


**Dependency: This works on Python 2.7 and Higher version only**


Designed By
-----------
**A.D.H.A.R Labs Research,Bharat(India)**

Abhijit Bose [info@adharlabs.in](mailto:info@adharlabs.in)

[http://adharlabs.in](http://adharlabs.in)


Version History
---------------
version 0.0 - Initial Release (2012-03-16)

 *    Support for SIP Single Inline Connectors


version 0.1 - (2012-03-18)

 *   Updated with mm to Mil Converter tool

 *   Corrected the Error in Locking Silk screen


version 0.2 - (2012-03-23)

 *   Added Mil to mm and viz. Option

 *   Added Check for Oblong pads

 *   GUI Reorganized

 *   Added Auto Name Generation


Limitation in Present Design
-----------------------------
The generator works using ** Mils Units ** however there are 
plans to expand it for * mm Units * also.


License
--------
Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported

[CC BY-NC-SA 3.0](http://creativecommons.org/licenses/by-nc-sa/3.0/)

[Full Text](http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode)


