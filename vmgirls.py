import os
import requests
from bs4 import BeautifulSoup
from threading import Thread


""" 
WEB SCRAPING
TESTED ON WWW.VMGIRLS.COM
PYTHON 3.8.9

6/25/2021, 11:00 AM EST.

WHAT'S NEW:
* FIX BUGS
* CATCH UP THE MEASURES THAT WEBSITE HAS TO SUCCESSFULLY KEEP DOWNLOADING THE IMAGES.

INSTRUCTION:
1. Go to https://www.vmgirls.com/archives.html
2. The default page here in this code is set to stop at the
    https://www.vmgirls.com/15071.html/
3. The reason for above is due to the last version, I've already collected all the
images from posts that created earlier than that post.
4. You shall change the number as per your need at the definition of make_list(soup)
I've left a mark there to guide you.
5. Open TERMINAL (CMD / PowerShell), USE "python vmgirls.py" to start downloading. 
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
        # When I upload the code last year, this is where the lastest page located.
        # You shall change the number to any newest page you've downloaded, to avoid further time wasting.
        if '15071' in post_num_html:  # <<<<<< CHANGE THIS AS PER YOUR NEED <<<<<<
            break  # 16008 @ 4/27/2021
        post_title = tag.get_text()
        posturl = url_pre + post_num_html
        # https://www.vmgirls.com/15187.html
        # Has to remove the first element from list as below, to avoid the consequence.
        # 'https://www.vmgirls.com/#':
        if '#' in posturl:
            continue
        postdict[posturl] = post_title
    return postdict


def download_single_post(posturl, header):
    soup = get_soup_from_webpage(posturl, header)
    downlist = extract_image_url(soup)
    if not downlist:
        print("Somehow there is no images found in this page, skip this.")
    else:
        # Remove duplicated links, if there is any
        downlist = list(set(downlist))
        dir_name = get_dir(soup)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)       # Create folder as per page's title
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
        # Remove item such as below
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
    filename = url.split("/")[-1]
    total_path = dir_name + '/' + filename
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        with open(total_path, 'wb') as fd:
            for chunk in response.iter_content(1024):
                fd.write(chunk)
        print(f"{filename}  Download Successful")


def bring_mms_home():
    soup = get_soup_from_webpage(
        'https://www.vmgirls.com/archives.html', header)
    postdict = make_list(soup)
    for posturl in postdict:
        print(f'Now opening：  {posturl}  {postdict[posturl]}')
        download_single_post(posturl, header)


if __name__ == '__main__':
    header = {
        'referer': 'https://www.vmgirls.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46'}
    bring_mms_home()
    print("~~FIN~~")

#                                                                                                  El Psy Kongroo
#                                                                                         (&&@&@@@&@@&&&&&&&&&&&&&&@@@@%@*.                                                                              
#                                                                                  .*#@@&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&@@@/*                                                                          
#                                                                             .%@@&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&%&@@%,.                                                                   
#                                                                        *(@@&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&@#.                                                                 
#                                                                     ((&@&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&@##(                                                              
#                                                                    %@@&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&@@(                                                             
#                                                                  /&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&@&&&&&&&@@,                                                           
#                                                                 &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&@&&&&&&&&                                                           
#                                                               #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&@&&&&&&&@(/                                                        
#                                                            ,@@&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&@&&&&&&&@%                                                         
#                                                           #@@&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&@&&&&&&&&&&&&&&&&&@@&&&&&&&&                                                        
#                                                           @&&&&&&&&&&&&&&&&&&&&&&&&&@@&&&&&&&&&&&&&&&&@&&&&&&&&&&&&@@&&&&&&&&&&&&&&&&&&@&&&&&&&&                                                       
#                                                         *@&&&&&&&&&&&&&&&&&&&&&&&&&&&&@&&&&&&&&&&&&&&&@&&&&&&&&&&&&@@&&&&&&&&&&&&&&&&&&@&&&&&&&&&                                                      
#                                                         *@&&&&@&&&&&&@@&&&&&&&&&&&&&&&&@&&&&&&&&&&&&&&@&&&&&&&&&&&&&@&&&&&&&&&&&&&@&&&&&@&&&&&&&@%                                                     
#                                                        *&&&&&&@&&&&&&@&&&&&&&&&&&&&&&&&&@&&&&&&&&&&&&&&&@&&&&&&&&&&@@&&&&&&&&&&&&@%&&&&&@@&&&&&&&&(                                                    
#                                                       .@&&&&@&&&&@&&@@&&&&&&&&&&&&&&&&&&&@@&&&&&&&&&&&&&@&&&&&&&&&&&@%&&&&&&&&&&&&@&&&&&&@&&&&&&&&@,                                                   
#                                                      .%@&&&&@&&&&@&&&@&&&&&&&&&&&&&&&&&&&&&@&&&&&&&&&&&&@&&&&&&&&&&&@&&&&&&&@&&&&@@&&&&&&@&&&&&&&&@/                                                   
#                                                       %&&&&&@&&&&@&&&&@&&&&&&&&&&&&&&&&&&&&&@&&&&&&%&&&@@@@&&&&&&&&&@@&&&&&&&@&&&@@%&&&&&@@&&&&&&&@%                                                   
#                                                       @%&&&@@&&&&&@&&&@&&&&&&&&&&&&&&&&&&&&&@@&&&&&@@&&%@ ,@&&&&&&&&%@&&&&&&@@&&&&%@&&&&&&@&&&&&&&&@*                                                  
#                                                       &&&&&@&&&&&&@&&&&&@&&&&&&&&&&&&&&&&&&&&@@&&&&&@&&&@  ,@&&&&&&&&@&&&&&&@&&&&@@@&&&&&&&@&&&&&&&@*                                                  
#                                                      (&&&&&@&&&&&&&@&&&&@@&&&&&&&&&&&&&&&&&&&&@&&&&&@&&@* .//@@@@@@@@@&&&&&&@&&&&@&@&&&&&&&@@&&&&&&@*                                                  
#                                                      ,&&&&&@@&&&&&&&@&&&&@@&&&&&&&&&&@@&&&&&&&&@&&&@@&@@@&%./&&@@&&&@@&&&@@@&&&&&&%&@&@&&&&&@&&&&&&@%                                                  
#                                                      *&&&&&@%&&&@@&@,@&&&@&(&&&&&&&&&&&@@&&&&@@@@@@@@%&@@@@@@@@@@@@@&@@&@@@&@&&&&@@@.   .@&&@&&&&&@@%                                                  
#                                                       &&&&&&@&&&@&&@, *@&&&/,@@&&&&&@&&&@&&&&&&@&@&@&@@&*@@@///////@&@&&@&&@&&&&&&@#%*.%,@&&&&&&&&&@&                                                  
#                                                       &&&&&&&@&&&@&@,  ,@&&@//(@@&&&&@@&&&& (@&&@@@@@/,%(  #////////&@&@@&&@&&&&&@@(%/  .@&&&&&&&&&@@,                                                 
#                                                       &@&&&&@@&&@@@@      ,@@/   (@@&&&@@%&@ .%@@@@&%,#     /@*/////#@@@&&&@&&&&&@@*  */.@&&&&&&&&@@@,                                                 
#                                                       .@&&&&&@&&&&@&@@#  @@@@@@@@@@@@&@@&@%@&@  @@@*           ,@@   @&&&&@@&&&&&@@@ *# .@&&&&&&&&&@@*                                                 
#                                                        &&&&&&&@@&&@@&@@@,*#///*////%/  %.*&@@*@. .@,                 @@&&&@&&&&&@@@@%, /@&&&&&&&&&@@@%                                                 
#                                                       .@&&&&&&&@@&@@&@.   &(///////%&   &,   &,                      @@&&&@&&&&&@@@@,.@&&&&&&&&&&&@@@&                                                 
#                                                        /@&&&&&&&@@&&@*&@/ .@*////(@%     %,                         .@&&&@@&&&&&@@@@@@&&&&&&&&&&&&@&&@%                                                
#                                                         &&&&&&&&@@@@@@# ..   .....        &.                        ,@&&&@&&&&&@@@%&@&&&&&&&&&&&&&@@&@&                                                
#                                                         (@&&&&&&&@@@@@@@,                                           ,@&&&@&&&&&@@@&&@&&&&&&&&&&&&@@&&&@.                                               
#                                                         #@&&&&&&&@@@@@@@@*                 .*.                      ,@&&@@&&&&&@@@&&@@&&&&&&&&&&@@&@&&@/                                               
#                                                          @&&&&&&&@@@@@@@@@@.                 .%@.                   ,@&%@&&&&&@@@@&&&@&&&&&&&&&&@&@@&&@/                                               
#                                                           &&&&&&&&@@@@@@@@@@@                                       &%&&@&&&&&@@%&&&&&&&&&&&&&&@&&%@&&&@,                                              
#                                                           *@&&&&&&@@@@@@@@@@@@&                          .#         &&&@&&&&&&@@&&&&&&&&&&&&&&&@&&&@&&&&#                                              
#                                                            &%&&&&&@@@@@@@@@@@@@@&.           .&&&&*                 &@&@&&&&&&@@&&&&&&&&&&&&&&%@&&@@&&&&@/                                             
#                                                            *@@&&&&@@@@@@@@@@@@@@@@@&                               @@%&@&&&&&@%&&&&&&&&&&&&&&&@@&&@@&&&&@&                                             
#                                                             *@&&&&&@@@@@@@@@@@@@@@@@@@@@*                      .@( ,@&@&&&&&&@&&&&&&&&&&&&&&&&@&&&&@@@&&&&&                                            
#                                                             .@@&&&&&@@@@@@@@@@@@@@@@@@@@@@@&(,              ,%(.   /&&@&&&&&@@&&&@&&&&&&&&&&&&@&&&@@@@&&&&@%                                           
#                                                              &&@&&&&@@@@@@@@@@@@@@@@@@@@@@@@@@@@&*.     ,*@@%*///**%&@@&&&&@@&&&&@&&&&&&&&&&&@@&&&@@@@@&&&&&                                           
#                                                              *@&@@&&&@@@@@@@@@@@@@@@@@@@@@@@@@@@@(/@@@@/.@%&#.,,,..@@@@&&&@@&&&&@&&&&&&&&&&&&@&&&@@@@@@&&&&@@/                                         
#                                                               @&&&@&&&@@@@@@@@@@@@@@@@@@@#@@@@@@@&%@/(//**@(@/((/*%&&@&&&&@@&&&&@&&&&&&&&&&&&@&&&@@@@@@@@&&&&&@,                                       
#                                                              ,@&&&&@&&&@@@@@@@@@@@@@@@@@@(@@@@@@@%(@*&  @./##@***,&@,@&&&&&@&&&&@&&&&&&&&&&&@@&&&@@@@@@@@&&&&&&&@.                                     
#                                                              .@&&&&&@&&&@@@@@@@@@@@@@@@&@(@@@@@@@#*&,&,,@.,&#&(*,,@/,@&&&&&@&&&&@&&&&&&&&&&&@&&&&@@@@@@@@@&&&&&&&@/                                    
#                                                               &&&&&&&@@&@@@@@@@@@@@@@@@(@#%@@@@@@@#@@&/&@@@@@(&#(&(/(@&&&&@&&&&&@&&&&&&&&&&&@&&&@@@@@@@@@@@&&&&&&&&@&.                                 
#                                                               @&&&&&&&&@&@@@@@@@@@@@@@,....&@@@@#@   &,,. .,,@/,#...,@&&&&&@&&&@@&&&&&&&&&&@&&&&@@@@@@@@@@@@&&&&&&&&&@%(                               
#                                                               @&&&&&&&&&@&@@@@@@@@@@@@@@@@@@@@@#@*  (/   .,**@@(@/,**@&&&&&@&&&&@&&&&&&&&&&&&&&&@@@@@@@@@@@@@&&&&&&&&&&%.                              
#                                                              %&&&&&&&&&&&@&@@@@@@@@@@@@@@@@@@/*@@,  %    **#&%%@#&(//@&&&&@&&&&&@&&&&&&&&&&&&&&@@@@@@@@@@@@@@@&&&&&&&&&&@*                             
#                                                             *@&&&&&&&&&&&&@@@@@@@@@@&..,,@@/@&%%%( @    . @%%%%%@(##&@@&&&&@&&&@@&&&&&&&&&&&&&&@@@@@@@@@@@@@@@@@&&&&&&&&&@@*                           
#                                                            #@&&&&&&&&&&&@@@&((#/(**#%&/##&@%%%%%%@&   /**@%%%%%%%%&&/*@&&&@@&&&&@&&&&&&&&&&&&&&@/****/(#@@@@@@@@@&&&&&&&&&&@                           
#                                                            /(@/&@@%(((**,,,*,,    ,///,**/@#%%%%%&* .***@%%%%%%%%%%(((@&&&&&&&&&@@&&&&&&&&&&&&&&*,,*,/((((((((/(((((((@@&&&&@.                         
#                                                     /@.....,@,...,,,,,,,.             .,,,&%%%%%%%@,,*,@%%%%%%%%%&*,,./&&&&&&&&&&@&&@&&&&&&&&&&%,,,,..,,,,,,,,...,*/#,,..&@@@@@@                       
#                                                   (&(,,*/(#%(/*/////.                 ./((&%%%%%%&%/#@%%%%%%%%%%%////*/#@&&&&&&&&&@&@@&&&&&&&&@(/////*/(/((///**//&#/(//**///@,/*                      
#                                                  (@@(.....%**,..          .,&(          ,*&@&%%%%%#%%%%%%%%%@&**,,.,,..,%&&&&&&&&&@&&@&&&&&&&&@*,,.,..,,,*,,,,...@*,,*,...,/@@&@..                     
#                                                  (&%%.,,**/%**        ,**,#%             /@%&&&%@&%#%%%&@#&***//*****,**/@&&&&&&&&@&&&@&&&&&&&@/**,**,***/****,,%(/**/**,,%%%#(#.,.                    
#                                                  (%(#,**//(%//     ./(//&**.             /@%%%%#@@%&@@%//@/////(//*/***//(@&&&&&&&@@&&@&&&&&&&@(//*/**///(////*(%/(/////@&#(#(,/,*,,                   
#                                                 %@@@@,....*#,.. ..,,,,@..                *@%%%%%%%%%%%#.% .,..,,,..,...,,,/@&&&&&&%@&&&&@&&&&&%%,......,,,,.,..&..,../@@@@@@@@@@#....                  
#                                                */*&@#&#**/*&//***//*/&//******           /@%%%%%%%%%&#/%/,*/*////**/***/////@&&&&&&&@@&&@&&&&&&@/**/**/////*//@**//##/(%&%#(%(*/(*,,,.                 
#                                               /#(*,(&&%%&*,/&*,***@*&/***,,****/.       ./@%%%%%%%%&//(%*,.    ******,***/***&&&&&&&&&@&&@&&&&&@#****,***/***@,,,*#@%##&&&%#%#(#%,,,,.                 
#                                              #&&%...#@@@&&*./(...((#/*,,,..,,,,,*,      ,*&%%%%%%&&,,*&,..          ..,,,,,,,.@&&&&&&&&@&@@&&&&&#,.,..,,,*,.@....,&&&&@@@@@@@@&&@/......               
#                                             .(//.*,***%(/*((/&**(&@/((///*/////((/*,   //(&%&@@@@/. /&(//*,             /(////*@&&&&&&&&@&@&&&&&@/*//*/(/(/@//*//@,/(*/%%%((#/,/(.,*****((             
#                                            *@@&@&,....(@@&@@@@&,@*,,        .,,,*,.,. .,*@%%%#&,.   %,,,,..                ,,,../&&&&&&&&@&@&&&&&/,,,.,,,*,,,,..&&&&@&@@@@@@@&&@&(.......,%            
#                                            %&&%%%,.,,../@%&&%&@&,,             .*,,,,,,,/&##%#&,,, *(  *,..                 .,,,,(&&&&&&&&@@@&&&&@,,,,,****,,,,(&%#%%@%&&&&&&%#%%*,,...,,,,&,          
#                                           @#%#//*.,**,,*#*((/@/**                .*//*//&%#%%%&//* @    **,...               ,***/%@&&&&&&&&@@&&&@(***/////////&%(,(@/(#%%((#(,/(.******/(/*%*         
#                                         /@@@@@@@@(........@@#,..                   ,,..,@%%%%%@... @      &/                &&@,.,**@&&&&&&&&&&&&&*....,,,,.,,@@@@@@@@@@@@@@@@@@@............,#        
#                                      /@##%%%%//((/,**,,*/#&//,                      .,*@%%%%%%@***#*      &//(%##//((*/&%%*      ,((#@&&&&&&&&&&&&@/***/////*&%%@@*(#/(%%%((%(*(**,*,*,*/(,,/,,*       
#                                     &(#%%&&%/*****,,,,,,(@**                         ,*@#%%%%%@,**%.     @##%#%&%#(#(////////%&&@*%#/*(&@&&&&&&&&&&@****&//*&@&@&#(#%(#%&&%#/**,,*,*,*,,,/,,*,,,&      
#                                      #@@@@@@@@,........@@*,                          ./%#%%%%&*..,@     %                &@@@&#(#(/*//((@@&&&&&&&&&@&..,&,,#@@@@@@@@@@@@@*........%@@@@@.,.....*&      
#                                       /@#%%(#(/*(/,**.#@%(/*                         .@##%%%%&///#*     @                  .//*///((&@@(**@&&&&&&&&&&&//@(#@(&%%%(,(((/*,,***,,/((%%%%&////***,&       
#                                       %@@@&&&&&&%%*,@@@@(*,/*                        %%##%%%%&*,,((    (*               .*,,,,,,,,*,,/%,,.,(@&&&&&&&&@#,@/@@@&&@@&*,,,,,,%&&&%%@@&&*.,,,,,,.,,%/       

""" 
After six months, my skills have improved some more.
Revisited this site and refactored my code.
Used the multi-threaded power tool.
Found out that the webmaster has taken some new measures, including
    Disabled Firefox's "developer options"
    Surreptitiously changed the suffix of images that are actually in Webp format to Jpeg
    Also added server-side validation, when the request header is detected without wrapping the Referrer, it returns a 404 code
