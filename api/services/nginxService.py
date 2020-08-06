import os, subprocess, sys


def status():
    status_cmd = "service nginx status"
    output = subprocess.call(status_cmd, shell=True)
    return output


def restart():
    restart_cmd = "service nginx restart"
    output = subprocess.call(restart_cmd, shell=True)
    return output


def testConfig():
    test_cmd = "nginx -t"
    output = subprocess.call(test_cmd, shell=True)
    return output



