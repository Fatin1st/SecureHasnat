import datetime
import sqlite3
import pyperclip
import tkinter.ttk as ttk
from tkinter import *
from tkcalendar import DateEntry
import tkinter.messagebox as mb
import random


# password-generating func
def generate_password(range1):

    characters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "+", "¦", "@", "*", "#", "ç", "°", "%", "§", "&", "¬", "/", "|", "(", "¢", ")", "=", "?", "`", "~", "ü", "[", "]", "ö", "ä", "{", "}", ";", ":", "_", ">", "£", "'", "^", ",", ".", "-", "$", "é", "à", "¨", "è", "§", "°"]
    random_characters = []
    
    for i in range(int(range1)+1):
        i = random.choice(characters)
        random_characters.append(i)

    random.shuffle(random_characters)

    password = "".join([str(item) for item in random_characters])
    return password


# Connecting to the Database
connector = sqlite3.connect("SecureHasnat.db")
cursor = connector.cursor()

connector.execute(
	'CREATE TABLE IF NOT EXISTS SecureHasnat (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Date DATETIME, Password TEXT, Website TEXT, Username TEXT, Range INT)'
)
connector.commit()

# Functions
def list_all_passwords():
	global connector, table

	table.delete(*table.get_children())

	all_data = connector.execute('SELECT * FROM SecureHasnat')
	data = all_data.fetchall()

	for values in data:
		table.insert('', END, values=values)

def copy_password():
	global table
	global password

	if not table.selection():
		mb.showerror('No info selected', 'Please select a row from the table to copy it')

	current_selected_password = table.item(table.focus())
	values = current_selected_password['values']
	password.set(values[2])
	selected_password = password.get()

	pyperclip.copy(selected_password)
	mb.showinfo('Pasword Copied', f"Your password-					\n\n\n{selected_password}\n\n\nCopied!					")


def view_password_details():
	global table
	global date, password, web, username, pass_range

	if not table.selection():
		mb.showerror('No info selected', 'Please select a password from the table to view its details')

	current_selected_password = table.item(table.focus())
	values = current_selected_password['values']

	that_date = datetime.date(int(values[1][:4]), int(values[1][5:7]), int(values[1][8:]))

	date.set_date(that_date) ; password.set(values[2]) ; web.set(values[3]) ; username.set(values[4]) ; pass_range.set(values[5])


def clear_fields():
	global web, password, username, pass_range, date, table

	today_date = datetime.datetime.now().date()

	web.set('') ; password.set('') ; username.set(''), pass_range.set(10), date.set_date(today_date)
	table.selection_remove(*table.selection())


def remove_password():
	if not table.selection():
		mb.showerror('No record selected!', 'Please select a record to delete!')
		return

	current_selected_password = table.item(table.focus())
	values_selected = current_selected_password['values']

	surety = mb.askyesno('Are you sure?', f'Are you sure that you want to delete the record of {values_selected[3]}')

	if surety:
		connector.execute('DELETE FROM SecureHasnat WHERE ID=%d' % values_selected[0])
		connector.commit()

		list_all_passwords()
		mb.showinfo('Record deleted successfully!', 'The record you wanted to delete has been deleted successfully')


def remove_all_passwords():
	surety = mb.askyesno('Are you sure?', 'Are you sure that you want to delete all the passwords from the database?', icon='warning')

	if surety:
		table.delete(*table.get_children())

		connector.execute('DELETE FROM SecureHasnat')
		connector.commit()

		clear_fields()
		list_all_passwords()
		mb.showinfo('All Info deleted', 'All the info were successfully deleted')
	else:
		mb.showinfo('Ok then', 'The task was aborted and no info was deleted!')


def add_another_password():
	global date, password, web, username, pass_range
	global connector

	if not date.get() or not web.get()  or not username.get() or not pass_range.get():
		mb.showerror('Fields empty!', "Please fill all the missing fields before pressing the add button!")
	else:
		generated_password = generate_password(pass_range.get())
		connector.execute(
		'INSERT INTO SecureHasnat (Date, Password, Website, Username) VALUES (?, ?, ?, ?)',
		(date.get_date(), generated_password, web.get(), username.get())
		)
		connector.commit()

		clear_fields()
		list_all_passwords()
		
		pyperclip.copy(generated_password)
		mb.showinfo('Info Saved', f"Your password-					\n\n\n{generated_password}\n\n\nCopied!					")



def edit_password():
	global table

	def edit_existing_password():
		global date, web, password, username, pass_range
		global connector, table

		current_selected_password = table.item(table.focus())
		contents = current_selected_password['values']

		connector.execute('UPDATE SecureHasnat SET Date = ?, Password = ?, Website = ?, Username = ? Range = ? WHERE ID = ?',
		                  (date.get_date(), password.get(), web.get(), username.get(), pass_range.get(), contents[0]))
		connector.commit()

		clear_fields()
		list_all_passwords()

		mb.showinfo('Data edited', 'We have updated the data and stored in the database as you wanted')
		edit_btn.destroy()
		return

	if not table.selection():
		mb.showerror('No info selected!', 'You have not selected any info in the table for us to edit; please do that!')
		return

	view_password_details()

	edit_btn = Button(data_entry_frame, text='Edit info', font=btn_font, width=30,
	                  bg=hlb_btn_bg, command=edit_existing_password)
	edit_btn.place(x=10, y=395)


