import os
import requests
import random
import time
from bs4 import BeautifulSoup
from threading import Thread


"""
2021年11月11日 木曜日

もともと、大きなインターネットの写真を引っ張るコードはどこにでもあるはずだと思っていたのですが、結局、Pythonを始めたときは、知乎からCSDNへのチュートリアルとして使っていました。
意外にも、Githubを検索したところ、そのコードに関連するページは1つだけです。
それ以来、私は更新するのが愚かで、それはあまりにも目立ちます。結局のところ、昨年Webサイトが変更されて以来、新しい所有者はWebサイトがクロールされないようにあらゆることを行い、嫌なことではないひどいJSを大量にロードしました。これは、実際にはコンピューター全体のドラッグです。
人々がウェブサイトをクロールするのを恐れるために、開発者ツールは無効になっています。携帯電話でアクセスするとページが自動的に閉じられるという副作用は考えられませんでした。今回は、モバイル端末からのトラフィックです。食べられなくなります。
他人に這われないようにするために、この方法でも行われており、作者の無力感や怒りを感じることができます。
とにかく商業的価値のあるサイトだと思いましたが、昔のことわざにもあるように、人の財産を切ることは親を殺すようなものです。作者が私を切るのを防ぐために、ここで更新することにしました。
写真を撮ったので、その方法は教えません。
みなさんおやすみなさい。
"""


def get_soup_from_webpage(url, header):
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')

    # に追加された新しい検出機能は
    # 塔のファイアウォールの自動リダイレクトを処理するために使用されました
    if soup.title.get_text() == '检测中':
        # BeautifulSoupが処理できるように
        # 意図的に外部に追加されたjsスクリプト</ html>をそのスクリプトに取り込みます。
        html = response.text.replace('</html>', '') + '</html>'
        url = find_redirect_url_from_script(html)
        print(f"URLはにリダイレクトされます:")
        print(url)
        header['Referer'] = url
        return get_soup_from_webpage(url, header)

    else:
        # ウェブページのゴミ要素を捨てて、処理速度を上げてください
        for script in soup.find_all("script"):
            script.decompose()
        for style in soup.find_all("style"):
            style.decompose()
        return soup


def find_redirect_url_from_script(html):
    tag_script = BeautifulSoup(html, 'lxml').find_all('script')[-1]
    btwaf = tag_script.string.split("/")[-1].replace('";', '')
    prefix = 'https://www.vmgirls.com/'
    btwaf_url = (prefix + btwaf).strip()  # URLにスペースがあり、本当に衝撃的です
    return btwaf_url


def lets_wait(timer=20):
    while timer > 0:
        time.sleep(1)
        print(f"お待ちください{timer}秒")
        timer -= 1
    print("終わりを待って、続けましょう")


def get_dir(soup):
    return soup.title.get_text().split("丨")[0].strip()


def make_list(soup):
    '''「アーカイブ」からすべての投稿のリストを取得します'''
    postdict = {}
    div_archives = soup.find('div', class_='archives')
    tags_a = div_archives.find_all('a')
    url_pre = 'https://www.vmgirls.com/'
    for tag in tags_a:
        post_num_html = tag['href']
        # 停止するには、ここでページ番号を変更してください
        # <<<<<<<<<<<<<<<<<  CHANGE THE PAGE NUMBER HERE FOR STOPPAGE.
        if '15071' in post_num_html:
            break
        post_title = tag.get_text()
        posturl = url_pre + post_num_html
        # ここでは、最初のアイテムを除外します。これは、＃が付いている唯一のアイテムです。
        # 'https://www.vmgirls.com/#': '全部展开/收缩'
        if '#' in posturl:
            continue
        postdict[posturl] = post_title
    return postdict


def download_single_post(single_post_soup, header):
    '''1つのページですべての画像アドレスを解析し、マルチスレッドダウンロードのためにダウンローダーを呼び出します'''

    downlist = extract_image_url(single_post_soup)
    if not downlist:
        print("この投稿には写真がありません。スキップしてください～～")
    else:
        downlist = list(set(downlist))  # ダウンリストの重複排除
        dir_name = 'D:/RMT/TRY/vmg/' + get_dir(single_post_soup)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)  # フォルダーを作る
        threads = []
        for url in downlist:
            if not str(url).startswith('https://'):
                print("奇妙なURLを混ぜる: " + url)
                continue
            t = Thread(target=rillaget, args=[url, dir_name, header])
            t.start()
            threads.append(t)
        for t in threads:
            t.join()


