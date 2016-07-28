from lxml import etree as ET
from Tkinter import *
from ttk import *
import tkMessageBox
import tkFileDialog

ns = {'n1': 'http://www.stercomm.com/SI/Map'}

class cond_window(Frame):                   # A pop-up window to ask the condition
    def destroy(self) :
        condition.set("")
        self.top.destroy()
        
    def __init__(self,parent):
        top = self.top = Toplevel(parent)
        self.top.geometry('500x150+400+300')
        self.top.title("Condition")

        Label(self.top,text = "Enter the Condition:").grid(row=0,column=0,pady = 30,padx = 25)
        Entry(self.top,textvariable = condition,width = 50).grid(row=0,column=1,pady = 6)

        Button(self.top,text = "Submit",command = self.top.destroy).grid(row=1,column=1,padx =20,sticky = 'W')

class Tab1(Frame):                      #Edit lxml tab              
    
    def open_file(self) :               #For open file dialog box
        file_name  = tkFileDialog.askopenfilename(defaultextension = '.mxl',filetypes = [('Source Maps','.mxl;.map')])
                                        #sets the value of entry to the chosen file name 
        fname.set(file_name)

    def addwhile(self) :                #adds a while statement to the text box
        self.wait_window(cond_window(self).top)
        self.text.insert(self.text.index(INSERT),"WHILE ("+condition.get()+") DO \n\tBEGIN\n\tEND\n")
        condition.set("")
        
    def addif(self) :                   #adds an if statement to the text box
        self.wait_window(cond_window(self).top)
        self.text.insert(self.text.index(INSERT),"If "+condition.get()+" THEN \n\tBEGIN\n\tEND\nElse THEN \n\tBEGIN\n\tEND\n")
        condition.set("")
        
    def addelif(self) :                 #adds an else if statement to the text box
        self.wait_window(cond_window(self).top)
        self.text.insert(self.text.index(INSERT),"ELSE If "+condition.get()+" THEN \n\tBEGIN\n\tEND\n")
        condition.set("")
        
    def onbegin(self) :                 #sets the position value to 0 when onbegin is clicked
        position.set(0)
        self.top.destroy()

    def onend(self) :                   #sets the position value to 1 when onend is clicked
        position.set(1)
        self.top.destroy()
        
    def edit (self) :
        if(I_or_O.get()==0 or option.get() ==0 or name.get().strip() == "" or fname.get() == ""):       #checks for empty fields
            tkMessageBox.showerror("Error","Please fill the empty field",parent = self)
            return

        else :
            tree = ET.parse(fname.get())            #parses the tree
            root = tree.getroot()
            
            xpath = ""

            if I_or_O.get() == 1 :
                xpath = "./n1:INPUT/n1:EDISyntax/n1:Group"
            elif I_or_O.get() == 2 :
                xpath = "./n1:OUTPUT/n1:EDISyntax/n1:Group"

            found = root.find(xpath,ns)
            isthere = False
            
            for node in found.iterfind('.//n1:Name', ns):
                if node.text == name.get() :
                    isthere = True                                  
                    if "Field" in node.getparent().tag :                #checks if the name belongs to field
                        while("StoreLimit" not in node.tag) :
                            node = node.getnext()
                            
                        if I_or_O.get() == 2 :                          #if the name is in output checks if there is any link
                            if "Link" in node.getnext().tag :
                                node = node.getnext()
                                
                        if "ExplicitRule" in node.getnext().tag :       #checks if there is an explicit rule tag initially
                            node = node.getnext()
                        else :                                          #if not present creates one tag
                            explicit_rule = ET.Element('{http://www.stercomm.com/SI/Map}ExplicitRule')
                            node.addnext(explicit_rule)
                            node = explicit_rule
                                
                    elif "Segment" in node.getparent().tag or "Group" in node.getparent().tag :
                                                                        #checks if the name belongs to segment or group
                        if "Segment" in node.getparent().tag :
                            while("Max" not in node.tag) :
                                node = node.getnext()
                            if node.text == '1' :                       #checks if the given segment name can have extended rule or not 
                                tkMessageBox.showerror("Error","The given segment name cannot have explicit rule",parent = self)
                                return                                    

                        while("UsageRelatedFieldName" not in node.tag) :
                            node = node.getnext()
                        if "ExplicitRule" in node.getnext().tag :       #checks if there is an explicit rule tag initially
                            node = node.getnext()

                        else :                                          #if not present creates one tag with OnBegin and OnEnd as children
                            explicit_rule = ET.Element('{http://www.stercomm.com/SI/Map}ExplicitRule')
                            print explicit_rule.tag
                            print node.tag
                            explicit_rule_begin = ET.SubElement(explicit_rule,'{http://www.stercomm.com/SI/Map}OnBegin')
                            explicit_rule_end = ET.SubElement(explicit_rule,'{http://www.stercomm.com/SI/Map}OnEnd')
                            node.addnext(explicit_rule)
                            node = explicit_rule

                        children = node.getchildren()

                        ## creates a pop message asking where to insert

                        self.top = Toplevel()
                        self.top.geometry('240x150+400+300')
                        self.top.title("Segment or Group")
                        
                        

                        msg = Message(self.top,text = "Where to insert?",width = 100)
                        msg.grid(row = 0,column = 0,padx = 70,pady = 30,columnspan = 6 )

                        Button(self.top,text = "On Begin" , command = self.onbegin).grid(row = 1,column = 1)
                        Button(self.top,text = "On End", command = self.onend).grid(row = 1,column = 4)

                        self.top.wait_window(self.top)

                        ##
                        
                        node = children[position.get()]
                        
                    if option.get() == 1 :                              
                        node.text = self.text.get('1.0',END)            #replaces the extended rule
                    elif option.get() == 2 :
                        node.text = node.text+self.text.get('1.0',END)  #appends to the existing extended rule
                        
                    break
                
            if isthere == False :
                tkMessageBox.showerror("Error","The given operation name is not found",parent = self)

            else :   
                tree.write(fname.get(),encoding = "UTF-8",xml_declaration = True)# writes to the file
                self.text.delete('1.0',END)                             #Clears the entered options to repeat the process
                name.set("")
                fname.set("")
                I_or_O.set(0)
                option.set(0)
                tkMessageBox.showinfo("Successful","The extended rule is updated",parent = self)
    
    def createWidgets(self) :       ##adds widgets to the tab 1
                    
        Label(self,text = "Open the file:").grid(row = 0,column = 0,sticky = 'W')
        Entry(self,textvariable = fname,width = 30,state = 'readonly').grid(row = 0,column = 1,sticky = 'W')
        Button(self,text = "Browse" ,command = self.open_file).grid(row = 0,column = 3,sticky = 'W')
        
        Label(self, text="enter the name of the operation:").grid(row = 1,column = 0,sticky = 'W')
        Entry(self,textvariable = name).grid(row = 1,column = 1,sticky = 'W')

        Label(self, text="to edit:").grid(row = 2,column = 0,sticky = 'W')
        Radiobutton(self,text = "Input",variable = I_or_O,value = 1).grid(row = 2,column = 0,padx = 40,sticky = 'W')
        Radiobutton(self,text = "Output",variable = I_or_O,value = 2).grid(row = 3,column = 0,padx = 40,sticky = 'W')

        Label(self, text="enter the extended rule:").grid(row =4 ,sticky = 'W')
        Radiobutton(self,text = "to replace",variable = option,value = 1).grid(row = 5,column = 0,sticky = 'W')
        Radiobutton(self,text = "to append",variable = option,value = 2).grid(row = 5,column = 1,sticky = 'W')
        
        self.text = Text(self,width = 50,height = 15)
        self.text.insert('1.3', '//extended rule starts here\n')
        self.text.grid(row =6,rowspan = 5,columnspan = 3,padx = 10)
        
        Button(self,text = "while" ,command = self.addwhile).grid(row = 6,column = 3,padx = 2,sticky = 'W')
        Button(self,text = "If" ,command = self.addif).grid(row = 7 ,column = 3,padx = 2,sticky = 'W')
        Button(self,text = "Else if" ,command = self.addelif).grid(row = 8 ,column = 3,padx = 2,sticky = 'W')
        
        
        Button(self,text = "Submit",command = self.edit).grid(row = 11,column =0,pady = 6)
        Button(self,text = "Quit",command = self.quit).grid(row = 11,column =1,pady = 6)
        
            
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

