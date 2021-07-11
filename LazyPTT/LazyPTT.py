import threading
import requests
import bs4
import time
import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from bs4 import BeautifulSoup
from PIL import Image, ImageTk 

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# get the newest page of board
def get_page(text):
    start = text.find('index')
    end = text.find('.html')
    pagenum = text[start + 5 : end]
    return int(pagenum) + 1

def get_list(plate):
    rs = requests.session()
    load = {'from' : '/bbs/' + str(plate) + '/index.html',
            'yes' : 'yes'}
    response = rs.post('https://www.ptt.cc/ask/over18', verify = False, data = load)
    pooling = bs4.BeautifulSoup(response.text,"html.parser")
    allpage = pooling.select('.btn.wide')[1]['href']
    start_page = get_page(allpage)
    listpage = []
    for i in range(start_page, start_page - 8, -1):
        url = 'https://www.ptt.cc/bbs/' + plate + '/index{}.html'.format(i)
        listpage.append(url)    
    return listpage

# get the ptt's boards
def get_board():
    response = requests.get("https://www.ptt.cc/bbs/hotboards.html")
    pooling = bs4.BeautifulSoup(response.text,"html.parser")
    boards = pooling.find_all('div','board-name')
    board = []
    for i in range(len(boards)):
        board.append(boards[i].text.strip())
    return board

# get date
def get_data(URL,theme,num):
    ptt_headers = {'cookie': 'over18=1;'}
    response = requests.get(URL, headers = ptt_headers)
    pooling = bs4.BeautifulSoup(response.text,"html.parser")
    titles = pooling.find_all('div','title')
    if num == 1:
        today = time.strftime("%m/%d").lstrip('0')
    if num == 0:
        days = ["31","28","31","30","31","30","31","31","30","31","30","31"]
        today = time.strftime("%m/%d").lstrip('0')
        a = today.find('/')
        if today == "1/01":
            today = "12/31"
        elif int(today[a+1:])-1 == 0:
            today = str(int(today[:a])-1) + '/' + str(days[int(today[:a])-2])
        else:
            if len(str(int(today[a+1:])-1)) == 1:
                today = today[:a+1] + '0' + str(int(today[a+1:])-1)
            else:
                today = today[:a+1] + str(int(today[a+1:])-1)

    date_divs = pooling.find_all('div','r-ent')
    date_check = []
    for day in date_divs:
        date_check.append(day.find('div','date').text.strip() == today)
    for i in range(len(titles)):
        if date_check[i] == True and theme == '':
            data.append(titles[i].text.strip())
            continue
        if date_check[i] == True and theme in titles[i].text and "Re" not in titles[i].text:
            data.append(titles[i].text.strip())
        if date_check[i] == True and len(theme) > 5:
            if theme in titles[i].text and "Re" not in titles[i].text:
                goal = str(titles[i])
                start = goal.find('href=')
                end = goal.find('html')
                link1.bind("<Button-1>", lambda e: callback("https://www.ptt.cc" + goal[start+6:end] + "html"))

# using threadds to speed up
def get_output(list_page,theme,num):
    threads = []
    global data,info
    data = []
    info = ''
    for i in range(len(list_page)):
        threads.append(threading.Thread(target = get_data(list_page[i],theme,num)))
        threads[i].start() 
    for i in range(len(list_page)):
        threads[i].join()
    info = '\n'.join(data)

def get_final_today():
    plate = pttcombobox.get()
    theme = var2.get()
    link1.bind("<Button-1>", lambda e: callback("https://www.ptt.cc/bbs/" + plate + "/index.html"))
    get_output(get_list(plate),theme,1)
    t = tk.Text(root, width=40, height=8, font=("Helvetica", 15), selectforeground='red')
    t.place(x=30, y=280)
    t.insert('insert',"Total: ")
    t.insert('insert',len(data))
    t.insert('insert','\n\n')
    t.insert('insert',info)

def get_final_yes():
    plate = pttcombobox.get()
    theme = var2.get()
    link1.bind("<Button-1>", lambda e: callback("https://www.ptt.cc/bbs/" + plate + "/index.html"))
    get_output(get_list(plate),theme,0)
    t = tk.Text(root, width=40, height=8, font=("Helvetica", 15), selectforeground='red')
    t.place(x=30, y=280)
    t.insert('insert',"Total: ")
    t.insert('insert',len(data))
    t.insert('insert','\n\n')
    t.insert('insert',info)

def callback(url):
    webbrowser.open_new(url)

# using tkinter
root = tk.Tk()
root.title('Lazy PTT')
root.geometry('500x500')

link1 = tk.Label(root, text="PPT Hyperlink", fg="blue", cursor="hand2")
link1.pack()
link1.bind("<Button-1>", lambda e: callback("https://www.ptt.cc/bbs/hotboards.html"))

canvas = tk.Canvas(root, height=500, width=750)
im = Image.open("ptt.png")
im_tk = ImageTk.PhotoImage(im)
canvas.create_image(250, 250, image=im_tk)
canvas.pack()

comboboxList = get_board()
pttcombobox = ttk.Combobox(root, state='normal', width=35, font = ("Helvetica", 11))
pttcombobox['values'] = comboboxList

line0 = tk.Label(root, bg = 'light cyan', text = "Board : ", font = ("Helvetica", 12)) 
line0.place(x=80, y=100)
pttcombobox.place(x=140, y=100)
pttcombobox.current(0)

line2 = tk.Label(root, bg = 'light cyan', text = "Theme : ", font = ("Helvetica", 12))
line2.place(x=80, y=150)

var2 = tk.StringVar()
b2 = tk.Entry(root, textvariable = var2, font=("Helvetica", 12), show=None, width=33)
b2.place(x=140, y=150)

a = tk.Button(root, bg='light cyan', text="Search! Yesterday", width=25, height=2, command=get_final_yes)
a.place(x=50, y=200)
b = tk.Button(root, bg='light cyan', text="Search! Today", width=25, height=2, command=get_final_today)
b.place(x=270, y=200)

root.mainloop()