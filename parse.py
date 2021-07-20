import json
import os
from time import sleep

import source

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.PhantomJS()
driver.get("http://www.lvva-raduraksti.lv/pases/index.php?temavb=ru#")

all_data = {}

PAGE = source.PAGE


def main():
    global var
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "d"))
        )
    finally:  # element or elements — big diff., i'nt noticed  | "S" letter ~attention
        data = []
        surnames = []
        names = []
        father_names = []
        bdate = []
        bplace = []
        Place = []
        try:
            print(PAGE)
            script = 'if(!(isNaN(page))){page=page*1+' + str(PAGE) + ';loadData();}'
            driver.execute_script(script)
            file_thing(0)
            sleep(2)
            for a in range(PAGE, 10252):
                print("a: " + str(a))
                for i in range(1, 51):
                    print("i: " + str(i))
                    for j in range(6):
                        element = driver.find_element_by_xpath(
                            "//table[@class='grid']/tbody/tr[" + str(i + 1) + "]/td[" + str(j + 1) + "]")
                        element = element.text
                        if j == 0:
                            surnames.insert(i, element)
                        elif j == 1:
                            names.insert(i, element)
                        elif j == 2:
                            father_names.insert(i, element)
                        elif j == 3:
                            bdate.insert(i, element)
                        elif j == 4:
                            bplace.insert(i, element)
                        elif j == 5:
                            Place.insert(i, element) # append на insert
                    lala = {"Фамилия": surnames[i-1], "Имя": names[i-1], "Отчество": father_names[i-1],
                            "Дата рождения": bdate[i-1], "Место рождения": bplace[i-1],
                            "Место приписки": Place[i-1]} # 'i-1' на 'i'
                    data.insert(i, lala)
                var = a
                all_data["item" + str(a)] = data
                if a != 0 and a % 1000 == 0:
                    back_up(all_data)
                next_page()
                print("Sleeping...")  # Мб с cmd запустить(?)
                sleep(2)  # Мб стоит пождать больше, вдруг не все успевает догрузиться. Хотя, вряд ли
        except:
            save_data(all_data, var)
            file_thing(1)
        finally:
            save_data(all_data, var)
            file_thing(1)


def next_page():
    script = 'if(!(isNaN(page))){page=page*1+1;loadData();}'
    driver.execute_script(script)
    # sleep(3)
    # driver.get_screenshot_as_file("screenshot"+str(a+1)+".png")
    print("Page is turned.")


def save_data(all_data, var):
    with open("LVA-archive.json", "a", encoding="UTF-8") as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=1, separators=(',', ': '))
    with open("source.py", "w", encoding="UTF-8") as source_f:
        source_f.write("PAGE = " + str(var))


def back_up(data):
    with open("LVA-archive(res).json", "w", encoding="UTF-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=1, separators=(',', ': '))


def file_thing(argument):
    if argument == 1:
        try:
            os.remove("parse_lock.lock")
        except FileNotFoundError:
            pass
    elif argument == 0:
        open("parse_lock.lock", "w")


if __name__ == '__main__':
    main()
