# @Time : 2021/12/11 1:03
# @Author : 吴喜钟 
# @File : slider_spide.py 
# @Software: PyCharm

def acceleration(distance):
    """
        定义封装一个函数来计算每0.3秒加速度走过的位移
        位移计算公式：s = v0*t + 0.5*a*(t**2)
        末速度计算公式： v = v0 + a*t
    """
    #定义一个加速后开始减速的阀值
    mid = 4/5*distance
    #定义一个时间单位t=0.3秒，即以每0.3秒计算走过的距离
    t = 0.3
    #定义一个当前的初始距离current_distance
    current_distance = 0
    #定义一个空的列表用于存放每0.3秒走过的位移值displacement_list
    displacement_list = []
    #定义初始末速度为0
    v = 0
    while current_distance < distance:
        # 初速度
        v0 = v
        if current_distance < mid:
            #加速度
            a = 3
            #0.3秒走过的位移
            s = round(v0 * t + 0.5 * a * (t ** 2))
            # 更新current_distance的值
            current_distance = current_distance + s
            #计算末速度
            v = v0 + a * t
        else:
            #加速度
            a = -2
            #0.3秒走过的位移
            s = round(v0 * t + 0.5 * a * (t ** 2))
            # 更新current_distance的值
            current_distance = current_distance + s
            #计算末速度
            v = v0 + a * t
        # 将位移添加列表
        displacement_list.append(s)
    #将位移列表返回
    return displacement_list

if __name__ == '__main__':
    k = acceleration(16)
    print(k)



