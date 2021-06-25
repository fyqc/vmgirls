import os
import requests
from bs4 import BeautifulSoup
from threading import Thread


""" 
测试于2021年6月25日
"""


def save_html_as_local(url, header, html_rename='local.html'):
    html = requests.get(url, headers=header)
    with open(html_rename, 'w', encoding='utf-8') as f:
        f.write(html.text)


def get_soup_from_localhtml(webpage):
    soup = BeautifulSoup(open(webpage, encoding='utf-8'), features='lxml')
    return soup


def get_soup_from_webpage(url, header):
    response = requests.get(url, headers=header)
    # 这里的编码应根据网页源码指定字符集做相应修改
    response.encoding = 'utf-8'
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    return soup


def get_dir(soup):
    dir_name = soup.title.get_text().split("丨")[0].strip()
    return dir_name


def make_list(soup):
    postdict = {}
    div_archives = soup.find('div', class_='archives')
    tags_a = div_archives.find_all('a')
    url_pre = 'https://www.vmgirls.com/'
    for tag in tags_a:
        post_num_html = tag['href']
        if '15071' in post_num_html:  # 上一次采集到这里停止了
            break  # 16008 @ 4/27/2021
        post_title = tag.get_text()
        posturl = url_pre + post_num_html
        # 这里要把第一项，也就是唯一一个带#的项滤掉，不然后面会Fuck Up
        # 'https://www.vmgirls.com/#': '全部展开/收缩'
        if '#' in posturl:  
            continue
        postdict[posturl] = post_title
    return postdict


def download_single_post(posturl, header):
    soup = get_soup_from_webpage(posturl, header)
    downlist = extract_image_url(soup)
    if not downlist:
        print("这个帖子不存在图片，跳过～～")
    else:
        downlist = list(set(downlist))  # 对downlist去重
        dir_name = get_dir(soup)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)  # 建立文件夹
        threads = []
        for url in downlist:
            t = Thread(target=rillaget, args=[url, dir_name, header])
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

            
def extract_image_url(soup):
    downlist = []
    div_nc_light_gallery = soup.find('div', class_="nc-light-gallery")
    a = div_nc_light_gallery.find_all('a')
    for n in a:
        img_url_incomplete = n.get('href')
        if 'image' not in img_url_incomplete:
            continue
        img_url = 'https:' + img_url_incomplete
        downlist.append(img_url)
    return downlist


def rillaget(url, dir_name, header):
    filename = url.split("/")[-1]
    total_path = dir_name + '/' + filename
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        with open(total_path, 'wb') as fd:
            for chunk in response.iter_content(1024):
                fd.write(chunk)
        print(f"{filename}  下载成功")


def bring_mms_home():
    soup = get_soup_from_webpage(
        'https://www.vmgirls.com/archives.html', header)
    postdict = make_list(soup)
    for posturl in postdict:
        print(f'正在打开：  {posturl}  {postdict[posturl]}')
        download_single_post(posturl, header)


if __name__ == '__main__':
    header = {
        'referer': 'https://www.vmgirls.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46'}
    bring_mms_home()
    print("～～完结撒花～～")
