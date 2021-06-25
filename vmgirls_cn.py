import os
import requests
from bs4 import BeautifulSoup
from threading import Thread


""" 
时隔六个月，技艺又增进了一些。
重访这个网站，重构我的代码。
用上了多线程的强力工具。
发现站长采取了一些新的措施，包括：
    禁用了Firefox的“开发者选项”
    偷偷地把实际上为Webp格式的图片的后缀改为Jpeg
    此外还添加了服务器端的验证，当检测出请求头没有包裹Referrer的时候，就返回404代码
幸好今日之我已非昨日之我，这些措施或许可以一时挡住某些好奇人士的脚步，
可是对于一心想要获取资源的人来说，这究竟能起到怎样的结果，还望站长三思。
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
        # https://www.vmgirls.com/15187.html

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
        # 上一个版本在这里有一个多余的else，简直匪夷所思，脑子大概瓦特了……
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
        # 居然还有这种东西跑出来干扰
        # tag/%e6%91%84%e5%bd%b1/
        if 'image' not in img_url_incomplete:
            continue
        img_url = 'https:' + img_url_incomplete
        downlist.append(img_url)
    return downlist


def rillaget(url, dir_name, header):
    fake_filename = url.split("/")[-1]
    real_filename = fake_filename.replace('jpeg', 'webp')
    total_path = dir_name + '/' + real_filename
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        with open(total_path, 'wb') as fd:
            for chunk in response.iter_content(1024):
                fd.write(chunk)
        print(f"{real_filename}  下载成功")


def bring_mms_home():
    soup = get_soup_from_webpage(
        'https://www.vmgirls.com/archives.html', header)
    postdict = make_list(soup)
    for posturl in postdict:
        print(f'正在打开：  {posturl}  {postdict[posturl]}')
        download_single_post(posturl, header)


def convert_webp_to_jpeg():
    # 调用ffmpeg把下载回来的webp转为jpeg
    os.system(r'for %i in (*.webp) do ffmpeg -i "%i" "%~ni.png" -loglevel quiet')


if __name__ == '__main__':
    header = {
        'referer': 'https://www.vmgirls.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46'}
    bring_mms_home()
    print("～～完结撒花～～")