def extract_image_url(soup):
    '''ウェブページのスープから元の画像のURLを精製する'''
    downlist = []

    # ケース1 - 17054より新しい画像
    div_nc_light_gallery = soup.find('div', class_="nc-light-gallery")
    a = div_nc_light_gallery.find_all('a')

    for n in a:
        img_url_incomplete = n.get('href')
        # 干渉するために不足しているこの種のものがまだあります
        # tag/%e6%91%84%e5%bd%b1/
        if 'img' in img_url_incomplete or 'image' in img_url_incomplete:
            img_url = str('https:' + img_url_incomplete).replace("-scaled", "")
            downlist.append(img_url)

    # ケース2 2239周りの古い画像
    img = div_nc_light_gallery.find_all('img')
    for n in img:
        img_url_incomplete = n.get('src')
        if 'img' in img_url_incomplete or 'image' in img_url_incomplete:
            img_url = str('https:' + img_url_incomplete).replace("-scaled", "")
            downlist.append(img_url)

    return downlist


def i_dnt_wanna_cache(url):
    '''URLの後にタイムスタンプを追加するなど、キャッシュヒットを防ぐために、ランダムな疑似パラメータをURLに追加します'''
    false_random_number = random.randint(1533834270359, 1553834270359)
    return "".join([url, '?_=', str(false_random_number)])


def rillaget(url, dir_name, header):
    filename = url.split("/")[-1]
    total_path = dir_name + '/' + filename

    attempts = 0
    success = False

    while success is not True and attempts < 8:
        time.sleep(random.uniform(1.1, 3.4))  # サーバーフライヤーを回避するためにランダムな待機を追加します
        try:
            response = requests.get(
                i_dnt_wanna_cache(url), headers=header, timeout=5)
        except:
            print(f"{filename} ダウンロードの問題、ネットワーク接続の不良、再試行")
            try:
                response = requests.get(
                    i_dnt_wanna_cache(url), headers=header, timeout=5)
            except:
                print(f'{filename} ダウンロードするのは本当に難しいです')
                attempts += 1
                continue

        if 'Content-Length' in response.headers:
            if len(response.content) == int(response.headers['Content-Length']):
                with open(total_path, 'wb') as fd:
                    for chunk in response.iter_content(1024):
                        fd.write(chunk)
                print(f"{filename}  {len(response.content)//1000}KB  ダウンロードに成功 ")
                success = True

        elif len(response.content) > 40000:  # 40KBある限りダウンロード
            with open(total_path, 'wb') as fd:
                for chunk in response.iter_content(1024):
                    fd.write(chunk)
            print(
                f"{filename}  {len(response.content)//1000}KB  ダウンロードは成功しますが、不完全になるリスクがあります")
            success = True

        else:
            attempts += 1
            print(
                f"{filename} それだけ {len(response.content)}bytes "
                f"{attempts + 1}回目に再試行してください  status_code:{response.status_code}")
            lets_wait(attempts*3)

        if attempts == 6:
            # サーバー上に縮尺のない画像がない可能性があります。元のファイル名を復元してダウンロードしてみてください
            url = str(url).replace(".jpeg", "-scaled.jpeg")
            url = str(url).replace(".png", "-scaled.png")
            url = str(url).replace(".jpg", "-scaled.jpg")
            url = str(url).replace(".webp", "-scaled.webp")
            # ファイル名もそれに応じて変更されます
            total_path = str(total_path).replace(".jpeg", "-scaled.jpeg")
            total_path = str(total_path).replace(".png", "-scaled.png")
            total_path = str(total_path).replace(".jpg", "-scaled.jpg")
            total_path = str(total_path).replace(".webp", "-scaled.webp")
            print("HD以外の画像をダウンロードしてみてください")

        if attempts == 8:
            print(f'{filename}  ダウンロードに失敗しました status_code:{response.status_code}')


def get_soup_from_localhtml(webpage):
    soup = BeautifulSoup(open(webpage, encoding='utf-8'), features='lxml')
    # ウェブページのゴミ要素を捨てて、処理速度を上げてください
    for script in soup.find_all("script"):
        script.decompose()
    for style in soup.find_all("style"):
        style.decompose()
    return soup


def bring_kanojo_home(header):
    top_list_soup = get_soup_from_webpage(
        'https://www.vmgirls.com/archives.html', header)

    postdict = make_list(top_list_soup)

    for posturl in postdict:
        print(f'オープニング：  {posturl}  {postdict[posturl]}')
        # ホスティングサーバーのオペレーターが不可解な5秒間の「ジャンプ」を実行するように描画されないようにするには、次のコードを追加します。
        single_post_soup = get_soup_from_webpage(posturl, header)
        while get_dir(single_post_soup) != postdict[posturl]:
            print(get_dir(single_post_soup))
            lets_wait()
            single_post_soup = get_soup_from_webpage(posturl, header)
            print(get_dir(single_post_soup))

        download_single_post(single_post_soup, header)


if __name__ == '__main__':
    header = {
        'Referer': 'https://www.vmgirls.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
        ' (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
    }

    bring_kanojo_home(header)

    print("～～終わりに、花～～")
