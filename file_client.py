#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
import hashlib
import json


def get_file_md5(file_path):
    m = hashlib.md5()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break    
            m.update(data)
    
    return m.hexdigest().upper()

def register():
    '''
    用户注册
    '''
    conf = json.load(open("register.json")) # 加载配置信息
    reg_info = json.dumps(conf).encode()
    data_send = "{:<15}".format(len(reg_info)).encode()
    sock.send(data_send)
    sock.send(reg_info)
    sock.recv(15)
    res_data_1 = sock.recv(len(reg_info))
    res = b'{"op": 2, "error_code": 0}'
    if res == res_data_1:
        print("注册成功")

def login():
    '''
    用户登录
    '''
    login_info = {"op": 1,"args": {"uname": "hui","passwd": "asdfghjkl",} }   # 真实密码的MD5值，使用大写表示
    reg = json.dumps(login_info).encode()
    data_send = "{:<15}".format(len(reg)).encode()
    sock.send(data_send)
    sock.send(reg)
    res_len = sock.recv(15)
    res_data_1 = sock.recv(int(res_len))
    res = b'{"op": 1, "error_code": 0}'
    if res == res_data_1:
        print("登录成功")

def write_file(file_path, file_size, file_md5):
        f = open(file_path, "wb")
        recv_size = 0
        i = 0
        while recv_size < file_size:
            file_data = sock.recv(file_size - recv_size)
            if len(file_data) == 0:
                break
            f.write(file_data)
            a = recv_size / file_size

            if a > i:                
                print("已下载：{:.3%}".format(a))
                i += 0.01
            if a == 1:
                print("已下载：{:.3%}".format(a))
            recv_size += len(file_data)

        f.close()

        recv_file_md5 = get_file_md5(file_path)

        if recv_file_md5 == file_md5:
            print("成功接收文件 %s" % file_path)
        else:
            print("接收文件 %s 失败（MD5校验不通过）" % file_path)
            

# server_ip = input("服务器IP地址：")
# server_port = int(input("服务器端口："))

# 本机调试
# server_ip = "127.0.0.1"
server_ip = "192.168.9.168"
server_port = 9999

# while True:
#     try:
#         sock = socket.socket()
#         sock.connect((server_ip, server_port))
#     except:
#         time.sleep(1)
#     else:
#         break

sock = socket.socket()
sock.connect((server_ip, server_port))

def recv_dir():
    '''
    接收文件夹包括空文件夹
    '''
    login()
    while True:
        file_path = sock.recv(300).decode().rstrip()
        print(file_path)
        if len(file_path) == 0:
            break

        file_size = sock.recv(15).decode().rstrip()
        # print(file_size)
        if len(file_size) == 0:
            break
        file_size = int(file_size)

        file_md5 = sock.recv(32).decode()
        # print(file_md5)
        if len(file_md5) == 0:
            break

        # 一个文件
        if '\\' not in file_path and '/' not in file_path :
            print('\\' not in file_path and '/' not in file_path)      
            write_file(file_path, file_size, file_md5)
            break

        # 如果为空文件夹
        if file_size == -1:
            print("\n成功接收空文件夹 %s" % file_path)
            os.makedirs(file_path, exist_ok=True)
            continue

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        print("\n正在接收文件 %s，请稍候......" % file_path)

        write_file(file_path, file_size, file_md5)


recv_dir()
# register()

sock.close()
