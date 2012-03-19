#!/usr/bin/python
############################################################################
############################################################################
"""
##  modgen - Module Generator Program for Kicad PCBnew V0.1
## 
##  Designed by
##         A.D.H.A.R Labs Research,Bharat(India)
##            Abhijit Bose( info@adharlabs.in )
##                http://ahdarlabs.in
##
## License:
## Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported
## CC BY-NC-SA 3.0 http://creativecommons.org/licenses/by-nc-sa/3.0/
## http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode
"""
##
## Version History:
## version 0.0 - Initial Release (2012-03-16)
##          -- Support for Single Inline Connectors
## version 0.1 - Updated with mm to Mil Converter tool
##          -- Corrected the Error in Locking Silk screen
############################################################################
############################################################################
#IMPORTS>
import xml.dom.minidom,sys,os,ttk,tkMessageBox
from Tkinter import *
############################################################################
#EXPORT>
__author__ = "Abhijit Bose(info@adharlabs.in)"
__author_email__="info@adharlabs.in"
__version__ = "0.1"
############################################################################    
#DEBUG> Print Additional Debug Messages
#  if needed make _debug_message = 1
_debug_message = 0
############################################################################
#FORMAT>Lib
template = """PCBNEW-LibModule-V1  07-02-2012 08:54:12
# encoding utf-8
$INDEX
%(modname)s
$EndINDEX
#
# %(modname)s PACK[%(package)s] 
#
$MODULE %(modname)s
Po 0 0 0 15 4F309929 00000000 ~~
Li %(modname)s
Cd %(description)s
Kw %(keywords)s
Sc 00000000
AR %(modname)s
Op 0 0 0
T0 0 -1000 600 600 0 120 N V 21 "%(refname)s"
T1 0 -500 50 50 0 10 N I 21 "VAL**"
%(drawing)s
%(pads)s
$EndMODULE  %(modname)s
$EndLIBRARY
#
# End Module
"""
template_pad="""
$PAD
Sh %(shape)s
Dr %(drill)s
At %(padtype)s N %(layermask)s
Ne 0 ""
Po %(pinx)s %(piny)s
$EndPAD"""
############################################################################
#FORMAT FUNCTIONS>
def PinDescriptions(comp):
  "Read in the pin descriptions as a list"
  el = xmlcomp.getElementsByTagName("module")[0]
  xbits=[i.data for i in el.childNodes if i.nodeType==el.TEXT_NODE]
  
  # Split into lines
  bits = "".join(xbits).split("\n")
  #Remove white space
  bits = [ i.strip() for i in bits ]
  #Remove empty strings
  bits = [ i for i in bits if i!="" ]
  #Get the Pin names & Modes
  bits = [ i.split(',') for i in bits]
  return bits

def PinGen(numb):
  "Generate Pin Numbers if No pin Description is available using PIN"
  bits = []
  for i in range(1,numb+1):
    bits.append([str(i)])
  #print bits
  return bits

def MetaData(comp):
  "Extract the component description parameters (common to all pins)"
  el = comp.getElementsByTagName("module")[0]
  d = {}
  for name, value in el.attributes.items() :
    d[name] = value
  return d

def MakePads_SIP(pins,meta):
  """To Make the Pads and draw outline for SIP Connector"""
  pin_str = ""
  x = 0
  y = 0
  pin = {}
  pitch = float(meta["pitch"]) * 10
  locking = 0
  for p in pins:
    if(meta["locking"]!=None):
      if(locking==0):
        locking=1
        pin["piny"]="%d"%(y+(int(meta["locking"])*10))
      else:
        locking=0
        pin["piny"]="%d"%(y-(int(meta["locking"])*10))
    else:
      pin["piny"]="%d"%(y)
    pin["pinx"]="%d"%(x)
    x = x + pitch
    pin["padtype"]=meta["padtype"]
    pin["layermask"]='00E0FFFF' #normally for STD
    pin["drill"]="%d 0 0"%(int(float(meta["paddrill"])*10))
    if(x==pitch and meta["firstpadsquare"]!= None):
      pin["shape"]="\"%s\" %s %d %d 0 0 0"%(p[0],"R",\
          float(meta["padx"])*10,float(meta["pady"])*10)
    else:
      pin["shape"]="\"%s\" %s %d %d 0 0 0"%(p[0],meta["padshape"],\
          float(meta["padx"])*10,float(meta["pady"])*10)
    pin_str += template_pad%pin #Add the Pad
  # Make Drawing  
  buf = (max(float(meta["padx"]),float(meta["pady"]))+50)*10
  X = x - pitch + buf
  mx = buf/-2
  if(meta["locking"]!=None):#Add some margin for Locking
    buf = buf + (int(meta["locking"])*2.0)
  Y = buf #Increase Y Only  
  my = buf/-2  
  drawing  = "DS %d %d %d %d 120 21"%(mx,my,mx+X,my)
  drawing += "\nDS %d %d %d %d 120 21"%(mx,my,mx,my+Y)
  drawing += "\nDS %d %d %d %d 120 21"%(mx,my+Y,mx+X,my+Y)
  drawing += "\nDS %d %d %d %d 120 21"%(mx+X,my,mx+X,my+Y)
  meta["drawing"]=drawing
  return pin_str

