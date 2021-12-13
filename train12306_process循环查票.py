# @Time : 2021/9/12 7:26
# @Author : 吴喜钟
# @File : train12306_process循环查票.py
# @Software: PyCharm

import csv
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import ChromeOptions
from slider_spide import acceleration

'''12306自动买票'''


class TrainSpider(object):
    def __init__(self, start_station, destinty_station, train_date, ticket_infos, passengers):
        """
            :param start_station: 出发地
            :param destinty_station: 目的地
            :param train_date: 出发日期
            :param ticket_infos: 车次以及坐席 {"G6325": ['O', 'M']}
            :param passengers: 乘客信息
        """
        # 12306登陆的url
        self.url = 'https://kyfw.12306.cn/otn/resources/login.html'
        # 乘客确认信息界面url
        self.passengers_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        # 网上支付url
        self.pay_url = 'https://kyfw.12306.cn/otn//payOrder/init?random=1631263890402'
        # 支付方式url
        self.payway_url = 'https://epay.12306.cn/pay/payGateway'
        # 出发站
        self.start_station = start_station
        # 到达站
        self.destinty_station = destinty_station
        # 购票出发日期
        self.train_date = train_date
        # 查票界面的url
        self.query_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'
        # 扫码成功后的个人url
        self.personal_url = 'https://kyfw.12306.cn/otn/view/index.html'
        # 定义存放站名及代号的字典
        self.stations_dict = {}
        # 初始化站名及代号
        self.station_code()
        # 把出发站转成相应的代号
        self.start_station_code = self.stations_dict[self.start_station].strip()
        # 把到达站转成相应等代号
        self.destinty_station_code = self.stations_dict[self.destinty_station].strip()
        # 车次及坐席的字典
        self.ticket_infos = ticket_infos
        # 乘客信息
        self.passengers = passengers
        # 定义一个空的坐席
        self.seat_type = None
        # 定义flag标志
        # self.flag = False
        # 设置浏览器,防止selenium被检测出来
        self.options = ChromeOptions()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 加载浏览器驱动
        self.driver = webdriver.Chrome(options=self.options)

    def logic(self):
        ''''登录12306'''
        # 登陆成功后的个人url self.personal_url = 'https://kyfw.12306.cn/otn/view/index.html'
        self.driver.get(self.url)
        # 窗口最大化
        self.driver.maximize_window()
        # 显示等待
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, "J-login")))
        # 输入登录账号
        self.driver.find_element_by_id("J-userName").send_keys("13456789012")
        # 输入登录密码
        self.driver.find_element_by_id("J-password").send_keys("wxz1234567890")
        # 点击立即登录
        login_button = self.driver.find_element_by_id("J-login")
        self.driver.execute_script('arguments[0].click();', login_button)
        # 隐式等待滑块界面加载
        self.driver.implicitly_wait(10)
        # 定位滑块标签
        block_tag = self.driver.find_element_by_id("nc_1_n1z")
        # 以字典形式获取滑块的尺寸
        block_dic = block_tag.size
        # 获取滑块的宽度
        block_width = block_dic['width']
        # 定位滑槽
        chute_tag = self.driver.find_element_by_id("nc_1__scale_text")
        # 以字典形式获取滑槽的尺寸
        chute_dic = chute_tag.size
        # 获取滑槽的长度
        chute_length = chute_dic['width']
        # 滑块需滑动的总距离
        total_distance = chute_length - block_width
        # 前面五分之三需滑动的距离
        forwad_distance = round(3 / 5 * total_distance)
        # 后面剩余一部分的距离
        back_distance = total_distance - forwad_distance
        # 创建鼠标行为链
        actions = ActionChains(self.driver)
        while True:
            # 按住滑块
            actions.click_and_hold(on_element=block_tag)
            # 鼠标按住滑块不放滑动前面五分之三的距离(forwad_distance)
            actions.move_by_offset(forwad_distance, 0)
            # 调用加速度位移函数
            distance_lst = acceleration(back_distance)
            for every_distance in distance_lst:
                actions.move_by_offset(every_distance, 0)
            # 提交行为链
            actions.perform()
            try:
                WebDriverWait(self.driver, 10).until(EC.url_contains(self.personal_url))
                print('登录成功')
            except:
                continue
            else:
                break

    # 将站名及对应代号读取并存放字典中
    def station_code(self):
        with open(r'stations.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for line in reader:
                # print(line)
                # 获取站名
                name = line['name']
                # 获取站名代号
                code = line['code']
                self.stations_dict[name] = code
            # print(self.stations_dict)

    def open_ticket_message(self):
        '''打开查票界面并关闭弹窗'''
        # 打开查票的url
        self.driver.get(self.query_url)
        # 隐式等待
        self.driver.implicitly_wait(12)
        # 关闭弹窗
        self.driver.find_element_by_id('qd_closeDefaultWarningWindowDialog_id').click()

    def check_tickets(self):
        '''选择车次坐席购买'''
        # 定位出发站输入框，必须定位到隐藏的那个标签
        start_station_input = self.driver.find_element_by_id('fromStation')
        # 定位到达站输入框，必须定位到隐藏的那个标签
        destinty_station_input = self.driver.find_element_by_id('toStation')
        # 向输入框中输入出发站
        self.driver.execute_script('arguments[0].value="%s"' % self.start_station_code, start_station_input)

        '''不能输入站名，输入站名查询不到提示查询超时'''
        # self.driver.execute_script('arguments[0].value="%s"'%self.start_station,start_station_input)

        # 向输入框中输入到达站
        self.driver.execute_script('arguments[0].value="%s"' % self.destinty_station_code, destinty_station_input)

        '''不能输入站名，输入站名查询不到，提示输入超时'''
        # self.driver.execute_script('arguments[0].value="%s"'%self.destinty_station,destinty_station_input)

        # 向输入框中同时分别输入出发站和到达站
        # self.driver.execute_script('arguments[0].value="{}";arguments[1].value="{}"'.format(self.start_station_code,self.destinty_station_code),start_station_input,destinty_station_input)

        # 定位购票出发日期输入框
        train_date_input = self.driver.find_element_by_id('train_date')
        # 向购票出发日期输入框中输入购票日期
        self.driver.execute_script('arguments[0].value="%s"' % self.train_date, train_date_input)
        # 显式等待输入出发地、目的地、出发日期
        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, 'train_date'), self.train_date))
        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, 'fromStation'), self.start_station_code))
        WebDriverWait(self.driver, 1000).until(
            EC.text_to_be_present_in_element_value((By.ID, 'toStation'), self.destinty_station_code))

        # 定位查询按钮
        query_button = self.driver.find_element_by_id('query_ticket')
        # 点击查询
        query_button.click()

    # 解析数据并预订
    def buy_tickets(self):
        trs = self.driver.find_elements_by_xpath('//tbody[@id="queryLeftTable"]/tr[not(@datatran)]')
        # 定义flag标签
        flag = False
        for tr in trs:
            # print(tr.text)
            tr_list = tr.text.replace('\n', ' ').split(' ')
            if tr_list[1] == '复':
                tr_list.remove('复')
            # print(tr_list)

            # 获取车次
            train = tr_list[0]
            # 查找所购买车次
            if train in self.ticket_infos:
                seatypes = self.ticket_infos[train]
                for seatype in seatypes:
                    # 优选选择二等坐席是否有票
                    if seatype == 'O':
                        if tr_list[9] == '有' or tr_list[9].isdigit():
                            # 调用stop_cycle()修改flag标签,确定坐席
                            flag = self.stop_cycle(seatype, flag)
                            # 跳出循环
                            break
                        # continue
                    # 查询没有二等座票时再选商务座
                    elif seatype == 'M':
                        if tr_list[8] == '有' or tr_list[9].isdigit() == True:
                            # 调用stop_cycle()修改flag标签,确定坐席
                            flag = self.stop_cycle(seatype, flag)
                            # 跳出循环
                            break
                        # continue
                if flag:
                    # global back_to
                    # back_to = True
                    tr.find_element_by_xpath('.//td[@align="center"]/a[@class="btn72"]').click()
                    break

    # 修改flag标签，确定坐席
    def stop_cycle(self, seatype, flag):
        # 修改flag标签
        flag = True
        self.seat_type = seatype
        return flag

    # 选择确认乘客信息
    def passenger_info(self):
        # 显式等待乘客确认信息界面加载
        WebDriverWait(self.driver, 12).until(EC.url_contains(self.passengers_url))
        li_list = self.driver.find_elements_by_xpath('//ul[@id="normal_passenger_id"]/li')
        # 定义一个初始值
        k = 0
        for i, li in enumerate(li_list):
            passenger = li.text
            # print(passenger)
            if passenger in self.passengers:
                k += 1
                # time.sleep(1)
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, f'normalPassenger_{i}')))
                li.find_element_by_id(f'normalPassenger_{i}').click()
                # 选择票种
                ticket_tag = self.driver.find_element_by_id(f'ticketType_{k}')
                ticket_obj = Select(ticket_tag)
                if passenger == '吴泓榕':
                    ticket_obj.select_by_value('2')
                    # 显示等待弹窗加载
                    WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.ID, 'dialog_xsertcj_ok')))
                    # 点击确认关闭弹窗
                    consider_tag = self.driver.find_element_by_id('dialog_xsertcj_ok')
                    self.driver.execute_script('arguments[0].click();', consider_tag)
                else:
                    ticket_obj.select_by_value('1')

                # 选择坐席
                seat_tag = self.driver.find_element_by_id(f"seatType_{k}")
                seat_obj = Select(seat_tag)
                seat_obj.select_by_value(self.seat_type)
            else:
                continue
        # 测试点击上一步是否成功
        # 定位到上一步按钮
        # back_btn = self.driver.find_element_by_id('preStep_id')
        # 点击上一步按钮
        # back_btn.click()

        # 定位并点击提交订单
        submit_tag = self.driver.find_element_by_id('submitOrder_id')
        self.driver.execute_script('arguments[0].click();', submit_tag)

        '''核对乘客信息'''
        # 显示等待订单确认弹窗按钮加载
        WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.ID, 'qr_submit_id')))

        # 选择座位
        # 座位标签列表
        lag = True
        j = 1
        try:
            for i in range(1, len(self.passengers) + 1):
                if self.seat_type == 'O':
                    seat_number_list = self.driver.find_elements_by_xpath(f'//div[@id="erdeng{i}"]//li')
                elif self.seat_type == 'M':
                    seat_number_list = self.driver.find_elements_by_xpath(f'//div[@id="yideng{i}"]//li')
                # 按照乘客数量逐个顺序选择座位
                for num in range(len(self.passengers)):
                    lag = True
                    try:
                        seat_number = seat_number_list[num]
                        # print(seat_number)
                    except:
                        lag = False
                        break
                    else:
                        if j > len(self.passengers):
                            break
                        # 隐式等待
                        self.driver.implicitly_wait(10)
                        # 点击座位
                        seat_number.click()
                        j += 1
                if lag:
                    break
        except:
            pass

        # 点击确认提交订单按钮
        self.driver.find_element_by_id('qr_submit_id').click()

        '''网上支付'''
        # 显示等待支付界面加载
        WebDriverWait(self.driver, 1000).until(EC.presence_of_element_located((By.ID, 'payButton')))
        # 点击网上支付按钮
        # 这里用普通点击不起作用
        # self.driver.find_element_by_id('payButton').click()

        # 必须得用JS点击才有作用
        net_button = self.driver.find_element_by_id('payButton')
        self.driver.execute_script("arguments[0].click();", net_button)

        # 提示选择微信方式支付
        # 显式等待支付方式界面跳转
        # WebDriverWait(self.driver, 100).until(EC.url_contains(self.payway_url))
        # print('温馨提示，订单已提交成功，请在30分钟内选择微信点击支付')

    def run(self):
        '''定义主函数'''
        # 调用logic()方法:登录12306
        self.logic()
        # 打开查票界面
        self.open_ticket_message()
        while True:
            time.sleep(0.15)
            try:
                # 选择车次坐席、出发日期查询
                self.check_tickets()
                # 显式等待页面加载
                WebDriverWait(self.driver, 1000).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//tbody[@id="queryLeftTable"]/tr')))
                self.buy_tickets()
            except:
                break
        self.passenger_info()


if __name__ == '__main__':
    '''主入口'''
    train = TrainSpider('广州南', '潮阳', '2021-12-13', {"G6556": ['O', 'M']}, ['吴喜钟', '马楚贤'])
    train.run()