Fortunately, today's me is not yesterday's me, these measures may be able to stop some curious people for a while.
But for people who are bent on getting resources, what kind of results this can have, I hope the webmaster will think twice.
"""


# import time
# import requests
# from bs4 import BeautifulSoup
# import os

# # WEB SCRAPING
# # TESTED ON WWW.VMGIRLS.COM
# # 11/13/2020, 1:22 PM EST.
# # PYTHON 3.8.6

# # INSTRUCTION:
# # PUT ALL THE URL OF EACH WEBPAGE INTO A TEXT FILE, AND PUT THAT TXT FILE UNDER THE SAME FOLDER AS THIS PY FILE.
# # IN TERMINAL, USE "python vmgirls.py" AS START COMMAND.


# header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}

# playlist=[]

# with open(r'example.txt','r') as f: # CHANGE NAME OF FILE AS YOU NEED.
#     for line in f:
#         playlist.append(list(line.strip('\n').split(',')))

# for URL in playlist:
#     url = URL[0]
#     print(f'The web that open: {url}')

#     response = requests.get(url,headers=header)
#     content = response.text
#     soup = BeautifulSoup(content, 'lxml')

#     # ACQUIRE WEBPAGE TITLE
#     title = soup.title.get_text()
#     dir_name = title[:-7]
#     print(title) # PRINT WEBPAGE TITLE

#     downlist = []

#     # TAG <div>, class = nc-light-gallery
#     div = soup.find_all('div', class_ ='nc-light-gallery')
#     # USE lxml TO PROCESSING HTML
#     img_bf = BeautifulSoup(str(div[0]), 'lxml')
#     # <a> href
#     # <a href="//static.vmgirls.com/image/2019/06/2019-06-05_13-20-11.jpg" alt=Halcyon title=Halcyon>
#     tag_a = img_bf.find_all('img')
#     for each in tag_a:
#         url_direct = each.get('data-pagespeed-lsc-url')
#         # DELETE "-scaled" FROM URL-DIRECT
#         if url_direct is not None:
#             url_noscaled = url_direct.replace('-scaled','')
#         # NOW THE URL IS CLEAN, AND LOADED TO downlist, READY FOR DOWNLOAD
#             downlist.append(url_noscaled)

#     # USE static.vmgirls.com AS KEY WORD TO VERIFY ALL THE LINKS
#     # MAKE SURE ALL THE LINKS ARE DOWNLOADABLE.
#     for dontwant in downlist:
#         if dontwant is not None:
#             if 'static.vmgirls.com' not in dontwant:
#                 downlist.remove(dontwant)


#     # print(downlist) # THIS IS FOR TEST PURPOSE, TO CHECK ALL THE LIST MANUALLY.

#     # COUNT THE NUMBER OF LINKS IN downlist
#     print("Found " + str(len(downlist)) + "images")

#     # DOWNLOAD START
#     t1 = time.time() # TIME COUNT START
#     filenumber = 0
#     for url in downlist:
#         file_name = url.split("/")[-1]
#         attempts = 0 # SHALL THERE IS NETWORK ISSUE, THIS WILL AUTOMATCIALLY RETRY THE DOWNLOAD FOR THAT FILE 5 TIMES.
#         success = False
#         while attempts < 5 and not success:
#             try:
#                 response = requests.get(url, headers=header, timeout=15)
#                 if response.status_code == 200:
#                     if not os.path.exists(dir_name):
#                         os.mkdir(dir_name)
#                 total_path = dir_name + '/' + file_name

#                 if 'Content-Length' in response.headers and len(response.content) == int(response.headers['Content-Length']):
#                     with open(total_path, 'wb') as f:
#                         for chunk in response.iter_content(1024):
#                             f.write(chunk)
#                         f.close()
#                     print(file_name + "has been downloaded.")

#                 else:
#                     # DUE TO THE HTTP FILE, SINCE Content-Length IS NOT AVAILABLE, THE IMAGE MAY NOT COMPLETELY DOWNLAOD.
#                     # SHALL THAT OCCUR, A PORTION OF GREY COLOR MAY SHOWN ON BOTTOM SECTION OF THAT IMAGE.
#                     # A MANUAL EXAMINATION OF EACH IMAGE IS HIGHLY RECOMMANED.
#                     print("The image may not be completed.")
#                     with open(total_path, 'wb') as f:
#                         for chunk in response.iter_content(1024):
#                             f.write(chunk)
#                         f.close()
#                     print(file_name + "has been downloaded.")

#                 success = True

#             except:
#                 attempts += 1
#                 if attempts == 5:
#                     break
#             filenumber += 1

#     t2 = time.time()-t1
#     failnumber = filenumber - int(len(downlist))
#     print(f'There is/are {filenumber} image(s) downloaded, and that took：{t2:.1f} seconds.')
#     if failnumber > 0:
#         print(f'Caution, there is/are {failnumber} file(s) failed to be downloaded.')
#     print()







'''
FOUND THE FOLLOWING CODE ON SOMEONE ELSE'S WEBSITE.
WAS ABLE TO USE ON CERTAIN PAGES. [NOTE: WON'T WORK AT ALL AT 2021]
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

