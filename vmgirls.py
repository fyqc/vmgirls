import time
import requests
from bs4 import BeautifulSoup
import os

# WEB SCRAPING
# TESTED ON WWW.VMGIRLS.COM
# WRITTEN BY FYQ
# 11/13/2020, 1:22 PM EST.
# PYTHON 3.8.6

# INSTRUCTION:
# PUT ALL THE URL OF EACH WEBPAGE INTO A TEXT FILE, AND PUT THAT TXT FILE UNDER THE SAME FOLDER AS THIS PY FILE.
# IN TERMINAL, USE "python vmgirls.py" AS START COMMAND.


header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}

playlist=[]

with open(r'example.txt','r') as f: # CHANGE NAME OF FILE AS YOU NEED.
    for line in f:
        playlist.append(list(line.strip('\n').split(',')))

for URL in playlist:
    url = URL[0]
    print(f'The web that open: {url}')

    response = requests.get(url,headers=header)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')

    # ACQUIRE WEBPAGE TITLE
    title = soup.title.get_text()
    dir_name = title[:-7]
    print(title) # PRINT WEBPAGE TITLE

    downlist = []

    # TAG <div>, class = nc-light-gallery
    div = soup.find_all('div', class_ ='nc-light-gallery')
    # USE lxml TO PROCESSING HTML
    img_bf = BeautifulSoup(str(div[0]), 'lxml')
    # <a> href 
    # <a href="//static.vmgirls.com/image/2019/06/2019-06-05_13-20-11.jpg" alt=Halcyon title=Halcyon>
    tag_a = img_bf.find_all('img')
    for each in tag_a:
        url_direct = each.get('data-pagespeed-lsc-url')
        # DELETE "-scaled" FROM URL-DIRECT
        if url_direct is not None:
            url_noscaled = url_direct.replace('-scaled','') 
        # NOW THE URL IS CLEAN, AND LOADED TO downlist, READY FOR DOWNLOAD
            downlist.append(url_noscaled)

    # USE static.vmgirls.com AS KEY WORD TO VERIFY ALL THE LINKS
    # MAKE SURE ALL THE LINKS ARE DOWNLOADABLE.
    for dontwant in downlist:
        if dontwant is not None:
            if 'static.vmgirls.com' not in dontwant:
                downlist.remove(dontwant)


    # print(downlist) # THIS IS FOR TEST PURPOSE, TO CHECK ALL THE LIST MANUALLY.

    # COUNT THE NUMBER OF LINKS IN downlist
    print("Found " + str(len(downlist)) + "images")

    # DOWNLOAD START
    t1 = time.time() # TIME COUNT START
    filenumber = 0
    for url in downlist:
        file_name = url.split("/")[-1]
        attempts = 0 # SHALL THERE IS NETWORK ISSUE, THIS WILL AUTOMATCIALLY RETRY THE DOWNLOAD FOR THAT FILE 5 TIMES.
        success = False
        while attempts < 5 and not success:
            try:
                response = requests.get(url, headers=header, timeout=15)
                if response.status_code == 200:
                    if not os.path.exists(dir_name):
                        os.mkdir(dir_name)        
                total_path = dir_name + '/' + file_name
                
                if 'Content-Length' in response.headers and len(response.content) == int(response.headers['Content-Length']):
                    with open(total_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                        f.close()
                    print(file_name + "has been downloaded.")

                else:
                    # DUE TO THE HTTP FILE, SINCE Content-Length IS NOT AVAILABLE, THE IMAGE MAY NOT COMPLETELY DOWNLAOD.
                    # SHALL THAT OCCUR, A PORTION OF GREY COLOR MAY SHOWN ON BOTTOM SECTION OF THAT IMAGE.
                    # A MANUAL EXAMINATION OF EACH IMAGE IS HIGHLY RECOMMANED.
                    print("The image may not be completed.")  
                    with open(total_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                        f.close()
                    print(file_name + "has been downloaded.")

                success = True
                
            except:
                attempts += 1
                if attempts == 5:
                    break
            filenumber += 1            

    t2 = time.time()-t1
    failnumber = filenumber - int(len(downlist))
    print(f'There is/are {filenumber} image(s) downloaded, and that took：{t2:.1f} seconds.')
    if failnumber > 0:
        print(f'Caution, there is/are {failnumber} file(s) failed to be downloaded.')
    print()






'''
FOUND THE FOLLOWING CODE ON SOMEONE ELSE'S WEBSITE.
WAS ABLE TO USE ON CERTAIN PAGES.
HOWEVER, IT WON'T WORK ON ANY HTML THAT CONTAINS ONLY FOUR DIGITS.
THEREFORE, I DECIDED TO RE-WRITE A MORE RELIABLE AND MORE COMPLEX CODE TO EXTRACT AND WORK ON ALL THE PAGES OF WWW.VMGIRLS.COM
BUT, HIS/HER CODE INSPIRED ME FROM THE BEGINNING, AND I ADMIRE THAT IT WAS SUCH TINY BEAUTIFUL CODE AND DID WORK ON THHOSE PARTICULAR PAGES.
'''


# import requests
# import re
# import os
# # requests.packages.urllib3.disable_warnings()
# kv={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}
# r=requests.get("https://www.vmgirls.com/13734.html",headers=kv)
# r.raise_for_status()
# r.encoding=r.apparent_encoding
# haha=re.findall('<a href="(.*?)" alt=".*?" title=".*?">',r.text)
# dir_name=re.findall('<h1 class="post-title h3">(.*?)</h1>',r.text)[-1]
# if not os.path.exists(dir_name):
#     os.mkdir(dir_name)
# for url in haha:
#     file_name=url.split("/")[-1]
#     meizi=requests.get(url,headers=kv)
#     with open(dir_name+'/'+file_name,'wb') as f:
#         f.write(meizi.content)

