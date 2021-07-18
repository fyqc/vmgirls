import os
import requests
from bs4 import BeautifulSoup
from threading import Thread


# 2021年7月18日

def get_soup_from_webpage(url, header):
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8'
    return BeautifulSoup(response.text, 'lxml')


def get_dir(soup):
    return soup.title.get_text().split("丨")[0].strip()


def make_list(soup):
    postdict = {}
    div_archives = soup.find('div', class_='archives')
    tags_a = div_archives.find_all('a')
    url_pre = 'https://www.vmgirls.com/'
    for tag in tags_a:
        post_num_html = tag['href']
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
    print(f"  {get_dir(soup)}  ")
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

    # CASE 1 - ANY IMAGE NEWER THAN 17054
    div_nc_light_gallery = soup.find('div', class_="nc-light-gallery")
    a = div_nc_light_gallery.find_all('a')
    for n in a:
        img_url_incomplete = n.get('href')
        # 居然还有这种东西跑出来干扰
        # tag/%e6%91%84%e5%bd%b1/
        if 'img' in img_url_incomplete or 'image' in img_url_incomplete:
            img_url = 'https:' + img_url_incomplete
            downlist.append(img_url)
    
    # CASE 2 ANY IMAGE OLDER AROUND 2239
    img = div_nc_light_gallery.find_all('img')
    for n in img:
        img_url_incomplete = n.get('src')
        # print(img_url_incomplete)
        if 'img' in img_url_incomplete or 'image' in img_url_incomplete:
            img_url = 'https:' + img_url_incomplete
            downlist.append(img_url)
    
    return downlist


def rillaget(url, dir_name, header):
    response = requests.get(url, headers=header)
    if len(response.content) == int(response.headers['Content-Length']):
            filename = url.split("/")[-1]
            total_path = dir_name + '/' + filename
            with open(total_path, 'wb') as fd:
                for chunk in response.iter_content(1024):
                    fd.write(chunk)
            print(f"{filename}  下载成功")


def bring_mms_home():
    soup = get_soup_from_webpage(
        'https://www.vmgirls.com/archives.html', header)
    
    # 抛弃网页中的垃圾元素，加快处理速度
    for tag in soup.find_all("script"): soup.script.decompose()
    for tag in soup.find_all("style"): soup.style.decompose()
    
    postdict = make_list(soup)
    for posturl in postdict:
        print(f'正在打开：  {posturl}  {postdict[posturl]}')
        download_single_post(posturl, header)


if __name__ == '__main__':
    header = {
        'Referer':'https://www.vmgirls.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
    }
    
    bring_mms_home()
    
    print("～～完结撒花～～")
