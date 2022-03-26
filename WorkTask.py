#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 12:10:39 2021
@author: tsubasa
"""

import sqlite3,time,datetime
from tkinter import Tk,Frame,Label,StringVar,Button,Entry,Toplevel,ttk,font,Text,messagebox

class TaskWindow:
    def __init__(self, master):
        self.master = master
        self.FirstFrame = Frame(master)
        master.title("Task")
        master.geometry('980x600')
        Label(self.FirstFrame, text="Status").grid(row=1,column=1)
        #Set up search box at the top
        self.tkvar = StringVar(master)
        self.myOption = ttk.Combobox(self.FirstFrame, width = 20, textvariable = self.tkvar)
        self.myOption.grid(row = 1, column = 2)
        self.myOption['values'] = ["Pending","Completed","ToDo"]
        self.myOption.insert(0,"Pending")
        self.my_tree = ttk.Treeview(self.FirstFrame,height=20)
        self.my_tree.grid(row=2,column=1,rowspan = 8,columnspan=4)
        #set up columns for the tree view
        self.my_tree['columns'] = ('OrderID','Start_Time','End_Time','Description', 'Est_Time' , 'Actual_Time', 'Status')
        self.my_tree.column("#0",width=0,stretch="NO")
        self.my_tree.column("OrderID",width=0,stretch="NO")
        self.my_tree.column("Start_Time",width=145)
        self.my_tree.column("End_Time",width=145)
        self.my_tree.column("Description",width=200)
        self.my_tree.column("Est_Time",width=80)
        self.my_tree.column("Actual_Time",width=80)
        self.my_tree.column("Status",width=80)
        #set up column Name
        self.my_tree.heading('Start_Time', text='Start_Time', anchor='center')
        self.my_tree.heading('End_Time', text='End_Time', anchor='center')
        self.my_tree.heading('Description', text='Description', anchor='center')
        self.my_tree.heading('Est_Time', text='Est_Min', anchor='center')
        self.my_tree.heading('Actual_Time', text='Actual_Min', anchor='center')
        self.my_tree.heading('Status', text='Status', anchor='center')
        #refresh the task list
        self.refresh_task_list("Pending")
        #Add buttons on the top (customer search)
        Button(self.FirstFrame, text="Filter", width=20, command=self.filter_by_status).grid(row = 1, column =3,padx=30)
        Button(self.FirstFrame, text="Refresh Time", width=20, command=self.RefreshStartTime).grid(row = 1,column = 4,padx=30)
        #Add buttons on the right
        Button(self.FirstFrame, text="Add Task", width=20, command=self.add_task).grid(row = 4, column =5,padx=30)
        Button(self.FirstFrame, text="Delete Task", width=20, command=self.delete_task).grid(row = 5, column =5,padx=30)
        Button(self.FirstFrame, text="Notes", width=20, command=self.Task_Note).grid(row = 6,column =5,padx=30)
        Button(self.FirstFrame, text="Complete", width=20, command=self.mark_as_complete).grid(row = 7,column = 5,padx=30)
        #Add buttons at the bottom
        Button(self.FirstFrame, text="Start", width=20, command=self.start_working).grid(row = 10,column =2,padx=0,pady=30)
        Button(self.FirstFrame, text="Pause", width=20, command=self.pause_working).grid(row = 10,column =3,padx=0,pady=30)
        Button(self.FirstFrame, text="TimeTable", width=20, command=self.Show_TimeTable).grid(row = 10,column =4 ,padx=0,pady=30)
        #Add timer info at the bottom
        self.show_lapse_time = Label(self.FirstFrame, text="")
        self.show_lapse_time.grid(row=11,column=2)
        #double click event
        self.my_tree.bind('<Double-Button-1>',self.viewclick)
        self.FirstFrame.pack(fill='both', expand=True)
        self.nwin=None # prevent muitiple window
        # reminder for not tracking 1000 ms
        self.pop_up_check=root.after(120000, self.Check_Tracking)
        
    def refresh_task_list(self,show_status):
        self.my_tree.delete(*self.my_tree.get_children())
        for row in cur.execute("SELECT TaskID,Start_Time,End_Time,Description,Est_Time,Actual_Time,Status \
                               FROM MyTask WHERE Status='{}' ORDER BY date(Start_Time) DESC,Start_Time ASC".format(show_status)).fetchall():
            try:
                self.my_tree.insert(parent="",index="end",iid=row[0],\
                               values=(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
            except:
                pass

    def add_task(self):
        self.add_task_window = Toplevel(self.master)
        self.app = NewTask(self.add_task_window)
        
    def delete_task(self):
        x = self.my_tree.selection()[0]
        cur.execute("DELETE FROM MyTask WHERE TaskID={}".format(x))
        con.commit()
        self.my_tree.delete(x)
        
    def Task_Note(self):
        self.task_note_window = Toplevel(self.master)
        self.app = NoteWindow(self.task_note_window)
    
    def mark_as_complete(self):#Pending,Completed,ToDo
        x = self.my_tree.selection()[0]
        selected = self.my_tree.focus()
        if self.my_tree.set(selected,'Status') == "Pending":
            cur.execute("UPDATE MyTask SET Status='Completed' WHERE TaskID={}".format(x))
            con.commit()
            self.my_tree.set(selected,'Status',"Completed")
        elif self.my_tree.set(selected,'Status') == "Completed":
            cur.execute("UPDATE MyTask SET Status='ToDo' WHERE TaskID={}".format(x))
            con.commit()
            self.my_tree.set(selected,'Status',"ToDo")
        elif self.my_tree.set(selected,'Status') == "ToDo":
            cur.execute("UPDATE MyTask SET Status='Pending' WHERE TaskID={}".format(x))
            con.commit()
            self.my_tree.set(selected,'Status',"Pending")
    
    def RefreshStartTime(self):
        for rowid in self.my_tree.selection():
            self.Est_Time = self.my_tree.set(rowid,"Est_Time")
            self.Act_Time = self.my_tree.set(rowid,"Actual_Time")
            cur.execute("UPDATE MyTask SET Start_Time=datetime('now','localtime'),End_Time=datetime('now','+{0} minutes') WHERE TaskID={1}"\
             .format(float(self.Est_Time)-float(self.Act_Time),rowid))
            con.commit()
            app.refresh_task_list("Pending")

    def filter_by_status(self):
        show_status = self.tkvar.get()
        if show_status == "" :
            show_status= "Pending"
            self.myOption.insert(0,"Pending")
        self.refresh_task_list(show_status)

    def start_working(self):
        self.working_item = self.my_tree.selection()[0]
        self.start_time = time.time()
        self.update_timer()
    
    def pause_working(self):
        root.after_cancel(self.running_timer)
        self.show_lapse_time['text'] = ""
        duration = (time.time() - self.start_time)/60
        cur.execute("INSERT INTO TimeTrack(TaskID, Start_Time, End_Time) VALUES ({},'{}',datetime('now','localtime'))".format(self.working_item,datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')))
        duration = round(float(cur.execute("SELECT SUM(JULIANDAY(TimeTrack.End_Time) - JULIANDAY(TimeTrack.Start_Time)) FROM TimeTrack GROUP BY TimeTrack.TaskID HAVING TimeTrack.TaskID={}".format(self.working_item)).fetchone()[0]*24*60),2)
        cur.execute("UPDATE MyTask SET Actual_Time={} WHERE TaskID={}".format(duration,self.working_item))
        con.commit()
        del self.working_item,self.start_time
        self.refresh_task_list("Pending")
               
    def update_timer(self):
       self.show_lapse_time['text'] = "Time lapsed for: {} min.".format(round((time.time() - self.start_time)/60,0))
       self.running_timer = root.after(60000, self.update_timer) # run itself again after 1000 ms

    def viewclick(self,dummy):
        self.update_task_info = Toplevel(self.master)
        self.app = AmendTask(self.update_task_info)     
    
    def Show_TimeTable(self):
        self.show_timetable_output = Toplevel(self.master)
        self.app = TimeTable(self.show_timetable_output)
    
    def Check_Tracking(self):
        if self.show_lapse_time['text'] == "":
            print("You are not tracking!!!")
            popup_root = Tk()
            popup_root.withdraw()
            messagebox.showinfo('Warning', 'You are not tracking!')
            popup_root.destroy()
        self.pop_up_check = root.after(300000, self.Check_Tracking) # run itself again after 1000 ms


class NewTask:#for adding new task
    def __init__(self, master):
        self.master = master
        master.geometry("500x180")
        self.ThrFrame = Frame(master)
        Label(self.ThrFrame, text="Start Time",font=(None, 16)).grid(row=1,column=1)
        self.Start_Time = Entry(self.ThrFrame)#Start Time
        self.Start_Time.grid(row=1,column=2)
        self.Lastest_EndTime = cur.execute("SELECT Max(End_Time) as End_Time from MyTask").fetchone()[0]
        self.Start_Time.insert(0, self.Lastest_EndTime) #Start time is the end of the lastest task
        Label(self.ThrFrame, text="Description",font=(None, 16)).grid(row=2,column=1)
        self.Description = Entry(self.ThrFrame)#Task_Name
        self.Description.grid(row=2,column=2)
        Label(self.ThrFrame, text="Est Min",font=(None, 16)).grid(row=3,column=1)
        self.Est_Time = Entry(self.ThrFrame)#Estimate Time
        self.Est_Time.grid(row=3,column=2)
        Button(self.ThrFrame, text="Confirm", width=20, command=self.confirm_newtask).grid(row=5,column=2,pady=20)
        self.ThrFrame.pack()
    def confirm_newtask(self):
        cur.execute("INSERT INTO MyTask (Description, Est_Time, Actual_Time, Status, Start_Time,End_Time)\
        VALUES ('{0}','{1}',0,'Pending','{2}',datetime('{2}','+{1} minutes'));"\
            .format(self.Description.get(),self.Est_Time.get(),self.Start_Time.get()))
        con.commit()
        app.refresh_task_list("Pending")
        self.master.destroy()


class AmendTask:#for changing task detail
    def __init__(self, master):
        self.master = master
        master.geometry("500x180")
        self.ThrFrame = Frame(master)
        Label(self.ThrFrame, text="Start Time",font=(None, 16)).grid(row=1,column=1)
        self.StartTime = Entry(self.ThrFrame)
        self.StartTime.grid(row=1,column=2)
        self.Start_Time_Stamp = cur.execute("SELECT Start_Time FROM MyTask WHERE TaskID={}"\
                                            .format(app.my_tree.selection()[0])).fetchone()[0]
        self.StartTime.insert(0, self.Start_Time_Stamp)
        Label(self.ThrFrame, text="Description",font=(None, 16)).grid(row=2,column=1)
        self.Description = Entry(self.ThrFrame)
        self.Description.grid(row=2,column=2)
        self.Description.insert(0, app.my_tree.set(app.my_tree.selection()[0],"Description"))
        Label(self.ThrFrame, text="Est_Min",font=(None, 16)).grid(row=3,column=1)
        self.Est_Time = Entry(self.ThrFrame)
        self.Est_Time.grid(row=3,column=2)
        self.Est_Time.insert(0, app.my_tree.set(app.my_tree.selection()[0],"Est_Time"))
        Button(self.ThrFrame, text="Confirm", width=20, command=self.confirm_task_update).grid(row=5,column=2,pady=20)
        self.ThrFrame.pack()
    def confirm_task_update(self):
        self.Act_Time = cur.execute("SELECT Actual_Time FROM MyTask WHERE TaskID ={}".format(app.my_tree.selection()[0])).fetchone()[0]
        cur.execute("UPDATE MyTask SET Start_Time='{0}',Description='{1}',\
                    Est_Time={2},End_Time=datetime('{0}','+{3} minutes') WHERE TaskID={4}"\
         .format(self.StartTime.get(),self.Description.get(),self.Est_Time.get(),float(self.Est_Time.get())-self.Act_Time,app.my_tree.selection()[0]))
        con.commit()
        app.refresh_task_list("Pending")
        self.master.destroy()
        

class NoteWindow: #Show notes for the task
    def __init__(self, master):
        self.master = master
        self.AddressFrame = Frame(master)
        master.title("Notes")
        master.geometry('800x450')
        self.Address_Info = cur.execute("SELECT Notes from MyTask WHERE TaskID = {}"\
                                        .format(app.my_tree.selection()[0])).fetchall()[0]
        if len(self.Address_Info)>0:
            self.Address_Info = str(self.Address_Info[0])
        else:
            self.Address_Info = ""
        self.Address_Entry_Box = Text(self.AddressFrame,width=85,height=20)
        self.Address_Entry_Box.insert(1.0,self.Address_Info)
        self.Address_Entry_Box.grid(row=1,column=1,padx=50,ipady=0)
        Button(self.AddressFrame, text="Save", width=20, command=self.Note_Confirm).grid(row = 2,column =1)
        self.AddressFrame.pack(fill='both', expand=True)

    def Note_Confirm(self):
        cur.execute("UPDATE MyTask SET Notes='{}' WHERE TaskID={}"\
                    .format(self.Address_Entry_Box.get(1.0,'end-1c'),app.my_tree.selection()[0]))
        con.commit()
        self.master.destroy()


class TimeTable:#showing time tracking table
    def __init__(self, master):
        self.master = master
        master.title("TimeTable")
        master.geometry("800x300")
        self.TimeTableFrame = Frame(master)
        self.my_TimeTree = ttk.Treeview(self.TimeTableFrame)
        self.my_TimeTree.grid(row=2,column=1,rowspan = 6,columnspan=4)
        #set up columns for the tree view
        self.my_TimeTree['columns'] = ('OrderID', 'Start_Time', 'End_Time', 'Description')
        self.my_TimeTree.column("#0",width=0,stretch="NO")
        self.my_TimeTree.column("OrderID",width=0,stretch="NO")
        self.my_TimeTree.column("Start_Time",width=200,stretch="NO")
        self.my_TimeTree.column("End_Time",width=200)
        self.my_TimeTree.column("Description",width=300)
        #set up column Name
        self.my_TimeTree.heading('Start_Time', text='Start_Time', anchor='center')
        self.my_TimeTree.heading('End_Time', text='End_Time', anchor='center')
        self.my_TimeTree.heading('Description', text='Description', anchor='center')
        self.my_TimeTree.bind('<Double-Button-1>',self.TimeTableviewclick)
        # RawOutput= cur.execute("SELECT TimeTrack.Start_Time,TimeTrack.End_Time,MyTask.description FROM TimeTrack INNER JOIN MyTask on TimeTrack.TaskID=MyTask.TaskID ORDER BY date(Start_Time) DESC,Start_Time ASC").fetchall()
        # CanvasOutput = '\n'.join([str(x) for x in RawOutput])
        # Label(self.TimeTableFrame, text="{}".format(""),font=(None, 16)).grid(row=1,column=1)
        #Fill TreeView with TimeTable
        self.refresh_TimeTable()
        # for row in cur.execute("SELECT TimeTrack.TrackRowID,TimeTrack.Start_Time,TimeTrack.End_Time,MyTask.description \
        #                        FROM TimeTrack INNER JOIN MyTask on TimeTrack.TaskID=MyTask.TaskID\
        #                            ORDER BY date(TimeTrack.Start_Time) DESC,TimeTrack.Start_Time ASC").fetchall():
        #     try:
        #         self.my_TimeTree.insert(parent="",index="end",iid=row[0],\
        #                        values=(row[0],row[1],row[2],row[3]))
        #     except Exception as E:
        #         pass
        #         print(E)
        self.my_TimeTree.pack(fill="both", expand=True)
        self.TimeTableFrame.pack(fill="both", expand=True)


    def refresh_TimeTable(self):
        self.my_TimeTree.delete(*self.my_TimeTree.get_children())
        for row in cur.execute("SELECT TimeTrack.TrackRowID,TimeTrack.Start_Time,TimeTrack.End_Time,MyTask.description \
                               FROM TimeTrack INNER JOIN MyTask on TimeTrack.TaskID=MyTask.TaskID\
                                   ORDER BY TimeTrack.Start_Time DESC").fetchall():
            try:
                self.my_TimeTree.insert(parent="",index="end",iid=row[0],\
                               values=(row[0],row[1],row[2],row[3]))
            except Exception as E:
                pass
                print(E)
                
    def TimeTableviewclick(self,dummy):
        self.update_timetable = Toplevel(self.master)
        self.app = EditTimeTable(self.update_timetable)  
        
        
class EditTimeTable:#for changing Timetable detail
    def __init__(self, master):
        self.master = master
        master.geometry("500x180")
        self.ThrFrame = Frame(master)
        Label(self.ThrFrame, text="Start Time",font=(None, 16)).grid(row=1,column=1)
        self.StartTime = Entry(self.ThrFrame)
        self.StartTime.grid(row=1,column=2)
        self.StartTime.insert(0, app.app.my_TimeTree.set(app.app.my_TimeTree.selection()[0],"Start_Time"))
        Label(self.ThrFrame, text="End Time",font=(None, 16)).grid(row=2,column=1)
        self.EndTime = Entry(self.ThrFrame)
        self.EndTime.grid(row=2,column=2)
        self.EndTime.insert(0, app.app.my_TimeTree.set(app.app.my_TimeTree.selection()[0],"End_Time"))
        Button(self.ThrFrame, text="Confirm", width=20, command=self.confirm_time_entry).grid(row=4,column=2,pady=20)
        Button(self.ThrFrame, text="Delete", width=20, command=self.delete_time_entry).grid(row=5,column=2,pady=100)
        self.ThrFrame.pack()
        

    def confirm_time_entry(self):
        cur.execute("UPDATE TimeTrack SET Start_Time='{0}',End_Time='{1}' WHERE TrackRowID={2}"\
         .format(self.StartTime.get(),self.EndTime.get(),app.app.my_TimeTree.selection()[0]))
        con.commit()
        app.app.refresh_TimeTable()
        self.master.destroy()
    def delete_time_entry(self):
        pass
    

def Exit_Programme():
    root.after_cancel(app.pop_up_check)
    root.destroy()
    


con = sqlite3.connect('TaskData.db')
cur = con.cursor()
root = Tk()
default_font = font.nametofont("TkDefaultFont") #font.families()
default_font.configure(size = 11)
root.option_add("*Font", default_font)
app = TaskWindow(root)
root.protocol("WM_DELETE_WINDOW", Exit_Programme)
root.mainloop()
con.commit()
con.close()



#Depreciated code
# cur.execute("CREATE TABLE MyTask (TaskID INTEGER PRIMARY KEY,DueDate date, Description text, Est_Time float, Actual_Time float, Status text ,Notes text);")
#Insert Statment
# cur.execute("INSERT INTO MyTask(DueDate, Description, Est_Time, Actual_Time, Status, Notes) \
#             VALUES ('2021-10-23','Write Programme',1,0.5,'Pending','This is a test')")
# cur.execute("CREATE TABLE TimeTrack (TrackRowID INTEGER PRIMARY KEY,TaskID INTEGER, Start_Time time, End_Time time);")
# cur.execute("INSERT INTO TimeTrack(TaskID, Start_Time, End_Time) VALUES (10,'{}',datetime('now','localtime'))".format(datetime.datetime.now()))
# cur.execute("SELECT * FROM MyTask").fetchall()
# cur.execute("SELECT TimeTrack.*,MyTask.description FROM TimeTrack INNER JOIN MyTask on TimeTrack.TaskID=MyTask.TaskID ORDER BY datetime(Start_Time)").fetchall()
# cur.execute("SELECT * FROM TimeTrack").fetchall()
# cur.execute("SELECT date(Start_Time) FROM TimeTrack").fetchall()
# cur.execute("INSERT INTO MyTask(DueDate, Description, Est_Time, Actual_Time, Status) \
#     VALUES ('{}','{}','{}', 0, '{}')".format(self.DueDate.get(),self.Description.get(),self.Est_Time.get(),'Pending'))