class Tab2(Frame):
    def open_file(self) :                           ## open file dialog box
        file_name  = tkFileDialog.askopenfilename(defaultextension = '.mxl',filetypes = [('Source Maps','.mxl;.map')])
        fname_2.set(file_name)
        tree = ET.parse(fname_2.get())
        root = tree.getroot

    def getinput(self) :                            ## fills the drop down menu operation names in the input side
        tree = ET.parse(fname_2.get())
        root = tree.getroot()        
        xpath = "./n1:INPUT/n1:EDISyntax/n1:Group"
        found = root.find(xpath,ns)
        I = [elem.text for elem in  found.iterfind('.//n1:Name', ns)]
        self.i['values'] = I

    def getoutput(self) :                           ## fills the drop down menu operation names in the output side
        tree = ET.parse(fname_2.get())
        root = tree.getroot()        
        xpath = "./n1:OUTPUT/n1:EDISyntax/n1:Group"
        found = root.find(xpath,ns)
        O = [elem.text for elem in  found.iterfind('.//n1:Name', ns)]
        self.o['values'] = O

    def get_id(self) :                              ## returns the operation id when operation name is given
        tree = ET.parse(fname_2.get())
        root = tree.getroot()        
        xpath = "./n1:INPUT/n1:EDISyntax/n1:Group"
        found = root.find(xpath,ns)
        for node in found.iterfind('.//n1:Name', ns):
            if node.text == self.i.get() :
                node = node.getprevious()
                break
        return node.text
        

    def form_link(self) :                           ##edits the .mxl file 
        tree = ET.parse(fname_2.get())
        root = tree.getroot()        
        xpath = "./n1:OUTPUT/n1:EDISyntax/n1:Group"
        found = root.find(xpath,ns)
        for node in found.iterfind('.//n1:Name', ns):
            if node.text == self.o.get() :
                while("StoreLimit" not in node.tag) :
                    node = node.getnext()
                if "Link" in node.getnext().tag :       #checks if there is link tag initially
                    node = node.getnext()
                else :                                  #else inserts link tag
                    link = ET.Element('{http://www.stercomm.com/SI/Map}Link')
                    node.addnext(link)
                    node = link
                    node.text = self.get_id()
                break
            
        tree.write(fname_2.get(),encoding = "UTF-8",xml_declaration = True)
        fname_2.set("")
        self.i.set("")
        self.o.set("")
        tkMessageBox.showinfo("Successful","The link is created",parent = self)
        
    def createWidgets(self) :                           # creates widgets for Tab2(Linker)
        
        Label(self,text = "Open the file :").grid(row = 0,column = 0,sticky = 'W',pady = 10)
        Entry(self,textvariable = fname_2,width = 40,state = 'readonly').grid(row = 0,column = 1,sticky = 'W',pady = 10)
        Button(self,text = "Browse" ,command = self.open_file).grid(row = 0,column = 2,sticky = 'W',pady = 10,padx = 35)

        Label(self,text = "Operation name in Input :").grid(row = 1,column = 0,sticky = 'W')
        self.i = Combobox(self,postcommand = self.getinput)
        self.i.grid(row = 1,column = 1,padx = 30,pady = 15)

        Label(self,text = "Operation name in Output :").grid(row = 2,column = 0,sticky = 'W')
        self.o = Combobox(self,postcommand = self.getoutput)
        self.o.grid(row = 2,column = 1,padx = 30)
                     
        Button(self,text = "Form link",command = self.form_link).grid(row = 3,column = 0,pady = 25,sticky = 'E')
        Button(self,text = "Quit",command = self.quit).grid(row = 3,column = 1,pady = 25,sticky = 'E')
        
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    
class Application(Frame):
    def createWidgets(self) :
        note = Notebook(self)

        tab1 = Frame(note)
        tab2 = Frame(note)

        Tab1(tab1)
        Tab2(tab2)

        note.add(tab1, text = "Edit lxml", compound=TOP)
        note.add(tab2, text = "Linker")

        note.grid()
        
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()



root = Tk()


## variables used in the Tab1
name = StringVar(master = root)
fname = StringVar(master = root)
I_or_O = IntVar(master = root)
option = IntVar(master = root)
position = IntVar(master = root)
condition = StringVar(master = root)

## variables used in the Tab2
fname_2 = StringVar(master = root)

app = Application()
app.master.title("Automated Map Development")
app.master.minsize(500, 435)
app.master.protocol(name = "WM_DELETE_WINDOW",func=app.master.quit)

app.mainloop()
root.destroy()