def MakePads(pins,meta):
  """Convert the Pins into a string of Pad data and add Drawing"""
  if meta["package"]=='SIP':
    return MakePads_SIP(pins,meta)
  print "Error: Un Supported Package"
  exit(0)
############################################################################
def Validate():
  """To Validate the GUI Inputs"""
  global er
  er = 1
  # Check Pitch
  try:
    k = float(pitch.get())*1.0
    er = "ok"
    if(k<=0):
      tkMessageBox.showerror("Error","Invalid Pitch Value")        
      er = "pitch"
      pitch.set("100")
      return 1
  except:    
    tkMessageBox.showerror("Error","Invalid Pitch Value")        
    er = "pitch"
    pitch.set("100")
    return 1
  # Check Padx
  try:
    k = float(padx.get())*1.0
    er = "ok"
    if(k<=0):
      tkMessageBox.showerror("Error","Invalid Pad X Value")        
      er = "padx"
      padx.set("70")
      return 1
  except:    
    tkMessageBox.showerror("Error","Invalid Pad X Value")        
    er = "padx"
    padx.set("70")
    return 1
  # Check Pady
  try:
    k = float(pady.get())*1.0
    er = "ok"
    if(k<=0):
      tkMessageBox.showerror("Error","Invalid Pad Y Value")        
      er = "pady"
      pady.set("70")
      return 1
  except:    
    tkMessageBox.showerror("Error","Invalid Pad Y Value")        
    er = "pady"
    pady.set("70")
    return 1
  # Check Pad Drill
  try:
    k = float(paddrill.get())*1.0
    er = "ok"
    if(k<=10 or k>250):
      tkMessageBox.showerror("Error","Invalid Pad Drill Value")        
      er = "paddrill"
      paddrill.set("35")
      return 1
  except:    
    tkMessageBox.showerror("Error","Invalid Pad Drill Value")        
    er = "paddrill"
    paddrill.set("35")
    return 1
  # Check Pin N
  try:
    k = int(PIN_N.get())*1
    er = "ok"
    if(k<=1):
      tkMessageBox.showerror("Error","Invalid Number of Pins")        
      er = "PIN_N"
      PIN_N.set("8")
      return 1
  except:    
    tkMessageBox.showerror("Error","Invalid Number of Pins")        
    er = "PIN_N"
    PIN_N.set("8")
    return 1
  #Check The Description
  if(len(description.get())==0):
    description.set(modname.get())
  #Check The Keywords
  if(len(keywords.get())==0):
    keywords.set(modname.get())
  return 1

def packed():
  """To Pack the GUI inputs to the XML form"""
  Validate()  
  if er != "ok":    
    print "Error In " + er
    return 0
  print "Module Name: " + modname.get()
  meta["modname"] = modname.get()
  print "Reference Designator: " + refdes.get()
  meta["refname"] = refdes.get()
  print "Package: " + package.get()
  meta["package"] = package.get()
  print "Units: " + units.get()  
  print "Pitc: " + pitch.get()
  meta["pitch"] = pitch.get()
  print "Pad x Dimension: " + padx.get()
  meta["padx"] = padx.get()
  print "Pad y Dimension: " + pady.get()
  meta["pady"] = pady.get()
  print "Pad Drill Diameter: " + paddrill.get()
  meta["paddrill"] = paddrill.get()
  print "Pad Shape: "+ padshape.get()
  meta["padshape"] = padshape.get()
  print "First Pad Square: " + ("True" if firstpinsquare.get() else "False")
  meta["firstpadsquare"] = 1 if firstpinsquare.get() else None
  print "Self Locking Pattern: " + ("True" if locking.get() else "False")
  meta["locking"] = "5" if locking.get() else None
  print "Pad Type: " + padtype.get()
  meta["padtype"] = padtype.get()
  print "Number of Pins: " + PIN_N.get()
  meta["PIN_N"] = PIN_N.get()
  pins = PinGen(int(meta["PIN_N"]))
  print "Description for Module: " + description.get()
  meta["description"] = description.get()
  print "Keywords for Module: " + keywords.get()
  meta["keywords"] = keywords.get()

  meta["pads"]=MakePads(pins,meta)
  print template%meta
  name = meta["modname"]
  if(locking.get()):
    name = name+"_LOCK"
  name = name+".emp"
  ans = tkMessageBox.askokcancel("File Wite",\
        "Do you want to wite "+name+" for the Module?")
  if(ans):
    fl = open(name,"w")
    fl.write(template%meta)
    fl.close()
    tkMessageBox.showinfo("Module Generator",\
      "Module "+meta["modname"]+" Written Successfully!!")
    print " Module "+name+" written successfully"
  return 1
  
