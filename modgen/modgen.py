#!/usr/bin/python
############################################################################
############################################################################
"""
##  modgen - Module Generator Program for Kicad PCBnew V0.2
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
## version 0.1 - (2012-03-18)
##          -- Updated with mm to Mil Converter tool
##          -- Corrected the Error in Locking Silk screen
## version 0.2 - (2012-03-23)
##          -- Added Mil to mm and viz. Option
##          -- Added Check for Oblong pads
##          -- GUI Reorganized
##          -- Added Auto Name Generation
############################################################################
############################################################################
#IMPORTS>
import xml.dom.minidom,re,sys,os,ttk,tkMessageBox
from Tkinter import *
############################################################################
#EXPORT>
__author__ = "Abhijit Bose(info@adharlabs.in)"
__author_email__="info@adharlabs.in"
__version__ = "0.2"
############################################################################    
#DEBUG> Print Additional Debug Messages
#  if needed make _debug_message = 1
_debug_message = 0
############################################################################
#FORMAT>Lib
template_pcb = """PCBNEW-LibModule-V1  07-02-2012 08:54:12
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
    buf = buf + (int(meta["locking"])*20.0)
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
  #Check the Oblong Selection PadY>Padx
  if(float(padx.get())>=float(pady.get())) and padshape.get()=='O':
    tkMessageBox.showerror("Error","Incorrect Pad Dimensions for Oblong pads")
    er = "Oblong Pad Shape"
    return 1
  #Check the Circle Selection PadY=Padx
  if(float(padx.get())!=float(pady.get())) and padshape.get()=='C':
    tkMessageBox.showerror("Error",\
      "Incorrect Pad Dimensions for Circular pads")
    er = "Circular Pad Shape"
    return 1
  #At the End Return
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
  print "Pitch: " + pitch.get()
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
  print template_pcb%meta
  name = meta["modname"]
  if(locking.get()):
    name = name+"_LOCK"
  name = name+".emp"
  ans = tkMessageBox.askokcancel("File Wite",\
        "Do you want to wite "+name+" for the Module?")
  if(ans):
    fl = open(name,"w")
    fl.write(template_pcb%meta)
    fl.close()
    tkMessageBox.showinfo("Module Generator",\
      "Module "+meta["modname"]+" Written Successfully!!")
    print " Module "+name+" written successfully"
  return 1

def autoname():
  """ To Automatically Generate the Name,Description,RefDes,
      and Keywords for the Component
  """
  if len(modname.get())!=0:
    try:
      # Check for Berg Connector Single Row
      f = re.match("^(.)*(CONN)",modname.get().upper())
      if f!=None and package.get()=="SIP":
        Validate()
        if er != "ok":    
            print "Error In " + er
            return
        refdes.set("J")#Set the Ref
        #Decription & Keyword
        dec="Connector "+PIN_N.get()+"Pin "
        key="CONN"+("%d"%int(PIN_N.get()))
        #Add Pad Type
        if padtype.get()=="STD":
           dec = dec + " Through Hole "
           key = key + "_TH"
        else:
           dec = dec + " SMD "
           key = key + "_SMD"          
        key = key + " " + key
        #Add Pitch
        pich = "%2.2f"%(float(pitch.get())*25.4/1000)
        dec = dec + pich+"mm Pitch"
        key = key + "_" +"".join(pich.split("."))
        #Add Pads
        if float(padx.get())==float(pady.get()):
           dec = dec + " " + padx.get() +" Pad "
           key = key + "_" + ("%d"%float(padx.get()))
        else:
           dec = dec + " " + padx.get() +"X"+pady.get()+ " Pad "
           key = key + "_" + ("%d"%float(padx.get()))+\
                 "X"+("%d"%int(pady.get()))
        #Add Drill
        if padtype.get()=="STD":
           dec = dec + paddrill.get()+" Drill"
           key = key + "X" + ("%d"%float(paddrill.get()))
        #Add Pad Shape Spec  
        if padshape.get() =='O':
           dec = dec + " Oblong "
           key = key +"_O"
           if locking.get():
             dec = dec + " Locking"
             key = key +"L"
        elif padshape.get() =='R':
           dec = dec + " Spc "
           key = key +"_R"
           if locking.get():
              dec = dec + " Locking"
              key = key +"L"
        else:
           if locking.get():
              dec = dec + " Locking"
              key = key +"_L"
           else:
              dec = dec + " Normal"
              key = key +"_N"
        #Assign to Fileds
        description.set(dec)
        keywords.set(key)
        modname.set(key.split(" ")[1])
    except:
      pass

