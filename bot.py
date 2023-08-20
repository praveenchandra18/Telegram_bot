from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
import telebot

Token="6493114823:AAFHPswOsiLQ9Gy_8jLrUPOcpxx8FqEBL08"
bot=telebot.TeleBot(Token,parse_mode=None)

path=Service('C:\chromedriver.exe')
option=webdriver.ChromeOptions()
option.add_argument('--headless')
link="https://webstream.sastra.edu/sastraparentweb/"
browser=webdriver.Chrome(service=path,options=option)


user_data={}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,"Hello this is a sastra bot, Please send message '/setup' to complete the setup process ")

@bot.message_handler(commands=['setup'])
def setup(message):
    bot.send_message(message.chat.id,"Enter the Id and DoB with space. Make sure your Id and DoB is right to avoid issues in near future")
    bot.register_next_step_handler(message,setup_process)

def setup_process(message):
    mess=message.text
    mess=mess.split()
    try:
        user_data[message.chat.id]=[mess[0],mess[1]]
        bot.send_message(message.chat.id,"Now every time you need the bunk data just send '/getmyatt' to the bot")
    except:
        bot.send_message(message.chat.id,"Something is not right with your ID or DOB. Make sure your Id and DoB is right to avoid issues in near future. Try /setup again")

@bot.message_handler(commands=['getmyatt'])
def get_my_attandance(message):
    try:
        bot.send_message(message.chat.id,"Please enter the Captcha")
        browser.get(link)
        sleep(2)
        captcha=browser.find_element(By.XPATH,'/html/body/form/div[3]/table/tbody/tr[4]/td[2]/img')
        with open(str(message.chat.id)+'.png','wb') as f:
            f.write(captcha.screenshot_as_png)
        with open('captcha.png','rb') as f:
            bot.send_photo(message.chat.id,f)
        bot.register_next_step_handler(message,inner_function)
    except:
        bot.send_message(message.chat.id,"Server is down, Please try again later")
    
def inner_function(message):
    try:
        mes=message.text
        id=browser.find_element(By.XPATH,"/html/body/form/div[3]/table/tbody/tr[1]/td[2]/input")
        id.send_keys(user_data[message.chat.id][0])
        password=browser.find_element(By.XPATH,"/html/body/form/div[3]/table/tbody/tr[2]/td[2]/input[1]")
        password.send_keys(user_data[message.chat.id][1])
        captcha_input=browser.find_element(By.XPATH,"/html/body/form/div[3]/table/tbody/tr[3]/td[2]/input")
        captcha_input.send_keys(mes)
        browser.find_element(By.XPATH,"/html/body/form/div[3]/table/tbody/tr[6]/td/input").click()
        sleep(10)
        name= browser.find_element(By.XPATH,'//*[@id="form01"]/table[1]/tbody/tr[2]/td[2]')
    except:
        bot.send_message(message.chat.id,"""Please enter the captcha right. If still there is an issue, There might be an issue in entering your id and dob. So start the /setup process again""")

    try:
        name=name.text
        browser.find_element(By.XPATH,"/html/body/form/div/div/div[1]/div/div[1]/div[1]/div[14]/a/font").click()
        sleep(5)
        data=browser.find_elements(By.CLASS_NAME,"ui-widget-header")
        data=data[2].text.split()
        total_hours=int(data[1])
        present=int(data[2])
        absent=int(data[3])
        percent=float(data[4])
        sending_message="You must be "+ name + f". In total hours {total_hours}, you are present in {present} hours and absent is {absent} hours. "
        if(percent>80):
            sending_message=sending_message+ f" You can bunk {int((present/0.8)-total_hours)} classes and still your attandance would be 80 %. "
        else:
            sending_message=sending_message+f" You cannot bunk classes. You need to attend {int((total_hours*0.8-present)/0.2)} hours without any bunks to make it 80 %."
        bot.send_message(message.chat.id,sending_message)
    except:
        bot.send_message(message.chat.id,"There might be an internal server issue. Please kindly co-operate and try again")

@bot.message_handler()
def normal_message(message):
    string="""I cannot understand what you say. I think this will help you.
/start to know about me.
/setup to setup your ID and DoB
/getmyatt to get your bunk data if you already completed the /setup process"""
    bot.send_message(message.chat.id,string)

bot.polling()