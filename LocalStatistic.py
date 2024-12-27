from tkinter.ttk import *
from customtkinter import *
from tkinter import filedialog
from tkinter import IntVar
from tkinter import messagebox
import pandas as pd
import ldb
import time


#_______GLOBAL VARIABELS
full_tests = ''
test_steps = ''
tested_qty = ''
passed_qty = ''
failed_qty = ''
aborted_qty = ''
#_______END GLOBAL VARIABLES


#_______FUNCTIONS___________

def click_browse_button()-> None:
    entry_db_file.delete(0, END)
    db_address = filedialog.askopenfilename()
    entry_db_file.insert(0, db_address)
   

def click_connect_button():
    global full_tests
    global test_steps 
    global label_general_statistic
    global simple_tests_filtered

    db_address = entry_db_file.get()
    full_tests, test_steps, status = ldb.connect_to_db(db_address)
    simple_tests_filtered = test_steps
    label_connected.configure(text = status, fg_color = '#06B420') if status == 'OK' else label_connected.configure(text = status,fg_color = '#C9C6C6')
    statistics = ldb.get_general_statistic(full_tests)
    label_general_statistic.configure(text = f'Tested - {statistics[0]}\tPassed - {statistics[1]}\tFailed - {statistics[2]}\tAborted - {statistics[3]}')

    for i in treview_full_tests.get_children():
        treview_full_tests.delete(i)

    table_columns = list(full_tests)
    r_data = full_tests.to_numpy().tolist()

    for column in table_columns:
        treview_full_tests.column(column, anchor='center')
        treview_full_tests.heading(column, text=column)
    for row in r_data:
        v = [ r for r in row]
        treview_full_tests.insert("",'end', values = v)


def click_filter_button():
    global label_general_statistic
    global full_tests
    global test_steps
    global full_tests_filtered
    global simple_tests_filtered

    
    if date_checked.get() ==1 and serial_number_checked.get() == 0:
        from_date = entry_date_from.get()
        till_date = entry_date_to.get()
        full_tests_filtered = ldb.get_data_for_period(full_tests, from_date,till_date)
        simple_tests_filtered = ldb.get_data_for_period(test_steps,from_date,till_date)

        statistics = ldb.get_general_statistic(full_tests_filtered)
        label_general_statistic.configure(text = f'Tested - {statistics[0]}\tPassed - {statistics[1]}\tFailed - {statistics[2]}\tAborted - {statistics[3]}')
        r_data = full_tests_filtered.to_numpy().tolist()

        for i in treview_full_tests.get_children():
            treview_full_tests.delete(i)

        for row in r_data:
            v = [r for r in row]
            treview_full_tests.insert("", 'end', values=v)

    elif date_checked.get()==0 and serial_number_checked.get() == 1:
        serial_number = entry_serial_number.get()
        full_tests_filtered = ldb.get_data_for_sn(full_tests,serial_number)
        statistics = ldb.get_general_statistic(full_tests_filtered)
        label_general_statistic.configure(text = f'Tested - {statistics[0]}\tPassed - {statistics[1]}\tFailed - {statistics[2]}\tAborted - {statistics[3]}')
        r_data = full_tests_filtered.to_numpy().tolist()
    
        for i in treview_full_tests.get_children():
            treview_full_tests.delete(i)
        
        for row in r_data:
            v = [r for r in row]
            treview_full_tests.insert("", 'end', values=v)

def click_export_to_excel_btn():
    full_tests_filtered.to_excel(f"Export.xlsx")

def click_show_info_btn():
    global test_steps
    for i in treview_full_tests.selection():
        serial_number = treview_full_tests.item(i)['values'][0]
        test_date_time = treview_full_tests.item(i)['values'][1]
        test_details_df = ldb.get_test_details(test_steps, serial_number,test_date_time)
        test_details_r_data = test_details_df.to_numpy().tolist()

        #____INFO WINDOW_______________
        info_window = CTkToplevel(main)
        info_window.geometry('1000x900')
        info_window.title(f'{serial_number} test data')
        
        triview_test_data = Treeview(master=info_window, selectmode='browse', columns=('SN','DateTime','SimpleTestName','SimpleTestStatus','SimpleTestLL','SimpleTestValue','SimpleTestHL'))
        triview_test_data.heading('SN', text='Serial Number')
        triview_test_data.heading('DateTime', text= 'Date time')
        triview_test_data.heading('SimpleTestName', text = 'Step Name')
        triview_test_data.heading('SimpleTestStatus', text= 'Status')
        triview_test_data.heading('SimpleTestLL', text='Low Limit')
        triview_test_data.heading('SimpleTestValue', text='Value')
        triview_test_data.heading('SimpleTestHL', text='High Limit')
        triview_test_data['show']='headings'
        triview_test_data.place(relx=0, rely=0, relheight=0.98, relwidth=0.98)
        vertical_scroll = Scrollbar(triview_test_data, orient='vertical', command= triview_test_data.yview)
        vertical_scroll.pack(side='right', fill='y')
        triview_test_data.configure(yscrollcommand=vertical_scroll.set)

        for i in triview_test_data.get_children():
            triview_test_data.delete(i)
        for row in test_details_r_data:
            v = [r for r in row]
            triview_test_data.insert("",'end', values=v)