############################################################################
# Main FUNCTION>
if __name__ == "__main__" :
  #{
  global meta,root,status,modname,refdes,package,units,pitch,padx,pady,\
         paddrill,padshape,firstpinsquare,locking,padtype,PIN_N,\
         description,keywords
  meta = {}
  print __doc__
  ## Create Main Window
  root = Tk()
  root.title("Module Generator by A.D.H.A.R Labs Research,Bharat(India)")  
  root.bind("<Escape>",lambda e:root.destroy())
  root["padx"]=10
  root["pady"]=10
  #  { MAIN CONTENT BEGIN
  content = Frame(root,width=300,height=200,borderwidth=2,relief="groove")
  #    { DATAFRAME 1 BEGIN
  data_frm1 = Frame(content,width=200,height=200,borderwidth=3,\
                    relief="ridge",padx=2,pady=2)
  
  Label(data_frm1,text="Module Name:")\
          .grid(column=0,row=0,padx=2,pady=2,sticky=N+E)
  modname=StringVar(value="Mod_Name")
  Entry(data_frm1,textvar=modname,width=20)\
          .grid(column=1,row=0,columnspan=2,padx=2,pady=2,sticky=N+W+E)

  Label(data_frm1,text="Reference Designator:")\
          .grid(column=0,row=1,padx=2,pady=2,sticky=N+E)
  refdes=StringVar(value="Ref_Des")
  Entry(data_frm1,textvar=refdes,width=20)\
          .grid(column=1,row=1,columnspan=2,padx=2,pady=2,sticky=N+W+E)

  Label(data_frm1,text="Package:")\
          .grid(column=0,row=3,padx=2,pady=2,sticky=N+E)
  package=StringVar()
  pack=ttk.Combobox(data_frm1,width=10,state="readonly",\
          values=['SIP'],textvariable=package)
  pack.current(0)
  pack.grid(column=1,row=3,columnspan=2,padx=2,pady=2,sticky=N+W+E)

  unit_lb=ttk.Labelframe(data_frm1,text="Units",padding=2)
  units=StringVar(value="mils")
  Radiobutton(unit_lb,text="Mils",variable=units,value="mils",width=5)\
          .grid(column=0,row=0,sticky=N+W+S)