def selected_password_to_words():
	global table

	if not table.selection():
		mb.showerror('No info selected!', 'Please select an info from the table for us to read')
		return

	current_selected_password = table.item(table.focus())
	values = current_selected_password['values']

	message = f'Your info can be read like: \n"You saved the password {values[2]} for {values[3]} for {values[4]} on {values[1]}"'

	mb.showinfo('Your Password Info', message)


def passwords_to_words_before_adding():
	global date, web, password, username, pass_range

	if not date or not web or not username or not pass_range:
		mb.showerror('Incomplete data', 'The data is incomplete, meaning fill all the fields first!')

	message = f'Your info can be read like: \n"You saved the password {password.get()} for {web.get()} for {username.get()} on {date.get_date()}"'

	add_question = mb.askyesno('Read your record like: ', f'{message}\n\nShould I add it to the database?')

	if add_question:
		add_another_password()
	else:
		mb.showinfo('Ok', 'Please take your time to add this record')


# Backgrounds anf Fonts
dataentery_frame_bg = '#7F7FFF'
buttons_frame_bg = '#9898F5'
hlb_btn_bg = '#7A7AC5'

lbl_font = ('Georgia', 13)
entry_font = 'Times 13 bold'
btn_font = ('Gill Sans MT', 13)

# Initializing the GUI window
root = Tk()
root.title('SecureHasnat')
root.geometry('1200x550')
root.resizable(0, 0)

Label(root, text='SecureHasnat', font=('Noto Sans CJK TC', 15, 'bold'), bg=hlb_btn_bg).pack(side=TOP, fill=X)

# StringVar and DoubleVar and IntVar variables
web = StringVar()
password = StringVar()
pass_range = IntVar(value=10)
username = StringVar(value='Fatin')

# Frames
data_entry_frame = Frame(root, bg=dataentery_frame_bg)
data_entry_frame.place(x=0, y=30, relheight=0.95, relwidth=0.25)

buttons_frame = Frame(root, bg=buttons_frame_bg)
buttons_frame.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.21)

tree_frame = Frame(root)
tree_frame.place(relx=0.25, rely=0.26, relwidth=0.75, relheight=0.74)

# Data Entry Frame
Label(data_entry_frame, text='Date (M/DD/YY) :', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=50)
date = DateEntry(data_entry_frame, date=datetime.datetime.now().date(), font=entry_font)
date.place(x=160, y=50)

Label(data_entry_frame, text='Website           :', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=130)
Entry(data_entry_frame, font=entry_font, width=31, text=web).place(x=10, y=160)

Label(data_entry_frame, text='Range\t             :', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=230)
Entry(data_entry_frame, font=entry_font, width=14, text=pass_range).place(x=160, y=230)

Label(data_entry_frame, text='Username           :', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=295)
Entry(data_entry_frame, font=entry_font, width=31, text=username).place(x=10, y=325)

Button(data_entry_frame, text='Add password', command=add_another_password, font=btn_font, width=30,
       bg=hlb_btn_bg).place(x=10, y=395)
Button(data_entry_frame, text='Convert to words before adding', font=btn_font, width=30, bg=hlb_btn_bg).place(x=10,y=450)

# Buttons' Frame
Button(buttons_frame, text='Delete Info', font=btn_font, width=25, bg=hlb_btn_bg, command=remove_password).place(x=30, y=5)

Button(buttons_frame, text='Clear Fields in DataEntry Frame', font=btn_font, width=25, bg=hlb_btn_bg,
       command=clear_fields).place(x=335, y=5)

Button(buttons_frame, text='Delete All Info', font=btn_font, width=25, bg=hlb_btn_bg, command=remove_all_passwords).place(x=640, y=5)

Button(buttons_frame, text='Copy Password', font=btn_font, width=25, bg=hlb_btn_bg,
       command=copy_password).place(x=30, y=65)

Button(buttons_frame, text='Edit Selected Info', command=edit_password, font=btn_font, width=25, bg=hlb_btn_bg).place(x=335,y=65)

Button(buttons_frame, text='Convert Info to a sentence', font=btn_font, width=25, bg=hlb_btn_bg,
       command=selected_password_to_words).place(x=640, y=65)

# Treeview Frame
table = ttk.Treeview(tree_frame, selectmode=BROWSE, columns=('ID', 'Date', 'Password', 'Website', 'Username'))

X_Scroller = Scrollbar(table, orient=HORIZONTAL, command=table.xview)
Y_Scroller = Scrollbar(table, orient=VERTICAL, command=table.yview)
X_Scroller.pack(side=BOTTOM, fill=X)
Y_Scroller.pack(side=RIGHT, fill=Y)

table.config(yscrollcommand=Y_Scroller.set, xscrollcommand=X_Scroller.set)

table.heading('ID', text='S No.', anchor=CENTER)
table.heading('Date', text='Date', anchor=CENTER)
table.heading('Password', text='Password', anchor=CENTER)
table.heading('Website', text='Website', anchor=CENTER)
table.heading('Username', text='Username', anchor=CENTER)

table.column('#0', width=0, stretch=NO)
table.column('#1', width=50, stretch=NO)
table.column('#2', width=95, stretch=NO)  
table.column('#3', width=200, stretch=NO)  
table.column('#4', width=325, stretch=NO)  
table.column('#5', width=210, stretch=NO) 

table.place(relx=0, y=0, relheight=1, relwidth=1)

list_all_passwords()

# Finalizing the GUI window
root.update()
root.mainloop()
