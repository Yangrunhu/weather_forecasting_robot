# _*_ coding: utf-8 _*_
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.aai.v20180522 import aai_client, models
from uuid import uuid4
from base64 import b64decode
from random import choice
from pydub import AudioSegment
import os
import re
from config.configs import tencent_cloud_SecretId
from config.configs import tencent_cloud_SecretKey

__author__ = 'Silent_YangRun'
__date__ = '2019/5/25 12:57'


class SpeechSynthesis:

    def __init__(self, voices_contents, date_type):
        self.audio_contents = voices_contents
        self.type = date_type
        self.total_voice = list()
        self.voice_contents = list()

        # 设置人声类型
        # 0 亲和女声  3 活力男声
        # 4 温暖女声  6 情感男声
        self.VoiceType = choice([0, 3, 4, 6])
        # 字幕文本文件
        self.voice_texts = [{
            'index': 1,
            'duration': None,
            'text': '早上好'
        }]

    def get_voice(self, content, voice_index):
        """
        该API中文限制100个字符，将生成的单端文字语音存储在list中
        :param content:短文本
        :param voice_index:list的索引
        :return:
        """
        print(content)
        try:
            cred = credential.Credential(tencent_cloud_SecretId, tencent_cloud_SecretKey)
            http_profile = HttpProfile()
            http_profile.endpoint = "aai.tencentcloudapi.com"

            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            client = aai_client.AaiClient(cred, "ap-beijing", client_profile)

            req = models.TextToVoiceRequest()
            session_id = uuid4()
            params = '{"Text":"' + content + '", "SessionId":"' + str(session_id) + '"}'
            req.from_json_string(params)
            req.ModelType = 1
            req.VoiceType = self.VoiceType
            resp = client.TextToVoice(req)
            content = b64decode(resp.Audio)
            self.voice_contents[voice_index] = content
            self.total_voice.pop(0)
        except TencentCloudSDKException as err:
            print(err)

    def generated_speech(self):
        """
        根据文本生成多段语音
        """
        for index, text in enumerate(self.audio_contents.split("。")):
            if text is not "":
                self.total_voice.append({
                    'text': text,
                    'index': index
                })
                self.voice_texts.append({
                    'text': text,
                    'index': index + 2,
                    'duration': None
                })
                # 用于占位，防止单个音频未生成成功导致音频位置出错
                self.voice_contents.append('')

        while self.total_voice:
            self.get_voice(self.total_voice[0]['text'], self.total_voice[0]['index'])

        # 生成多个音频文件
        for index, voice_content in enumerate(self.voice_contents):
            with open('./weather_voices/' + self.type + '_weather_voices/weather/' + self.type +
                      '_weather ' + str(index) + ' .wav', 'wb') as f:
                f.write(voice_content)

    def get_output_voice(self):
        """
        将几段生成的语音合成为一个语音
        """
        if self.type == 'today':
            prologue_name = 'GM.wav'
        else:
            prologue_name = 'GN.wav'
            self.voice_texts[0]['text'] = '晚上好'
        input_path = './weather_voices/' + self.type + '_weather_voices/'
        output_path = input_path + 'weather/'
        # 先删除原有文件
        if os.path.exists(output_path + self.type + "_weather.wav"):
            os.remove(output_path + self.type + "_weather.wav")
        voice_files = os.listdir(output_path)
        # 获取空白语音
        # test_path = 'C:/Users/Coder/PycharmProjects/wechat_bot/'
        blank_voice = AudioSegment.from_file("./weather_voices/blank_audio_final.wav", "wav")
        # 获取开场白语音
        voice = blank_voice + AudioSegment.from_file(input_path + 'templates/' + str(self.VoiceType) + prologue_name,
                                                     "wav")
        self.voice_texts[0]['duration'] = voice.duration_seconds
        for index, voice_file in enumerate(voice_files):
            old_voice = AudioSegment.from_file(output_path + voice_file, "wav")
            self.voice_texts[index + 1]['duration'] = old_voice.duration_seconds
            # 音频合并
            voice += old_voice
            # 音频完成之后删除源文件
            os.remove(output_path + voice_file)
        voice.export(output_path + self.type + "_weather.wav", format='wav')

        # 生成字幕初始文件
        # print(voice_texts)

    @staticmethod
    def get_time_str(time):
        """
        判断是否为个位数时间，如果是个位数时间，在前加个0返回
        :param time:
        :return:
        """
        if len(str(time)) < 2:
            return '0' + str(time)
        else:
            return str(time)

    def modify_time(self, float_time):
        """
        根据不同的秒数返回不同的时间轴
        :param float_time: 秒数 例如 0.9650625秒等
        :return:
        """
        float_time = round(float_time, 3)
        hour = 0
        minute = 0
        if float_time < 60:
            sec = int(float_time)
            ms = int((float_time - sec) * 1000)
        elif float_time < 3600:
            minute = int(float_time / 60)
            sec = int(float_time - minute * 60)
            ms = int((float_time - minute * 60 - sec) * 1000)
        else:
            hour = int(float_time / 3600)
            minute = int((float_time % 3600) / 60)
            sec = int(float_time % 60)
            ms = int(((float_time - hour * 3600) - minute * 60 - sec) * 1000)

        hour = self.get_time_str(hour)
        minute = self.get_time_str(minute)
        sec = self.get_time_str(sec)
        ms = self.get_time_str(ms)
        final_time = hour + ":" + minute + ":" + sec + ',' + ms
        return final_time

    def get_srt(self):
        """
        生成字幕文件
        """
        timer_shaft = 0.1
        if os.path.exists('./weather_voices/' + self.type + '_weather_voices/' + self.type + '_weather.srt'):
            os.remove('./weather_voices/' + self.type + '_weather_voices/' + self.type + '_weather.srt')
        with open('./weather_voices/' + self.type + '_weather_voices/' + self.type + '_weather.srt',
                  'w+', encoding='utf-8') as voice_srt:
            for text in self.voice_texts:
                voice_srt.write(str(text['index']) + '\n')
                voice_srt.write(self.modify_time(timer_shaft) + ' --> ')
                timer_shaft = text['duration'] + timer_shaft + 0.05
                voice_srt.write(self.modify_time(timer_shaft) + '\n')
                voice_srt.write(self.handling_text(text['text']))

    @staticmethod
    def handling_text(audio_texts):
        if len(audio_texts) <= 23:
            return audio_texts + "\n\n"
        final_text = ''
        temp = ''
        if len(re.findall('；', audio_texts)) > 0:
            for audio_text in audio_texts.split("；"):
                final_text = final_text + audio_text + "\n"
        else:
            for audio_text in audio_texts.split("，"):
                if len(temp + audio_text) < 25:
                    final_text = temp = final_text + audio_text + "，"
                else:
                    temp = ''
                    final_text = final_text + "\n" + audio_text
            final_text += "\n"
        return final_text + '\n'

    def get_final_audio(self):
        # 生成单段语音
        self.generated_speech()
        # 多段语音合成
        self.get_output_voice()
        # 生成字幕文件
        self.get_srt()


if __name__ == '__main__':
    contents_today = '今天是05月29日，农历四月廿五。' \
                     '昭阳区白天天气为阵雨, 气温12度到23度。' \
        # '白天不太热也不太冷，风力不大，相信您在这样的天气条件下，应会感到比较清爽和舒适。' \
    # '气象条件有利于空气污染物稀释、扩散和清除，' \
    # '可在室外正常活动。建议着薄外套、开衫牛仔衫裤等服装。' \
    # '年老体弱者应适当添加衣物，宜着夹克衫、薄毛衣等。' \
    # '有降水，如果您要短时间外出的话可不必带雨伞。' \
    # '紫外线强度较弱，建议出门前涂擦SPF在12-15之间、PA+的防晒护肤品。' \
    # '有降水，推荐您在室内进行健身休闲运动；若坚持户外运动，须注意携带雨具并注意避雨防滑。'
    contents_tomorrow = '明天是05月28日，农历四月廿四。昭阳区白天天气为多云, 气温12度到19度。'
    test = SpeechSynthesis(contents_tomorrow, 'tomorrow')
    test.get_final_audio()
    test2 = SpeechSynthesis(contents_today, 'today')
    test2.get_final_audio()