def click_statistic_details_btn():
    
    display_df = ldb.generate_tests_statistic(simple_tests_filtered)
    
    steps_statistic_window = CTkToplevel(main)
    steps_statistic_window.geometry('1000x900')
    steps_statistic_window.title('Statistic Data')

    frame_buttons = CTkFrame(master=steps_statistic_window, fg_color='#A1D4F7', border_color='#000000', border_width=3)
    frame_buttons.place(relx = 0, rely = 0, relwidth=1, relheight =0.1)

    frame_data = CTkFrame(master=steps_statistic_window,  fg_color='#A1D4F7', border_color='#000000', border_width=3 )
    frame_data.place(relx = 0, rely = 0.1, relwidth = 1, relheight = 0.9)

    button_details = CTkButton( master= frame_buttons, text='DETAILS', fg_color='#284B63', corner_radius=3, command= click_details_in_statistic_window)
    button_details.grid(row = 0, column = 0, padx = 5, pady = 5)

    global treview_steps_statistic
    treview_steps_statistic = Treeview(master= frame_data, selectmode='browse', columns=('SimpleTestName','Passed', 'Failed', 'Aborted'))
    treview_steps_statistic['show'] = 'headings'
    treview_steps_statistic.heading('SimpleTestName', text='Step Name')
    treview_steps_statistic.heading('Passed', text='Passed')
    treview_steps_statistic.heading('Failed', text='Failed')
    treview_steps_statistic.heading('Aborted', text='Aborted')
    treview_steps_statistic.place(relx=0, rely=0, relwidth=1, relheight=0.98)
    scrollbar_statistic = Scrollbar(master=frame_data, orient='vertical', command= treview_steps_statistic.yview)
    scrollbar_statistic.pack(side='right', fill= 'y')
    treview_steps_statistic.configure( yscrollcommand=scrollbar_statistic.set)

    for i in treview_steps_statistic.get_children():
        treview_steps_statistic.delete(i)
    
    for row in display_df.to_numpy().tolist():
        v = [r for r in row]
        treview_steps_statistic.insert("",'end', values=v)



def click_details_in_statistic_window():
    
    for i in treview_steps_statistic.selection():
        data_frame = ldb.show_all_status_for_step(treview_steps_statistic.item(i)['values'][0],simple_tests_filtered)

        step_status_window = CTkToplevel(main)
        step_status_window.geometry('1000x900')
        step_status_window.title(treview_steps_statistic.item(i)['values'][0])

        treview_step_status = Treeview(master=step_status_window, selectmode='browse', columns=('index','DateTime','SN', 'Status','Value'))
        treview_step_status['show'] = 'headings'
        treview_step_status.heading('index', text='order')
        treview_step_status.heading('DateTime', text='Date Time')
        treview_step_status.heading('SN', text='Serial Number')
        treview_step_status.heading('Status', text='Step Status')
        treview_step_status.heading('Value', text='Value')
        treview_step_status.place( relx= 0 , rely= 0 , relheight=0.99, relwidth=0.99)
        scroll_bar_step_status = Scrollbar(master= treview_step_status, orient= 'vertical', command=treview_step_status.yview)
        scroll_bar_step_status.pack(side='right', fill='y')
        treview_step_status.configure(yscrollcommand= scroll_bar_step_status.set)

        #insert data in table
        for i in treview_step_status.get_children():
            treview_step_status.delete(i)
        for row in data_frame.to_numpy().tolist():
            v = [ r for r in row]
            treview_step_status.insert("",'end', values=v)

        try:
            if ldb.check_if_float(treview_steps_statistic.item(i)['values'][2]):
                ldb.show_graph(treview_steps_statistic.item(i)['values'][0], simple_tests_filtered)
        except:
            print("Can t build grapghic")
    

#_______END FUNCTIONS________


#_______GUI VISUALISATION____
main = CTk()
main.geometry('1000x900')
main.title("Statistic aplication")

