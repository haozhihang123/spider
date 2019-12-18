#coding=utf-8
import requests
import urllib.parse
from lxml.html import etree
from requests.exceptions import RequestException

from urllib.parse import urljoin

from lxml import etree
import re
import json
import random  

# 百度搜索接口
proxy_list = []
def format_url(url, params: dict=None) -> str:
    query_str = urllib.parse.urlencode(params)
    return f'{ url }?{ query_str }'

def get_url(keyword):
    params = {
        'wd': str(keyword)
    }
    url = "https://www.baidu.com/s"
    url = format_url(url, params)
    # print(url)

    return url

def get_page(url):
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        }
        proxies=random.choice(proxy_list)
        response = requests.get(url=url,proxies=proxies,headers=headers)
        # 更改编码方式，否则会出现乱码的情况
        response.encoding = "utf-8"
        print(response.status_code)
        # print(response.text)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_page(url,page):

    for i in range(1,int(page)+1):
        print("正在爬取第{}页....".format(i))
        title = ""
        sub_url = ""
        abstract = ""
        flag = 11
        if i == 1:
            flag = 10
        html = get_page(url)
        content = etree.HTML(html)
        for j in range(1,2):
            data = {}
            res_title = content.xpath('//*[@id="%d"]/h3/a' % ((i - 1) * 10 + j))
            if res_title:
                title = res_title[0].xpath('string(.)')
                print(title)

            sub_url = content.xpath('//*[@id="%d"]/h3/a/@href' % ((i - 1) * 10 + j))
            if sub_url:
                sub_url = sub_url[0]

            res_abstract = content.xpath('//*[@id="%d"]/div[@class="c-abstract"]'%((i-1)*10+j))
            if res_abstract:
                abstract = res_abstract[0].xpath('string(.)')
            else:
                res_abstract = content.xpath('//*[@id="%d"]/div/div[2]/div[@class="c-abstract"]'%((i-1)*10+j))
                if res_abstract:
                    abstract = res_abstract[0].xpath('string(.)')
                    # res_abstract = content.xpath('//*[@id="%d"]/div/div[2]/p[1]'%((i-1)*10+j))
            # if not abstract:
            #     abstract = content.xpath('//*[@id="%d"]/div/div[2]/p[1]'%((i-1)*10+j))[0].xpath('string(.)')
            data['title'] = title
            data['sub_url'] = sub_url
            data['abstract'] = abstract
            # print(data)


            rel_url = content.xpath('//*[@id="page"]/a[{}]/@href'.format(flag))
            if rel_url:
                url = urljoin(url, rel_url[0])
            else:
                print("无更多页面！～")
                # return
            yield data


def parse_company(url):
    html = get_page(url)

    # print(html)
    p = re.compile('<title>(.*?)</title>', re.S)
    title = p.findall(html)
    if title == []:
        return
    print("title:",title)
    k = re.compile('<div  id="aboutuscontent">(.*?)</div>', re.S)
    content_s = k.findall(html)
    print("content_s:",content_s)
    fout = open('output2.txt', 'a', encoding="utf-8")
    fout.write(title[0])
    fout.write("\t\n")
    fout.write(content_s[0])
    fout.write("\t\n\t\n")


def pre():
    url = 'http://www.kuaidaili.com/free/'
    rp =requests.get(url)
    rp_html = etree.HTML(rp.text)

    #找xpath
    ip_xpath = '//*[@id="list"]/table/tbody/tr/td[1]/text()'
    port_xpath = '//*[@id="list"]/table/tbody/tr/td[2]/text()'
    http_or_https_xpath ='//*[@id="list"]/table/tbody/tr/td[4]/text()'

    #匹配内容
    ip_list = rp_html.xpath(ip_xpath)
    port_list = rp_html.xpath(port_xpath)
    http_or_https_list = rp_html.xpath(http_or_https_xpath)

    #进行组合
    list_zip = zip(ip_list,port_list,http_or_https_list)
    proxy_dict= {}
    
    for ip,port,http_or_https in list_zip:
        proxy_dict[http_or_https] = f'{ip}:{port}'
        proxy_list.append(proxy_dict)
        proxy_dict = {}
    print(proxy_list)

def main():
    # keyword = input("输入关键字:")
    # page = input("输入查找页数:")
    keywords = ['江苏振宇化工有限公司','江苏国胶化学科技有限公司','南通中泰化工有限公司','常州新华石油化工储运有限公司','常州东昊化工公司','常州新日化学有限公司','常州海克莱化学有限公司','江苏梅兰化工集团有限公司','江苏三蝶化工有限公司','']
    keyword = '常州海克莱化学有限公司顺企网'

    for keyword in keywords:
        if keyword != '':
            keyword = keyword + "顺企网"
            print(keyword)
            page = 1
            url = get_url(keyword)
            results = parse_page(url,page)
            new_url = []
            for result in results:
                new_url = result['sub_url']
            print(new_url)
            parse_company(new_url)
if __name__ == '__main__':
    pre()
    main()
