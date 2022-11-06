#!/usr/bin/env python
import os.path
import urllib.request
import urllib.parse
import re
from time import sleep
import requests
from cookie import *
import logging
from retrying import retry

BASE_URL = "http://tvtropes.org/pmwiki/pmwiki.php/"
URL_QUERY = "?action=source"


def sanitize_link(link_txt):
    # + shows a specific bullet
    link_txt = link_txt.replace('+ ', '')
    # * is another kind of bullet
    link_txt = link_txt.replace('* ', '')
    # no parenthesis, colons or triple-apostrophes
    link_txt = link_txt.replace('[[', '').replace(']]', '')
    link_txt = link_txt.replace('{{', '').replace('}}', '')
    link_txt = link_txt.replace(':', '')
    link_txt = link_txt.replace('\'\'\'', '')
    link_txt = link_txt.replace('\'\'', '')
    link_txt = link_txt.replace('\\\\', '')
    link_txt = link_txt.replace('\\', '')
    link_txt = link_txt.replace('|', '')
    link_txt = link_txt.replace('&quot;', '')
    link_txt = link_txt.replace(',', '')
    link_txt = link_txt.replace('.', '')
    # only the first word
    try:
        link_txt = link_txt.split()[0]
    except:
        return ""
    return link_txt


@retry(stop_max_attempt_number=10, wait_fixed=2000)
def download_page_source(title, namespace="Main", delay=0, logging=None):
    url = BASE_URL + urllib.parse.quote(namespace + '/' + title) + URL_QUERY
    if logging is not None:
        logging.info(f"Current URL: {url}")
    s = requests.session()
    s.keep_alive = False
    request = s.get(url, cookies=cookies, headers=headers)
    source = request.content
    source = source.decode('Windows-1252', errors='replace')
    sleep(delay)
    return source


def check_tropes(tropes):
    return tropes.isalpha() and tropes[0].isupper()


def candidates(subindex):
    candidates_index = []
    for i in range(26):
        for j in range(i + 1, 26):
            candidates_index.append(f'{subindex}/{chr(i + ord("A"))}To{chr(j + ord("A"))}')
    for i in range(10):
        for j in range(i + 1, 10):
            candidates_index.append(f'{subindex}/{i}To{j}')
    return candidates_index


def get_subindexes_from_paragraph(paragraph_list, k):
    paragraph = paragraph_list[k]
    if "!!Examples:" in paragraph:  # remove Examples
        return []
    paragraph_lines = paragraph.split('<br>')
    return [sanitize_link(i) for i in paragraph_lines if
            i.startswith('+ ') or i.startswith('++ ') or i.startswith('+++ ')]


def get_subindexes_from_index(page_src):
    try:
        paragraph_list = page_src.split('----')
    except IndexError:
        return None
    subindexes_from_page = []
    size = len(paragraph_list)
    for i in range(0, size):
        subindexes_from_page.extend(get_tropes_from_paragraph(paragraph_list, i))

    return subindexes_from_page


def get_tropes_from_paragraph(paragraph_list, k):
    paragraph = paragraph_list[k]
    if "!!Examples:" in paragraph:  # remove Examples
        return []
    paragraph_lines = paragraph.split('<br>')
    return [sanitize_link(i) for i in paragraph_lines if
            i.startswith('* ') or i.startswith('** ') or i.startswith('*** ')]


def get_tropes_from_page(page_src):
    try:
        paragraph_list = page_src.split('----')
    except IndexError:
        return None
    tropes_from_page = []
    size = len(paragraph_list)
    for i in range(0, size):
        tropes_from_page.extend(get_tropes_from_paragraph(paragraph_list, i))

    return tropes_from_page


def check_not_found(page_src):
    if '<span style="font-family:Courier, \'Courier New\', monospace">Couldn\'t get page source.</span>' in page_src:
        return True
    else:
        if '<br>' not in page_src:
            return True
        page_lines = page_src.split('<br>')
        if 'may refer to:' in page_lines[0]:
            return True
        return False


def check_redirect(page_src):
    if '<span style="font-family:Courier, \'Courier New\', monospace">[[redirect:' in page_src:
        return True, page_src.split('[')[-1].split(']')[0].split(':')[-1]
    else:
        return False, None


def catch_exception(exception, current_tropes, subindex, logging):
    if exception in current_tropes:
        logging.info('Exception \'' + exception + '\' caught in \'' + subindex + '\'')


def get_logger(name):
    logger = logging.getLogger(name)
    # 创建一个handler，用于写入日志文件
    filename = f'{name}.log'
    fh = logging.FileHandler(filename, mode='w+', encoding='utf-8')
    # 再创建一个handler用于输出到控制台
    ch = logging.StreamHandler()
    # 定义输出格式(可以定义多个输出格式例formatter1，formatter2)
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    # 定义日志输出层级
    logger.setLevel(logging.DEBUG)
    # 定义控制台输出层级
    # logger.setLevel(logging.DEBUG)
    # 为文件操作符绑定格式（可以绑定多种格式例fh.setFormatter(formatter2)）
    fh.setFormatter(formatter)
    # 为控制台操作符绑定格式（可以绑定多种格式例ch.setFormatter(formatter2)）
    ch.setFormatter(formatter)
    # 给logger对象绑定文件操作符
    logger.addHandler(fh)
    # 给logger对象绑定文件操作符
    logger.addHandler(ch)

    return logger