##  Radiobutton(unit_lb,text="MM",variable=units,value="mm",width=5)\
##          .grid(column=1,row=0,sticky=N+E+S)#Presently only Mils
  unit_lb.grid(column=0,row=4,columnspan=3,padx=2,pady=2,sticky=N+W+E)

  Label(data_frm1,text="Pitch:")\
          .grid(column=0,row=5,padx=2,pady=2,sticky=N+E)
  pitch=StringVar(value="100")
  Entry(data_frm1,textvar=pitch,width=20)\
          .grid(column=1,row=5,columnspan=2,padx=2,pady=2,sticky=N+W+E)

  Label(data_frm1,text="Pad Dimension X:")\
          .grid(column=0,row=6,padx=2,pady=2,sticky=N+E)
  padx=StringVar(value="70")
  Entry(data_frm1,textvar=padx,width=20)\
          .grid(column=1,row=6,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  Label(data_frm1,text="Pad Dimension Y:")\
          .grid(column=0,row=7,padx=2,pady=2,sticky=N+E)
  pady=StringVar(value="70")
  Entry(data_frm1,textvar=pady,width=20)\
          .grid(column=1,row=7,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  Label(data_frm1,text="Pad Drill Diameter:")\
          .grid(column=0,row=8,padx=2,pady=2,sticky=N+E)
  paddrill=StringVar(value="35")
  Entry(data_frm1,textvar=paddrill,width=20)\
          .grid(column=1,row=8,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  padshp_lb=ttk.Labelframe(data_frm1,text="Pad Shape",padding=2)
  padshape=StringVar(value="C")
  Radiobutton(padshp_lb,text="Circle",variable=padshape,value="C")\
          .grid(column=0,row=0,sticky=N+W+S)
  Radiobutton(padshp_lb,text="Rectangle/Square",variable=padshape,value="R")\
          .grid(column=1,row=0,sticky=N+W+S)
  Radiobutton(padshp_lb,text="Oblong",variable=padshape,value="O")\
          .grid(column=3,row=0,sticky=N+W+S)
  padshp_lb.grid(column=0,row=9,columnspan=3,padx=2,pady=2,sticky=N+W+E)

  firstpinsquare = BooleanVar()
  Checkbutton(data_frm1,text="First Pin Square",variable=firstpinsquare,\
           onvalue=True).grid(column=0,row=10,padx=2,pady=2,sticky=N+W+S)
  
  locking = BooleanVar()
  Checkbutton(data_frm1,text="Self Locking Formation",\
     variable=locking,onvalue=True)\
     .grid(column=1,row=10,padx=2,pady=2,columnspan=2,sticky=N+W+S)

  padtyp_lb=ttk.Labelframe(data_frm1,text="Pad Type",padding=2)
  padtype=StringVar(value="STD")
  Radiobutton(padtyp_lb,text="Through Hole",variable=padtype,value="STD")\
          .grid(column=0,row=0,sticky=N+W+S)
  Radiobutton(padtyp_lb,text="SMD",variable=padtype,value="SMD")\
          .grid(column=1,row=0,sticky=N+W+S)  
  padtyp_lb.grid(column=0,row=11,columnspan=3,padx=2,pady=2,sticky=N+W+E)

  Label(data_frm1,text="Number of Pins:")\
          .grid(column=0,row=12,padx=2,pady=2,sticky=N+E)
  PIN_N=StringVar(value="8")
  Entry(data_frm1,textvar=PIN_N,width=20)\
          .grid(column=1,row=12,columnspan=2,padx=2,pady=2,sticky=N+W+E)

  Label(data_frm1,text="Description:")\
          .grid(column=0,row=13,padx=2,pady=2,sticky=N+E)
  description=StringVar(value="Description")
  Entry(data_frm1,textvar=description,width=40)\
          .grid(column=1,row=13,columnspan=2,padx=2,pady=2,sticky=N+W+E)

  Label(data_frm1,text="Keywords:")\
          .grid(column=0,row=14,padx=2,pady=2,sticky=N+E)
  keywords=StringVar(value="Key1 Key_2")
  Entry(data_frm1,textvar=keywords,width=20)\
          .grid(column=1,row=14,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  data_frm1.grid(column=0,row=0,columnspan=2,rowspan=2,padx=5,pady=5)
  #    } DATA FRAME 1 END
  #    { DATA FRAME 2 BEGIN
  data_frm2 = Frame(content,width=200,height=200,borderwidth=3,\
                    relief="ridge",padx=2,pady=2)
  canvas = Canvas(data_frm2,width=200,height=200,background="white")
  canvas.pack(fill=BOTH)
  data_frm2.grid(column=2,row=0,columnspan=2,padx=5,pady=5,sticky=N+W+E)
  #    }  #DATA FRAME 2 END
  #    { DATA FRAME 3 BEGIN
  data_frm3 = Frame(content,width=200,height=200,borderwidth=3,\
                    relief="ridge",padx=2,pady=2)
  Label(data_frm3,text="mm to Mil Converter",justify="center")\
          .grid(column=0,row=0,columnspan=3,padx=2,pady=2,sticky=N+E+W)
  Label(data_frm3,text="mm")\
          .grid(column=0,row=2,padx=2,pady=2,sticky=N+E)
  mm=StringVar(value="0")
  Entry(data_frm3,textvar=mm,width=10)\
          .grid(column=1,row=2,padx=2,pady=2,sticky=N+W+E)
  Label(data_frm3,text="mils")\
          .grid(column=0,row=3,padx=2,pady=2,sticky=N+E)
  mil=StringVar(value="0")
  Entry(data_frm3,textvar=mil,width=10,state="readonly")\
          .grid(column=1,row=3,padx=2,pady=2,sticky=N+W+E)
  def handler(mm,mil):
    try:
      m = float(mm.get())*(1000/25.4)
      mil.set("%f"%m)
    except:
      mm.set("0")
      
  Button(data_frm3,text="Convert",command=lambda:handler(mm,mil))\
          .grid(column=3,row=2,padx=2,pady=2,sticky=N+W+E+S)
    
  data_frm3.grid(column=2,row=1,columnspan=2,padx=5,pady=5,sticky=N+W+E+S)
  #    }  #DATA FRAME 3 END
  Button(content,text="Generate",width=10,command=packed)\
                        .grid(column=2,row=2,padx=2)
  Button(content,text="Exit",width=10,command=lambda:root.destroy())\
                        .grid(column=3,row=2,padx=2)
  status = StringVar(value="""Designed by: A.D.H.A.R Labs Research,Bharat(India)
Abhijit Bose( info@adharlabs.in )
http://m8051.blogspot.com""")
  Label(content,text="",textvariable=status)\
        .grid(column=0,row=2,padx=2,columnspan=2,sticky=N+E+W+S)
  
  content.grid(column=0,row=0,sticky=N+S+E+W)
  #  }
  ## Main Loop Start
  root.mainloop()
  #}
