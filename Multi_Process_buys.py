# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

from multiprocessing import Process, Manager
from time import sleep
import sys
import sched
import random as rd 
import numpy as np


class buy_ticket(Process):

	def __init__(self, web_name, userid, userpwd, process_id = 0, 
		chromedriver_path = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'):
		super(buy_ticket, self).__init__()
		self.web_name = web_name
		self.userid = userid
		self.userpwd = userpwd
		self.process_id = process_id
		self.chromedriver_path = chromedriver_path # 定位到你的ChromeDriver地址
		print(f"Process [{self.process_id}]: Start. \n")

	def start_driver(self):
		driver = webdriver.Chrome(executable_path = self.chromedriver_path)

		driver.get(self.web_name)

		# 登录
		# 选择密码登录
		driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[1]/div[1]/div/div[2]/div").click()
		# 输入用户名（手机号）
		driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[2]/div[1]/div[1]/div/input").send_keys(str(self.userid))
		# 输入密码
		driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/input").send_keys(str(self.userpwd))

		login_Xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[2]/button'
		driver.find_element(By.XPATH, login_Xpath).click()

		sleep(3) # 确保页面跳转

	# 定义点击按钮的函数
	def click_button(self):
    	        pay_now_button.click()
    	        print(f"Process [{self.process_id}] :Clicked the button! \n")

	def click_button(self):
		driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div[3]/div[1]").click()
		# 选择 支付宝
		driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div[4]/div[1]").click()
		sleep(1)
		# 定位“立即付款”按钮
		element_ID = '//*[@id="root"]/div/div[2]/div/div/button'
		pay_now_button = driver.find_element(By.XPATH, element_ID)

		# 定期点击按钮
		while True:
    		click_button()
    		try:
        		# 等待页面跳转
        		WebDriverWait(driver, 0.5).until(staleness_of(pay_now_button))
        		print(f"Process [{self.process_id}]: Page has refreshed, stopping the script. \n")
        		sys.exit(0)
        		break
    		except:
        		# 页面未跳转
        		pass

def start_buy_ticket(process_id, web_name, userid, userpwd, chromedriver_path):

    worker = buy_ticket(process_id, web_name, userid, userpwd, chromedriver_path)
    worker.start()
    return worker


def listening_process(process_id, buy_ticket_pool, event):
	
	while True:

		event.wait()

		(exited_process, web_name, userid, userpwd, chromedriver_path) = buy_ticket_pool.get(exited = True)

		new_process = start_buy_ticket(exited_process, web_name, userid, userpwd, chromedriver_path)

		buy_ticket_pool.replace(exited_process, new_process)

		event.clear()

	print(f"Monitoring process {process_id} exiting...")


if __name__ == "__main__":
    # Set up the buy ticket pool with numbers of url workers
    chromedriver_path = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe' # 你的ChromeDriver位置
    url = ["", ""] # 多个引号内填入多个购票地址
    userid = '' # 购票手机号
    userpwd = '' # 购票密码
    processes_num = len(url) # 根据网页数量设置启动进程数

    buy_ticket_pool = multiprocessing.Pool(processes = processes_num)
    for i in range(len(url)):
        buy_ticket_pool.apply_async(start_buy_ticket, args=(f"Process {i}", url[i], userid, userpwd, chromedriver_path))

    # Set up the monitoring pool with processes
    monitoring_pool = multiprocessing.Pool(processes = processes_num)
    event = multiprocessing.Event()
    for i in range(processes_num):
        monitoring_pool.apply_async(listening_process, args=(f"Monitor {i}", buy_ticket_pool, event))

    # Wait for the Selenium workers to finish
    buy_ticket_pool.close()
    buy_ticket_pool.join()

    # Terminate the monitoring processes
    monitoring_pool.terminate()
    monitoring_pool.join()

'''

注意浏览器都没有设置自动关闭，如果进程因为崩溃而停止，会有备用进程跟进并继承参数；
如果进程正常停止，则代表页面成功跳转到了支付界面，需要手动扫码支付，然后手动关闭浏览器！

'''
