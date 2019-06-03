# _*_ coding: utf-8 _*_
import requests
import json
from config.configs import seniverse_private_key


__author__ = 'Silent_YangRun'
__date__ = '2019/5/25 16:50'

# 逐日天气预报
WEATHER_STATION_API = 'https://api.seniverse.com/v3/weather/daily.json'
# 农历、节气、生肖
CHINESE_CALENDAR_API = 'https://api.seniverse.com/v3/life/chinese_calendar.json'
# 天气指数
SUGGESTION_API = 'https://api.seniverse.com/v3/life/suggestion.json'
KEY = seniverse_private_key


def return_weather_str(location, date_type):
    if date_type is 'today':
        start = '0'
        date_name = '今天'
    else:
        start = '1'
        date_name = '明天'
    # 获取今日天气预报
    language = 'zh-Hans'
    # 单位为摄氏度
    unit = 'c'
    # 0从今日开始，-1从昨日开始
    # 预报几天的数据
    days = 1
    params = {
        'key': KEY,
        'location': location,
        'language': language,
        'unit': unit,
        'start': start,
        'days': days,
    }
    result = get_weather_str(WEATHER_STATION_API, params)
    ret_dict = json.loads(result)['results'][0]['daily']
    # 今日最高温
    today_high = ret_dict[0]['high']
    # 今日最低温
    today_low = ret_dict[0]['low']
    # 今日白天天气
    today_weather = ret_dict[0]['text_day']
    weather_str = location + '区' + "白天天气为" + today_weather + ", 气温" + today_low + "度到" + today_high + "度。"

    # 获取今日农历节日
    params = {
        'key': KEY,
        'start': start,
        'days': days,
    }
    result = get_weather_str(CHINESE_CALENDAR_API, params)
    ret_dict = json.loads(result)['results']['chinese_calendar'][0]
    month = ret_dict['date'].split("-")[1]
    day = ret_dict['date'].split("-")[2]
    # 农历月
    lunar_month_name = ret_dict['lunar_month_name']
    # 农历日
    lunar_day_name = ret_dict['lunar_day_name']
    lunar_day_name = lunar_day_name.replace('廿', '二十')
    # 二十四节气
    solar_term = ret_dict['solar_term']
    # 节假日
    lunar_festival = ret_dict['lunar_festival']
    date_str = date_name + '是' + month + '月' + day + '日，' + '农历' + lunar_month_name + lunar_day_name + '。'
    if lunar_festival is not "" and solar_term is not "":
        date_str = date_str + solar_term + '，并且也是' + lunar_festival + '。'
    else:
        if lunar_festival is not "":
            date_str = date_str + lunar_festival + '。'
        if solar_term is not "":
            date_str = date_str + solar_term + '。'

    # 获取今日生活建议
    suggestion_str = ''
    if date_type == 'today':
        params = {
            'key': KEY,
            'location': location,
            'language': language
        }
        result = get_weather_str(SUGGESTION_API, params)
        ret_dict = json.loads(result)['results'][0]['suggestion']
        # 舒适度
        comfort = ret_dict['comfort']['details']
        # 降水
        umbrella = ret_dict['umbrella']['details']
        # 空气质量
        air_pollution = ret_dict['air_pollution']['details']
        # 穿衣
        dressing = ret_dict['dressing']['details']
        # 紫外线
        uv = ret_dict['uv']['details']
        # 运动
        sport = ret_dict['sport']['details']
        suggestion_str = comfort + air_pollution + dressing + umbrella + uv + sport
    return date_str + weather_str + suggestion_str


def get_weather_str(weather_api, params):
    """根据不同的天气API和参数返回不同的值"""
    result = requests.get(weather_api, params=params, timeout=1).text
    return result


if __name__ == '__main__':
    # location = getLocation()
    local = '大关县'
    weather = return_weather_str(local, 'today')
    print(weather)
