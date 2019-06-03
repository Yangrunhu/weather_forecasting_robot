# _*_ coding: utf-8 _*_
import itchat
from apscheduler.schedulers.blocking import BlockingScheduler
import time
from weather import return_weather_str
from video import Video
from speech_synthesis import SpeechSynthesis
import threading

__author__ = 'Silent_YangRun'
__date__ = '2019/5/24 11:14'

friends_info = [
    {'name': '若如初见', 'local': '大关县'},
    {'name': 'Z &amp; O', 'local': '西山'},
    {'name': '后知后觉、', 'local': '昭阳'},
    {'name': '秋林', 'local': '昭阳'},
]

group_chats_info = [
    # {'name': '务虚求实', 'local': '昭阳'},
    # {'name': '务虚求实', 'local': '番禺'},
    {'name': '我的一家人', 'local': '昭阳'}
]


def get_specified_video(local, date_type):
    """根据地点生成今日或明日的天气预报"""
    # 获取天气信息
    weather_texts = return_weather_str(local, date_type)
    # 生成音频和字幕文件
    audio = SpeechSynthesis(weather_texts, date_type)
    audio.get_final_audio()
    # 生成视频文件
    video_today = Video(local, date_type)
    video_today.get_final_video()


def get_videos():
    date_type = get_status()[0]
    """生成所有地点的天气预报"""
    locations = []
    for friend in friends_info:
        locations.append(friend['local'])
    print(set(locations))
    for location in set(locations):
        get_specified_video(location, date_type)


def get_status():
    date_type = 'today'
    day_type = '今天'
    localtime_hour = time.localtime().tm_hour
    if localtime_hour >= 21:
        date_type = 'tomorrow'
        day_type = '明天'
    return date_type, day_type


def send_msg():
    date_type = get_status()[0]
    day_type = get_status()[1]

    audio_path = './weather_voices/' + date_type + '_weather_voices/video/'
    for friend in friends_info:
        print(friend)
        user_info = itchat.search_friends(name=friend['name'])
        if len(user_info) > 0:
            local = friend['local']
            user_name = user_info[0]['UserName']
            itchat.send_msg(day_type + local + '的天气预报（自动发送）', toUserName=user_name)
            print("发送消息成功")
            time.sleep(1)
            itchat.send_video(audio_path + local + 'weather03.mp4', user_name)
            print("发送视频成功")
        time.sleep(2)

    for group_chat in group_chats_info:
        chat_rooms = itchat.search_chatrooms(name=group_chat['name'])
        if len(chat_rooms) > 0:
            local = group_chat['local']
            itchat.send_msg(day_type + local + '的天气预报（自动发送）', chat_rooms[0]['UserName'])
            print("发送消息成功")
            time.sleep(1)
            itchat.send_video(audio_path + local + 'weather03.mp4', chat_rooms[0]['UserName'])
            print("发送视频成功")
        time.sleep(2)


def after_login():
    """定时功能"""
    scheduler.add_job(get_videos, 'cron', hour=21, minute=6)
    scheduler.add_job(send_msg, 'cron', hour=21, minute=30)
    scheduler.add_job(get_videos, 'cron', hour=9, minute=28)
    scheduler.add_job(send_msg, 'cron', hour=9, minute=31)
    scheduler.start()


def after_logout():
    scheduler.shutdown()


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    """自动回复"""
    print(msg.text)
    return "自动回复正在开发中~~感觉身体被掏空了呢~~"


def we_chat_login():
    """微信登录"""
    itchat.auto_login(hotReload=True, exitCallback=after_logout)
    itchat.run()


# 用于接收群里面的对话消息
@itchat.msg_register([itchat.content.TEXT], isGroupChat=True)
def print_content(msg):
    print(msg.User['NickName'])
    if "@知庸_bot" in msg.text:
        return "自动回复正在开发中~~感觉身体被掏空了呢~~"


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # 添加微信登录的线程
    we_chat_login_thread = threading.Thread(target=we_chat_login)
    # 添加定时任务的线程
    after_login_thread = threading.Thread(target=after_login)
    we_chat_login_thread.start()
    after_login_thread.start()
