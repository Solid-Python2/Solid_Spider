import requests,random
from project.美团全家桶.city import CITY_TAG
import pandas as pd
from datetime import date,timedelta
from project.Proxy import PROXY
#获取数据
def Get_Data():
    # departureCity=input('请输入出发城市:')
    # reachCity=input('请输入目的城市:')
    departureCity='广州'
    reachCity='北京'
    #获取30天内所有日期
    thirtyDaysToDate=[(date.today() + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
    url='https://i.meituan.com/uts/train/train/querytripnew?'
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000'
    }
    res = []
    for day in thirtyDaysToDate:
        print("正在获取数据........")
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000'
        }
        proxy = random.choice(PROXY)  # 本地代理
        proxies = {
            'http': 'http://' + proxy,
        }
        params = {
            'fromPC': 1,
            'train_source': 'meituanpc@wap',
            'uuid': 'C082368707A3F2CBB95285B68189E70F278B4EF52CC5105E0E5C3D0EA4E54390',
            'from_station_telecode':CITY_TAG[departureCity] ,
            'to_station_telecode': CITY_TAG[reachCity],
            'yupiaoThreshold': 0,
            'start_date': day,
            'isStudentBuying': 'false'
        }
        data=requests.get(url, params=params, headers=headers,proxies=proxies).json()['data']
        trains=data['trains']
        # 列车号
        train_code_list=[]
        #列车No
        train_No_list=[]
        #车次类型
        train_type_list=[]
        #出发时间
        start_time_list=[]
        #到达时间
        arrivalTime_list=[]
        #耗时
        run_time_list=[]
        #出发车站
        start_station_list=[]
        #到达车站
        arrival_station_list=[]
        #参考票价|余票
        for train in trains:
            if train['can_buy_now']=='Y':
                item={}
                # 列车号
                train_code=train['train_code']
                #列车No
                train_No=train['train_no']
                #车次类型
                if 'G' in train_code or 'C' in train_code:
                    train_type='高铁'
                elif 'D' in train_code:
                    train_type = '动车'
                else:
                    train_type = '火车'
                #出发时间
                start_time=train['start_time']
                #到达时间
                arrivalTime=train['arrive_time']
                #耗时
                run_time=train['run_time']
                #出发车站
                start_station=train['from_station_name']
                #到达车站
                arrival_station=train['to_station_name']
                #参考票价|余票
                seats=train['seats']
                dic = {}
                for x in seats:
                    dic[x['seat_type_name']]={'儿童票':x['maxChildPrice'],'学生票':x['maxStudentPrice'],'成人票':x['seat_min_price'],'余票':x['seat_yupiao']}
                item['train_code']=train_code
                item['train_No']=train_No
                item['train_type']=train_type
                item['start_time']=start_time
                item['arrivalTime']=arrivalTime
                item['run_time']=run_time
                item['start_station']=start_station
                item['arrival_station']=arrival_station
                item['dic']=dic
                item['trainDate']=train['trainDate']
                res.append(item)
            else:
                print('{}的{}现在无法购票!!!'.format(train['trainDate'],train['train_code']))
                continue
    return res
def Save_excel(writer,List,sheet_name):
    columns = ['列车号', '列车编号', '出发时间', '抵达时间', '耗时', '起始站', '目的站','日期', '车票类型', '旅客身份', '价格','余票']
    df = pd.DataFrame(
        data=List,
        columns=columns
    )
    df.to_excel(writer, sheet_name=sheet_name)
def AppendData(List,x):
    lst = []
    # 列车号
    train_code = x['train_code']
    lst.append(train_code)
    # 列车编号
    train_No = x['train_No']
    lst.append(train_No)
    # 出发时间
    start_time = x['start_time']
    lst.append(start_time)
    # 抵达时间
    arrivalTime = x['arrivalTime']
    lst.append(arrivalTime)
    # 耗时
    run_time = x['run_time']
    lst.append(run_time)
    # 起始站
    start_station = x['start_station']
    lst.append(start_station)
    # 抵达站
    arrival_station = x['arrival_station']
    lst.append(arrival_station)
    #日期
    trainDate=x['trainDate']
    lst.append(trainDate)
    #参考票价|余票
    seats = x['dic']
    for key, vlaue in seats.items():
        for k, v in vlaue.items():
            if k=='余票':
                continue
            # 车票类型
            lst.append(key)
            #旅客身份
            lst.append(k)
            #价格
            lst.append(v)
            lst.append(vlaue['余票'])
            List.append(lst)
            lst = lst[:-4]
    #日期
def classification(res):
    highSpeedRail_list=[]
    bulletTrain_list=[]
    train_list=[]
    for x in res:
        if x['train_type']=='高铁':
            AppendData(highSpeedRail_list,x)
        elif x['train_type']=='动车':
            AppendData(bulletTrain_list, x)
        else:
            AppendData(train_list, x)
    writer=pd.ExcelWriter('火车票.xls')
    Save_excel(writer,highSpeedRail_list,'高铁')
    Save_excel(writer,bulletTrain_list,'动车')
    Save_excel(writer,train_list,'火车')
    writer.save()
    writer.close()
    print('写入成功!!!')
if __name__ == '__main__':
    res=Get_Data()
    print("获取数据成功")
    classification(res)
