import time
import requests
import re
from bs4 import BeautifulSoup
import os
from multiprocessing import Pool


webpage = "https://www.vmgirls.com/13487.html"

header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}

POOL = 10

def getHtml(webpage):
    response = requests.get(webpage,headers=header)
    content = response.text
    return content

content = getHtml(webpage)

def title(content):
    soup = BeautifulSoup(content, 'lxml')
    title = soup.title.get_text()
    return title

title = title(content)
print(title)

# 生成dir name
def dirname(content):
    dir_name = re.findall('<h1 class=\"post-title h1\">(.*?)</h1>',content)[-1]
    return dir_name

# 处理url
def getImg(content):
    
    # 4位数网页正则表达式
    re_img_u4 = r"<img alt=\".*?\" data-pagespeed-lsc-url=\"(.*?)\" src=\".*?\">" 

    # 5位数网页正则表达式
    re_img_u5 = r"<a href=\"(.*?)\" alt=\".*?\" title=\".*?\">"

    # 4位数网页
    urls_4 = re.findall(re_img_u4, content)
    # 5位数网页
    urls_5 = re.findall(re_img_u5, content)

    downlist = []

    # 4位数网页
    for url in urls_4:
        downlist.append(url)

    # 5位数网页
    for url in urls_5:
        url_noscaled = url.replace('-scaled','')
        url_hi = "https:" + url_noscaled
        downlist.append(url_hi)
    print(f'找到：{len(downlist)}个图片')
    
    return downlist

def start_download():
    pool = Pool(POOL)
    pool.apply_async(downloader(downlist))
    pool.close()
    pool.join()

dir_name = dirname(content)
downlist = getImg(content)

def total_path(dir_name):
    
    return total_path

def downloader(downlist):
    # 开始下载
    t1 = time.time() # 开始计时
    for url in downlist:
        file_name = url.split("/")[-1]
        try:
            response = requests.get(url, headers=header, timeout=15)
            if response.status_code == 200:
                if not os.path.exists(dir_name):
                    os.mkdir(dir_name)    
                total_path = dir_name + '/' + file_name
                if len(response.content) == int(response.headers['Content-Length']):
                    with open(total_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                        f.close()
                    print(file_name + "下载成功")
                else:
                    print("Image not complete")
        except:
            print("Connection dropped..")
            print("Wait for 5 seconds")
            time.sleep(5)
            print("Continue...")
            continue
    t2 = time.time()-t1
    print(f'{len(downlist)} 个图片下载成功，用时：{t2:.1f}秒')
    print()

if __name__ == '__main__':
    start_download()