frame_menu = CTkFrame(master= main,  fg_color='#A1D4F7')
frame_menu.place(relx = 0, rely = 0, relwidth = 1, relheight = 0.05,)

frame_filter = CTkFrame(master= main, fg_color='#BF1EF3', border_color='#000000', border_width=2)
frame_filter.place(relx = 0, rely = 0.05, relwidth = 0.5, relheight = 0.2,)

frame_general_statistic = CTkFrame( master= main, fg_color='#BF1EF3', border_color='#000000',border_width=2)
frame_general_statistic.place(relx = 0.5, rely = 0.05, relwidth = 0.5, relheight = 0.2)

frame_information = CTkFrame( master= main, fg_color='#2C5CC4')
frame_information.place(relx=0, rely= 0.3 , relheight = 0.7, relwidth = 1)

entry_db_file = CTkEntry(master= frame_menu, corner_radius= 3, border_color='#000000', width= 300)
entry_db_file.grid(row = 0, column = 0, sticky = 'WE')

button_browse = CTkButton(master= frame_menu, corner_radius= 5, text='Browse DB',fg_color='#284B63', width=100,command= click_browse_button )
button_browse.grid(row = 0, column = 1, padx = 1, pady = 1, sticky = 'WE')

button_connect = CTkButton(master= frame_menu, corner_radius= 5, text='Connect',fg_color='#284B63', width=100, command= click_connect_button )
button_connect.grid( row = 0, column = 2, padx = 10)

label_connected = CTkLabel(master= frame_menu, width=100, bg_color='#C9C6C6', text='No Data')
label_connected.grid( row = 0, column = 3)

label_general_statistic = CTkLabel( master= frame_general_statistic, text='EMPTY')
label_general_statistic.grid( row = 0, column = 0)


button_detailed_statistic = CTkButton( master= frame_general_statistic, text= 'STATISTIC DETAILS',fg_color='#284B63', command=click_statistic_details_btn )
button_detailed_statistic.grid( row = 1, column = 0, padx = 3)


date_checked = IntVar()
serial_number_checked = IntVar()

chekbutton_date = Checkbutton( master= frame_filter, variable= date_checked, onvalue=1, offvalue=0, text= "Filter by period:")
chekbutton_date.grid(row=0, column=0, pady=5 )

chekbutton_serial = Checkbutton( master= frame_filter, variable= serial_number_checked, onvalue=1, offvalue=0, text='Filter by serial number:')
chekbutton_serial.grid(row=0, column= 1, pady= 5)

button_filter = CTkButton(master= frame_filter, corner_radius=3, fg_color='#284B63', text="FILTER", command= click_filter_button )
button_filter.grid( row = 3, column = 0,padx = 3, pady = 5, sticky = 'we')

button_show_info = CTkButton(master= frame_filter, corner_radius=3, fg_color='#284B63', text='SHOW DETAILS',command= click_show_info_btn)
button_show_info.grid(row = 4, column = 0, padx = 3,pady = 1, sticky= 'we')

button_export_excel = CTkButton(master = frame_filter, corner_radius=3, fg_color='#284B63', text= "Export EXCEL" , command= click_export_to_excel_btn) #TO DO COMMAND)
button_export_excel.grid(row = 3, column = 1, padx = 3, pady = 3, sticky = 'we')

entry_date_from = CTkEntry( master= frame_filter, width= 200 , corner_radius=3, placeholder_text='DATE FROM:')
entry_date_from.grid( row = 1, column = 0, pady = 5, padx = 5)

entry_date_to = CTkEntry(master= frame_filter, width= 200, corner_radius=3, placeholder_text='DATE TO:')
entry_date_to.grid(row = 2, column = 0, pady = 5, padx = 5)

entry_serial_number = CTkEntry(master= frame_filter, width= 200, corner_radius=3, placeholder_text="SERIAL NUMBER")
entry_serial_number.grid(row = 1, column = 1, padx = 5)




treview_full_tests = Treeview(frame_information, selectmode='browse', columns=('SN','DateTime','Status'))
treview_full_tests.heading('SN', text='SN')
treview_full_tests.heading('DateTime', text='DateTime')
treview_full_tests.heading('Status', text='Status')
treview_full_tests['show'] = 'headings'
treview_full_tests.place(relx=0.01, rely=0.01, relwidth=0.98, relheight= 0.9)
vertical_scrollbar = Scrollbar(main, orient='vertical', command= treview_full_tests.yview)
vertical_scrollbar.pack(side='right', fill='y')
treview_full_tests.configure(yscrollcommand=vertical_scrollbar.set)



main.mainloop()
# _______END OF GUI____________