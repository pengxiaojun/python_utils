# -*-coding: utf-8 -*-


import re
import sys
import json
import http.client
import http.cookiejar
import urllib.parse

host = "http://m.hzjianjiao.com/Agent"
login_url = host + "/Login/loginOfpassword.html"
category_url = host + "/Category/category.html"
more_goods_url = host + "/Category/goodsMore.html"

re_html_inner = re.compile(r'^<[^>]{1,}>(.+)</')
re_goods_id = re.compile(r'^<.+data-id="([0-9]{0,})".+')
re_chinese = re.compile(r'[\u4e00-\u9fa5]+')
re_letter = re.compile(r'^[a-zA-Z]+')


def get_vendor_name(goods_name):
    goods_name = goods_name.strip().replace('&amp;', ' ')
    fields = goods_name.split(' ')
    vendor = fields[0]
    name = ''.join(fields[1:])
    if len(re_chinese.findall(vendor)) == 0:
        # vendor is foreign brand
        left_word = re_letter.findall(name)
        if len(left_word) > 0:
            left_word = ''.join(left_word)
            vendor += left_word
            name = name[len(left_word):]

    if len(name) == 0:
        name = vendor
    return vendor, name


def collect(opener, phone, passwd):
    # step 1: login
    params = urllib.parse.urlencode({'phone': phone,
                                     'password': passwd})
    data = params.encode('utf-8')
    request = urllib.request.Request(login_url, data)
    resp = opener.open(request)
    resp_all = (resp.read().decode('utf-8'))
    # TODO: validate if login success

    # step 2: collect category information
    request = urllib.request.Request(category_url)
    resp = opener.open(request)
    category_text = resp.read().decode('utf-8')

    start = category_text.find('<ul class="g_car_ul f_g_ul">')
    stop = category_text.find('</ul>', start)

    if (start == -1 or stop == -1):
        print('Parse category error')
        return

    category_list = category_text[start:stop]
    cateogry_lines = category_list.split('\n')

    for line in cateogry_lines:
        line = line.strip()

        if 'class="tit"' in line:
            r_name = re_html_inner.match(line)
            if r_name:
                vendor, name = get_vendor_name(r_name.group(1))
                print(vendor, end=' ')
                print(name, end=' ')
        if '<p class="price">' in line:
            r_price = re_html_inner.match(line)
            if r_price:
                print(r_price.group(1), end=' ')
        if '<p class="can">' in line:
            r_market_price = re_html_inner.match(line)
            if r_market_price:
                print(r_market_price.group(1), end=' ')
        if '<div class="yong">' in line:
            r_yong = re_html_inner.match(line)
            if r_yong:
                print(r_yong.group(1)[9:], end=' ')
        if '<p class="ku">' in line:
            r_remain = re_html_inner.match(line)
            if r_remain:
                print(r_remain.group(1), end=' ')
        re_id = re_goods_id.match(line)
        if re_id:
            print(re_id.group(1), end='\r\n')

    # step 3: collect more goods
    for i in range(1, 40):
        post_data = urllib.parse.urlencode({'data_page': i,
                                            'keyword': '',
                                            'sort': 'add_time',
                                            'order': '0'})
        request = urllib.request.Request(more_goods_url,
                                         post_data.encode('utf-8'))
        resp = opener.open(request)
        goods_text = resp.read().decode('utf-8')
        json_obj = json.loads(goods_text)
        for j in range(len(json_obj)):
            vendor, name = get_vendor_name(json_obj[j]['goods_name'])
            print(vendor, end=' ')
            print(name, end=' ')
            print('￥'+json_obj[j]['goods_price'], end=' ')
            print('市场价:￥'+json_obj[j]['goods_market_price'], end=' ')
            print('￥'+json_obj[j]['yprice'], end=' ')
            print('库存:'+json_obj[j]['goods_number'], end=' ')
            print(json_obj[j]['id'], end='\r\n') # end sep for excel import


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:%s <user> <password>' % sys.argv[0])
        sys.exit(0)

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    # let server rememer me
    req = opener.open(login_url)
    ret = collect(opener, sys.argv[1], sys.argv[2])
