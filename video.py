# _*_ coding: utf-8 _*_

import os
import cv2
import subprocess
import numpy
from pydub import AudioSegment
from math import ceil
import oss2

from config.configs import aliyun_cloud_AccessKeyId
from config.configs import aliyun_cloud_AccessKeySecret


__author__ = 'Silent_YangRun'
__date__ = '2019/5/27 16:39'


class Video:

    def __init__(self, location, date_type):
        self.location = location
        self.date_type = date_type
        self.auth = oss2.Auth(aliyun_cloud_AccessKeyId, aliyun_cloud_AccessKeySecret)
        self.bucket = oss2.Bucket(self.auth, 'http://oss-cn-beijing.aliyuncs.com', 'resouce-image')

    def get_video(self):
        video_path = './weather_voices/' + self.date_type + '_weather_voices/video/'
        voice_path = './weather_voices/' + self.date_type + '_weather_voices/weather/' + self.date_type + '_weather.wav'

        # 根据音频长度设置图片数量
        voice_duration = AudioSegment.from_file(voice_path, "wav").duration_seconds
        images_num = ceil(voice_duration / 4)
        # 随机从图库中选取相应数量的图片
        images_list = numpy.random.randint(1, 181, images_num)

        path = './images/'

        fps = 30
        size = (1024, 768)  # 图片的分辨率片
        file_path = video_path + "weather01.mp4"  # 导出路径
        # 如果文件存在则删除
        if os.path.exists(file_path):
            os.remove(file_path)
        four_cc = cv2.VideoWriter_fourcc(*'MP4V')  # 不同视频编码对应不同视频格式（例：'I','4','2','0' 对应avi格式）

        video = cv2.VideoWriter(file_path, four_cc, fps, size)

        # 选取图片
        for item in images_list:
            item_path = path + '1_' + str(item) + '.jpg'
            self.bucket.get_object_to_file('images/1_' + str(item) + '.jpg', item_path)
            img = cv2.imread(item_path)
            for i in range(120):
                video.write(img)
            # 删除本地缓存图片
            os.remove(item_path)
        video.release()

    def video_add_voice(self):
        video_path = './weather_voices/' + self.date_type + '_weather_voices/video/'
        voice_path = './weather_voices/' + self.date_type + '_weather_voices/weather/' + self.date_type + '_weather.wav'
        file_path02 = video_path + "weather02.mp4"
        # 视频添加音频
        subprocess.call(
            'ffmpeg -y -i ' + video_path + 'weather01.mp4' + ' -i ' + voice_path + ' -strict -2 -f mp4 ' + file_path02,
            shell=True)
        os.remove(voice_path)
        # 添加字幕
        video_path03 = video_path + self.location + "weather03.mp4"
        subprocess.call(
            "ffmpeg -y -i " + file_path02 + " -vf subtitles='./weather_voices/" + self.date_type + "_weather_voices/"
            + self.date_type + "_weather.srt'  -max_muxing_queue_size 999 " + video_path03,
            shell=True)

    def get_final_video(self):
        self.get_video()
        self.video_add_voice()


if __name__ == '__main__':
    video_today = Video('昭阳', 'today')
    video_today.get_final_video()
    # video_tomorrow = Video('昭阳', 'tomorrow')
    # video_tomorrow.get_final_video()
