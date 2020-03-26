#!/bin/env python
# coding: utf8

import sys
import os
import subprocess
import json
import time
import socket
import logging

IS_LINUX = False if sys.platform.startswith("win") else True
IS_WIN = not IS_LINUX

endpoint = socket.gethostname()
tags = ""
counterType="GAUGE"
step = 60

if IS_LINUX:
    cfg_dir = os.path.abspath(__file__).split("/")[0:-3]
    cfg_dir = "/".join(cfg_dir)
    cfg_file = os.path.join(cfg_dir , "config", 'cfg.json')

try:
    with open(cfg_file) as confile:
        config = json.load(confile)
    endpoint = config['hostname']
    for k, v in config['default_tags'].items():
        tags = tags + "%s=%s" % (k, v) + ","
    tags = tags.strip(",")
except:
    pass


def read_cmd_output(cmd):
    if IS_WIN:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    else:
        p = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        logging.error("执行 %s: error message: %s" %
                      (cmd, err.decode('cp936').encode('utf-8')))
    return out.decode('cp936').encode('utf-8').strip()

def get_proc_num(proc_name):
    if IS_LINUX:
        if proc_name == "all":
            cmd = "ls /proc/[1-9]* -d 2>/dev/null | wc -l"
            proc_nmu = read_cmd_output(cmd)
            return proc_nmu
        else:
            cmd = "ps -ef | grep %s | egrep -v ' grep |proc_num.py' | wc -l" % proc_name
            proc_nmu = read_cmd_output(cmd)
            return proc_nmu

def get_fqdn():
    if IS_LINUX:
        cmd = "\hostname -f"
        FQDN = read_cmd_output(cmd)
        return FQDN

def get_os_version():
    if IS_LINUX:
        cmd = "\cat /etc/system-release 2>/dev/null |head -n 1"
        OS_VERSION = read_cmd_output(cmd)
        return OS_VERSION

def get_os_bit():
    if IS_LINUX:
        cmd = "\getconf LONG_BIT"
        OS_BIT = read_cmd_output(cmd)
        return OS_BIT

def get_kl_version():
    if IS_LINUX:
        cmd = "\uname -r"
        KL_VERSION = read_cmd_output(cmd)
        return KL_VERSION

def get_patch_version():
    if IS_LINUX:
        cmd = "\cat /etc/*-release|awk '/^PATCHLEVEL/{print $NF}'"
        PATCH_VERSION = read_cmd_output(cmd)
        return PATCH_VERSION

def print_json(metric,value):
    #monitor_data = []
    ts = int(time.time())
    tmp = {}
    tmp["endpoint"] = endpoint
    tmp["tags"] = tags
    tmp["timestamp"] = ts
    tmp["counterType"] = counterType
    tmp["step"] = step
    tmp["metric"] = metric
    tmp["value"] = value
    monitor_data.append(tmp)



if __name__ == "__main__":
    monitor_data = []
    FQDN_v = get_fqdn()
    print_json("config.FQDN",FQDN_v)
    OS_VERSION = get_os_version()
    print_json("config.os_version",OS_VERSION)
    OS_BIT = get_os_bit()
    print_json("config.os_bit",OS_BIT)
    KL_VERSION = get_kl_version()
    print_json("config.kernel_version",KL_VERSION)
    PATCH_VERSION = get_patch_version()
    print_json("config.patch_version",PATCH_VERSION)
    print(json.dumps(monitor_data))