def Draw_MainPane(fr):
  """To Generate the Content for the Main Input Frame"""
  global modname,refdes,package,pitch,padx,pady,\
         paddrill,padshape,firstpinsquare,locking,padtype,PIN_N,\
         description,keywords
  Label(fr,text="Module Name:")\
          .grid(column=0,row=0,padx=2,pady=2,sticky=N+E)
  #modname=StringVar(value="Mod_Name")
  modname=StringVar(value="CONN")
  Entry(fr,textvar=modname,width=20)\
          .grid(column=1,row=0,columnspan=2,padx=2,pady=2,sticky=N+W+E)

  Label(fr,text="Reference Designator:")\
          .grid(column=0,row=1,padx=2,pady=2,sticky=N+E)
  refdes=StringVar(value="Ref_Des")
  Entry(fr,textvar=refdes,width=20)\
          .grid(column=1,row=1,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  Label(fr,text="Package:")\
          .grid(column=0,row=3,padx=2,pady=2,sticky=N+E)
  package=StringVar()
  pack=ttk.Combobox(fr,width=10,state="readonly",\
          values=['SIP'],textvariable=package)
  pack.current(0)
  pack.grid(column=1,row=3,columnspan=2,padx=2,pady=2,sticky=N+W+E)

  Label(fr,text="All Units must be in Mils",anchor="center",\
          font=("Arial",10,"bold"))\
          .grid(column=0,row=4,columnspan=3,padx=2,pady=2,sticky=N+E+W)
  
  Label(fr,text="Pitch:")\
          .grid(column=0,row=5,padx=2,pady=2,sticky=N+E)
  pitch=StringVar(value="100")
  Entry(fr,textvar=pitch,width=20)\
          .grid(column=1,row=5,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  Label(fr,text="Pad Dimension X:")\
          .grid(column=0,row=6,padx=2,pady=2,sticky=N+E)
  padx=StringVar(value="70")
  Entry(fr,textvar=padx,width=20)\
          .grid(column=1,row=6,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  Label(fr,text="Pad Dimension Y:")\
          .grid(column=0,row=7,padx=2,pady=2,sticky=N+E)
  pady=StringVar(value="70")
  Entry(fr,textvar=pady,width=20)\
          .grid(column=1,row=7,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  Label(fr,text="Pad Drill Diameter:")\
          .grid(column=0,row=8,padx=2,pady=2,sticky=N+E)
  paddrill=StringVar(value="35")
  Entry(fr,textvar=paddrill,width=20)\
          .grid(column=1,row=8,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  padshp_lb=ttk.Labelframe(fr,text="Pad Shape",padding=2)
  padshape=StringVar(value="C")
  Radiobutton(padshp_lb,text="Circle",variable=padshape,value="C")\
          .grid(column=0,row=0,sticky=N+W+S)
  Radiobutton(padshp_lb,text="Rectangle/Square",variable=padshape,value="R")\
          .grid(column=1,row=0,sticky=N+W+S)
  Radiobutton(padshp_lb,text="Oblong",variable=padshape,value="O")\
          .grid(column=3,row=0,sticky=N+W+S)
  padshp_lb.grid(column=0,row=9,columnspan=3,padx=2,pady=2,sticky=N+W+E)

  firstpinsquare = BooleanVar()
  Checkbutton(fr,text="First Pin Square",variable=firstpinsquare,\
           onvalue=True).grid(column=0,row=10,padx=2,pady=2,sticky=N+W+S)
  
  locking = BooleanVar()
  Checkbutton(fr,text="Self Locking Formation",\
     variable=locking,onvalue=True)\
     .grid(column=1,row=10,padx=2,pady=2,columnspan=2,sticky=N+W+S)

  padtyp_lb=ttk.Labelframe(fr,text="Pad Type",padding=2)
  padtype=StringVar(value="STD")
  Radiobutton(padtyp_lb,text="Through Hole",variable=padtype,value="STD")\
          .grid(column=0,row=0,sticky=N+W+S)
  Radiobutton(padtyp_lb,text="SMD",variable=padtype,value="SMD")\
          .grid(column=1,row=0,sticky=N+W+S)  
  padtyp_lb.grid(column=0,row=11,columnspan=3,padx=2,pady=2,sticky=N+W+E)

  Label(fr,text="Number of Pins:")\
          .grid(column=0,row=12,padx=2,pady=2,sticky=N+E)
  PIN_N=StringVar(value="8")
  Entry(fr,textvar=PIN_N,width=20)\
          .grid(column=1,row=12,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  Label(fr,text="Description:")\
          .grid(column=0,row=13,padx=2,pady=2,sticky=N+E)
  description=StringVar(value="Description")
  Entry(fr,textvar=description,width=40)\
          .grid(column=1,row=13,columnspan=2,padx=2,pady=2,sticky=N+W+E)
  
  Label(fr,text="Keywords:")\
          .grid(column=0,row=14,padx=2,pady=2,sticky=N+E)
  keywords=StringVar(value="Key1 Key_2")
  Entry(fr,textvar=keywords,width=20)\
          .grid(column=1,row=14,columnspan=2,padx=2,pady=2,sticky=N+W+E)

def Draw_ConvertPane(fr):
  """To Generate the Content for the Converter Frame"""
  Label(fr,text="mm to Mil Converter",justify="center")\
          .grid(column=0,row=0,columnspan=3,padx=2,pady=2,sticky=N+E+W)
  Label(fr,text="mm")\
          .grid(column=0,row=2,padx=2,pady=2,sticky=N+E)
  mm=StringVar(value="0")
  Entry(fr,textvar=mm,width=10)\
          .grid(column=1,row=2,padx=2,pady=2,sticky=N+W+E)
  Label(fr,text="Mils")\
          .grid(column=0,row=3,padx=2,pady=2,sticky=N+E)
  mil=StringVar(value="0")
  Entry(fr,textvar=mil,width=10,state="readonly")\
          .grid(column=1,row=3,padx=2,pady=2,sticky=N+W+E)
  def handler(mm,mil):
    try:
      m = float(mm.get())*(1000/25.4)
      mil.set("%f"%m)
    except:
      mm.set("0")
      
  Button(fr,text="Convert",command=lambda:handler(mm,mil))\
          .grid(column=3,row=2,padx=2,pady=2,sticky=N+W+E+S)

  Label(fr,text="Mil to mm Converter",justify="center")\
          .grid(column=0,row=4,columnspan=3,padx=2,pady=2,sticky=N+E+W)
  Label(fr,text="Mils")\
          .grid(column=0,row=6,padx=2,pady=2,sticky=N+E)
  mil1=StringVar(value="0")
  Entry(fr,textvar=mil1,width=10)\
          .grid(column=1,row=6,padx=2,pady=2,sticky=N+W+E)
  Label(fr,text="mm")\
          .grid(column=0,row=7,padx=2,pady=2,sticky=N+E)
  mm1=StringVar(value="0")
  Entry(fr,textvar=mm1,width=10,state="readonly")\
          .grid(column=1,row=7,padx=2,pady=2,sticky=N+W+E)
  def handler1(mm,mil):
    try:
      m = float(mil.get())*(25.4/1000)
      mm.set("%f"%m)
    except:
      mil.set("0")
      
  Button(fr,text="Convert",command=lambda:handler1(mm1,mil1))\
          .grid(column=3,row=6,padx=2,pady=2,sticky=N+W+E+S)

def Draw_PicturePane(fr):
  """To Generate the Content for the Picture Frame"""
  canvas = Canvas(fr,width=200,height=200,background="white")
  canvas.pack(fill=BOTH)

def Draw_CommandPane(fr):
  """To Generate the Content for the Command & Buttons Frame"""
  status = StringVar(value="""Designed by: A.D.H.A.R Labs Research,Bharat(India)
Abhijit Bose( info@adharlabs.in )
http://m8051.blogspot.com""")
  Label(fr,text="",textvariable=status)\
        .grid(column=0,row=0,rowspan=2,padx=40,pady=2,sticky=N+E+W+S)

  Button(fr,text="Auto Generate Names",command=autoname )\
          .grid(column=1,row=0,padx=20,pady=2)

  gentogether = BooleanVar()
  ck = Checkbutton(fr,text="Generate Module & Lib",variable=gentogether,\
                   onvalue=True)
  ck.grid(column=1,row=1,padx=2,pady=2,sticky=N+W+S)
  gentogether.set(True)
  
  Button(fr,text="Generate Lib",width=10,command=packed)\
                        .grid(column=2,row=0,padx=2,pady=2)
  
  Button(fr,text=" Exit Prog ",width=10,command=lambda:root.destroy())\
                        .grid(column=2,row=1,padx=2,pady=2)

  
############################################################################
# Main FUNCTION>
if __name__ == "__main__" :
  #{
  global meta       
         
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
  note = ttk.Notebook(content,padding=2)
  data_frm1 = Frame(note,width=200,height=200,borderwidth=3,\
                    relief="ridge",padx=2,pady=2)
  Draw_MainPane(data_frm1)
  #data_frm1.grid(column=0,row=0,rowspan=2,padx=5,pady=5)
  note.add(data_frm1,text="Module Generator",padding=5)
  note.grid(column=0,row=0,rowspan=2,padx=5,pady=5)
  #    } DATA FRAME 1 END
  #    { DATA FRAME 2 BEGIN
  data_frm2 = Frame(content,width=200,height=200,borderwidth=3,\
                    relief="ridge",padx=2,pady=2)
  Draw_PicturePane(data_frm2)
  data_frm2.grid(column=1,row=0,padx=5,pady=5,sticky=N+W+E)
  #    } DATA FRAME 2 END
  #    { DATA FRAME 3 BEGIN
  data_frm3 = Frame(content,width=200,height=200,borderwidth=3,\
                    relief="ridge",padx=2,pady=2)
  Draw_ConvertPane(data_frm3)  
  data_frm3.grid(column=1,row=1,padx=5,pady=5,sticky=N+W+E+S)
  #    } DATA FRAME 3 END
  #    { DATA FRAME 4 BEGIN
  data_frm4 = Frame(content,padx=2,pady=2)
  Draw_CommandPane(data_frm4)
  data_frm4.grid(column=0,row=2,columnspan=2,padx=5,pady=5,sticky=N+W+E+S)
  #    } DATA FRAME 4 END
  content.grid(column=0,row=0,sticky=N+S+E+W)
  #  }
  ## Main Loop Start
  root.mainloop()
  #}
