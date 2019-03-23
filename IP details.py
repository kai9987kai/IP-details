from tkinter import *
import requests

def main_window():


    txt1 = input("Ip:")




    main_api = 'http://api.ipstack.com/' + txt1 + '?access_key=9d54083e1b722c6251e74180c95c7375'
    url = main_api
    json_data = requests.get(url).json()


    window = Tk()
    lbl1 = Label(window, text=("ip: " + json_data["ip"])).pack()
    lbl2 = Label(window, text=("type: " + json_data["type"])).pack()
    lbl3 = Label(window, text=("continent_code: " + json_data["continent_code"])).pack()
    lbl4 = Label(window, text=("continent_name: " + json_data["continent_name"])).pack()
    lbl5 = Label(window, text=("country_code: " + json_data["country_code"])).pack()
    lbl6 = Label(window, text=("country_name: " + json_data["country_name"])).pack()
    lbl7 = Label(window, text=("region_code: " + json_data["region_code"])).pack()
    lbl8 = Label(window, text=("region_name: " + json_data["region_code"])).pack()
    lbl9 = Label(window, text=("city: " + json_data["city"])).pack()
    lbl10 = Label(window, text=("zip: " + json_data["zip"])).pack()
    window.mainloop()




main_window()
