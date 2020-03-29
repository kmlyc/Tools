# -*- coding:utf8 -*-
# ---------------------------------------------------------------------------------------------------------------------
"""
Author: kmly
Date: 2020-03-29
Desc: A file for download files, like videos, pictures, musics....
"""
# ---------------------------------------------------------------------------------------------------------------------
import requests
import os
import time
import datetime
from _md5 import md5
from Crypto.Cipher import AES


class DF(object):
    def __init__(self, url, tp=None):
        self.tp = tp
        self.dir_name = os.path.dirname(os.getcwd()).replace('\\', '/')
        self.url = url

    def chose_func(self, directory):
        if self.tp == '00':
            self.download_video(self.url, directory)
        elif self.tp == '01':
            self.download_m3u8(self.url, directory)
        elif self.tp == '10':
            self.download_image(self.url, directory)

    def download(self, des_path=None, times=3):
        if des_path is not None:
            directory_path = des_path
        else:
            if self.tp == '00':
                directory_path = self.dir_name + '/video'
            elif self.tp == '01':
                directory_path = self.dir_name + '/video/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            elif self.tp == '10':
                directory_path = self.dir_name + '/image'
            else:
                directory_path = self.dir_name + '/tmp'
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        count = 0
        while True:
            try:
                count += 1
                self.chose_func(directory_path)
                break
            except Exception as e:
                print("Error: ", e)
                if count >= times:
                    print("The download has been retried {} times without success, and the system will no longer download the file.".format(times))
                    break
                print("The system will try to download again ...")

    @staticmethod
    def download_video(url, video_directory):
        if '.mp4' not in url.lower():
            raise Exception('The URL is not a valid mp4 video download link.')
        data = requests.get(url).content
        if data:
            video_name = md5(data).hexdigest() + '.mp4'
            file_path = '{}/{}'.format(video_directory, video_name)
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(data)
                    print('video: "{}" downloaded successfully'.format(video_name))
            else:
                print('This video is existed.')
            return True
        else:
            return False

    @staticmethod
    def download_m3u8(url, video_directory):
        all_content = requests.get(url).text
        if "#EXTM3U" not in all_content:
            raise Exception("The URL is not M3U8 download link.")

        if "EXT-X-STREAM-INF" in all_content:
            file_line = all_content.split("\n")
            for line in file_line:
                if '.m3u8' in line:
                    url = url.rsplit("/", 1)[0] + "/" + line
                    all_content = requests.get(url).text
        file_line = all_content.split("\n")

        flag = True
        key = ""
        for index, line in enumerate(file_line):
            if "#EXT-X-KEY" in line:  # encrypt Key
                method_pos = line.find("METHOD")
                comma_pos = line.find(",")
                method = line[method_pos:comma_pos].split('=')[1]
                print("Decode Method：", method)

                uri_pos = line.find("URI")
                quotation_mark_pos = line.rfind('"')
                key_path = line[uri_pos:quotation_mark_pos].split('"')[1]

                # key_url = url.rsplit("/", 1)[0] + "/" + key_path
                key_url = key_path
                print(key_url)
                res = requests.get(key_url)
                key = res.content
                print("key：", key)

            if "EXTINF" in line:
                flag = False
                pd_url = url.rsplit("/", 1)[0] + "/" + file_line[index + 1]
                # pd_url = file_line[index + 1]
                print(pd_url)

                res = requests.get(pd_url)
                ts_name = 'ts' + str((index+1)).zfill(3) + '.ts'

                with open(os.path.join(video_directory, ts_name), 'ab') as f:
                    if len(key):
                        aes = AES.new(key, AES.MODE_CBC, key)
                        f.write(aes.decrypt(res.content))
                    else:
                        f.write(res.content)
                    f.flush()
        if flag:
            raise Exception("Not find download links.")
        else:
            print("The M3U8 downloaded successfully")

    @staticmethod
    def download_image(url, directory):
        print(url)
        if not ('.jpg' in url.lower() or '.png' in url.lower()):
            print('Please confirm if this is an image download link')

        image_content = requests.get(url).content
        if image_content:
            image_name = md5(image_content).hexdigest() + '.jpg'
            file_path = '{}/{}'.format(directory, image_name)
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(image_content)
                    print('image: "{}" downloaded successfully'.format(image_name))
            else:
                print('This image is existed.')
            return True
        else:
            return False


if __name__ == '__main__':
    pass

