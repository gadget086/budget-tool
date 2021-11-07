import os
import sys
from   random import sample
from   string import ascii_letters
import sqlite3
import wx
import wx.lib.mixins.listctrl as listmix

app_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
dbFile = os.path.join(app_dir, "Database.db3")     # dbFile

def create_db():

    con = sqlite3.connect(dbFile)

    cur = con.cursor()

    try:
        cur.execute("""CREATE TABLE Database (Ids INTEGER PRIMARY KEY,
                                              Name TEXT,
                                              Surname TEXT,
                                              Age TEXT,
                                              Email TEXT,
                                              Phone TEXT)""")
    except sqlite3.OperationalError:
        print ("Unable to create the database "
               "(maybe because it already exists ?)")

        return

    con.commit()

    try:
        cur.execute("""CREATE TABLE accounts (code INTEGER PRIMARY KEY, name TEXT, type INT)""")
    except sqlite3.OperationalError:
        print ("Unable to create the database "
               "(maybe because it already exists ?)")
        return

    con.commit()

    sql = """INSERT INTO Database (Name,
                                   Surname,
                                   Age,
                                   Email,
                                   Phone)
                           VALUES (?, ?, ?, ?, ?)"""

    cur.execute("BEGIN")

    #------------

    for i in range(6000):
        cur.execute(sql, ["".join(sample(ascii_letters, 10))]*5)
    con.commit()

class dbConnection():
    def __init__(self):
        self.database_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
        dbFile = os.path.join(self.database_dir, "Database.db3")
        self.con = sqlite3.connect(dbFile)
        self.cur = self.con.cursor()

    def OnNumberRows(self):
        self.cur.execute("SELECT count(Name) FROM Database")
        return self.cur.fetchall()[0][0]


    def OnOneRow(self, qui):
        sql = "SELECT * FROM Database WHERE Ids=?"
        self.cur.execute(sql, (qui,))

        return self.cur.fetchall()[0]


    def OnAll(self):
        self.cur.execute("SELECT * from Database")
        return self.cur.fetchall()

    def deleteRow(self,row):
        sql = "DELETE FROM Database WHERE Ids=?"
        self.cur.execute(sql, (row,))
        self.con.commit()


class sumTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent)
        #self.SetBackgroundColour((0,159,184))
        self.cats = ["Bills","Food","Car","Gifts","Health","Misc Savings"]
        gs = wx.GridSizer(2,3,20,20)
        gs.Add(wx.StaticBox(self,-1,self.cats[0]),0,wx.EXPAND)
        gs.Add(wx.StaticBox(self,-1,self.cats[1]),0,wx.EXPAND)
        gs.Add(wx.StaticBox(self,-1,self.cats[2]),0,wx.EXPAND)
        gs.Add(wx.StaticBox(self,-1,self.cats[3]),0,wx.EXPAND)
        gs.Add(wx.StaticBox(self,-1,self.cats[4]),0,wx.EXPAND)
        gs.Add(wx.StaticBox(self,-1,self.cats[5]),0,wx.EXPAND)
        self.SetSizer(gs)

class newCatFrame(wx.Frame):
    def __init__(self, title, parent):
        wx.Frame.__init__(self, parent=parent, title=title)
        self.parent = parent
        self.SetSize(200,50)
        self.dlg = wx.TextEntryDialog(self, "Name:","New Category")
        self.dlg.SetValue("Category")
        if(self.dlg.ShowModal() == wx.ID_OK):
            self.parent.data.append(self.dlg.GetValue())
            self.parent.lst.Set(self.parent.data)
            self.parent.edit_btn.Enable()
        self.Destroy()

class editCatFrame(wx.Frame):
    def __init__(self, title, parent,category):
        wx.Frame.__init__(self, parent=parent, title=title)
        self.parent = parent
        self.SetSize(200,50)
        self.dlg = wx.TextEntryDialog(self, "Name:","Edit Category")
        self.dlg.SetValue(category)
        if(self.dlg.ShowModal() == wx.ID_OK):
            idx = self.parent.data.index(category)
            self.parent.data[idx] = self.dlg.GetValue()
            self.parent.lst.Set(self.parent.data)
        self.Destroy()

class catTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        self.data = []

        btn_stack = wx.BoxSizer(wx.VERTICAL)
        outer = wx.BoxSizer(wx.HORIZONTAL)

        new_btn = wx.Button(self, label="New")
        new_btn.Bind(wx.EVT_BUTTON, self.newCategory)

        remove_btn = wx.Button(self,label="Remove")
        remove_btn.Bind(wx.EVT_BUTTON, self.removeCategory)

        self.edit_btn = wx.Button(self, label="Edit")
        self.edit_btn.Bind(wx.EVT_BUTTON, self.editCategory)
        self.edit_btn.Disable()

        self.lst = wx.ListBox(self, size=(100,-1),choices=self.data, style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.onListBox, self.lst)

        self.selected = None
        btn_stack.Add(new_btn, 0, wx.ALL, 5)
        btn_stack.Add(remove_btn, 0, wx.ALL, 5)
        btn_stack.Add(self.edit_btn,0,wx.ALL,5)

        outer.Add(btn_stack,0,wx.EXPAND)
        outer.Add(self.lst,1,wx.EXPAND)

        self.SetSizer(outer)

    def newCategory(self, event):
        self.ntf = newCatFrame(title="New Category",parent=self)
    
    def removeCategory(self, event):
        if self.selected and self.data:
            self.data.remove(self.selected)
            self.lst.Set(self.data)
            if self.data == []:
                self.edit_btn.Disable()

    def editCategory(self, event):
        if self.selected in self.data:
            self.etf = editCatFrame(title="Edit Category",parent=self, category=self.selected)


    def onListBox(self, event):
        self.selected = event.GetEventObject().GetStringSelection()

class virtualList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT|wx.LC_VIRTUAL|
                             wx.LC_HRULES|wx.LC_VRULES)
        self.con = self.GetParent().con
        self.data = self.con.OnAll()
        self.SetItemCount(self.con.OnNumberRows())
        listmix.ListCtrlAutoWidthMixin.__init__(self)


    def OnGetItemText(self, row, col):
        data = self.data[row+1]
        return str(data[col])

class transTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent)

        self.con = dbConnection()

        btn_stack = wx.BoxSizer(wx.VERTICAL)
        outer = wx.BoxSizer(wx.HORIZONTAL)

        new_btn = wx.Button(self, label="New")
        new_btn.Bind(wx.EVT_BUTTON, self.newCategory)

        remove_btn = wx.Button(self,label="Remove")
        remove_btn.Bind(wx.EVT_BUTTON, self.removeCategory)

        self.edit_btn = wx.Button(self, label="Edit")
        self.edit_btn.Bind(wx.EVT_BUTTON, self.editCategory)
        self.edit_btn.Disable()

        self.lst = virtualList(self)
        self.lst.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListBox)
        for n, c in enumerate(("A", "B", "C", "D", "E", "F")):
            self.lst.InsertColumn(n, c)
            self.lst.SetColumnWidth(n, 100)

        self.selected = None
        btn_stack.Add(new_btn, 0, wx.ALL, 5)
        btn_stack.Add(remove_btn, 0, wx.ALL, 5)
        btn_stack.Add(self.edit_btn,0,wx.ALL,5)

        outer.Add(btn_stack,0,wx.EXPAND)
        outer.Add(self.lst,1,wx.EXPAND)

        self.SetSizer(outer)

    def newCategory(self, event):
        self.ntf = newCatFrame(title="New Category",parent=self)
    
    def removeCategory(self, event):
        if self.selected:
            print("remove ids: %s"%self.selected)
            self.con.deleteRow(self.selected)
            self.lst.data = self.con.OnAll()
            self.lst.Refresh()
            self.lst.Select(self.selectedItem,on=0)



    def editCategory(self, event):
        if self.selected in self.data:
            self.etf = editCatFrame(title="Edit Category",parent=self, category=self.selected)


    def onListBox(self, event):
        ind = event.GetIndex()
        item = self.lst.GetItem(ind)
        self.selected = int(item.GetText())
        self.selectedItem = item.GetId()
        print(self.selected)

class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title="Budget Tool", size=(800,600))
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        sum_tab = sumTab(nb)
        cat_tab = catTab(nb)
        trans_tab = transTab(nb)

        nb.AddPage(sum_tab, "Summary")
        nb.AddPage(cat_tab, "Categories")
        nb.AddPage(trans_tab, "Transactions")

        sizer = wx.BoxSizer()
        sizer.Add(nb,1,wx.EXPAND)
        p.SetSizer(sizer)
        self.Show()

class MyApp(wx.App):
    def OnInit(self):
        self.SetAppName("Sample_two")
        return True
        
if __name__ == "__main__":
    create_db()
    app = MyApp(redirect=False)
    frame = MainFrame()
    app.MainLoop()