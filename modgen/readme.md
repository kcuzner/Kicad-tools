modgen - Module Generator Program for Kicad PCBnew V0.3
===========================================================

This *Python & Tkinter* based GUI tool designed to create Modules
(PCB Footprints or Land Pattens) for Kicad PCB.
The output from the generation is a `.emp file` that can be imported into the `PCB board`.
The examples in the subsequemt sections show this.

The Current impmentation Supports the following Packages:

 1. `SIP` - Basic Berg pin type single row Headers

 2. `DIP` - For PDIP,SOIC,SSOP,TSSOP,MSOP,SOT23-6 type Packages

 3. `CONN-Dual` - Dual Row berg Connectors with custom row spacing

 4. 'QUAD' - QFP type packages and possiblity to have Rectangular QFPs also

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


version 0.3 - (2012-03-24)

 *   Corrected SMD Pad Mask

 *   Added DIP & CONN-Dual Package Support

 *   Added Quad Package support with variable pin structure

 *   Logical GUI Re-arrangements and improvements

 *   Custom value Population using Package type selection

 *   Automatic Picture Dispay for Package & Configurations


Limitation in Present Design
-----------------------------
Need to add Further useful automatic Name Generation.

Dependency: This works on Python 2.7 and Higher version only


License
--------
Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported

[CC BY-NC-SA 3.0](http://creativecommons.org/licenses/by-nc-sa/3.0/)

[Full Text](http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode)


