import os
import requests
from bs4 import BeautifulSoup
from threading import Thread
import random
import time


""" 
WEB SCRAPING
TESTED ON WWW.VMGIRLS.COM
PYTHON 3.8.10

7/19/2021, 5:12 PM EST.

WHAT'S NEW:
* FIX BUGS.
* ADD RETRY FEATURE DUE TO UNRELIABLE SERVER CONNECTION.
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


def get_soup_from_webpage(url, header):
    '''
    Use BeautifulSoup to analyze the HTML.
    '''
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8'
    return BeautifulSoup(response.text, 'lxml')


def get_dir(soup):
    '''
    Get page title and used it as directory name.
    '''
    return soup.title.get_text().split("丨")[0].strip()


def make_list(soup):
    '''
    Obtain all the post URLs from Archieves page.
    '''
    postdict = {}
    div_archives = soup.find('div', class_='archives')
    tags_a = div_archives.find_all('a')
    url_pre = 'https://www.vmgirls.com/'
    for tag in tags_a:
        post_num_html = tag['href']
        if '17054' in post_num_html:  # <<<<<<< Stop Flag, change here as per your need
            break
        post_title = tag.get_text()
        posturl = url_pre + post_num_html
        if '#' in posturl:  # Remove the first unwanted URL
            continue
        postdict[posturl] = post_title
    return postdict


def download_single_post(posturl, header):
    soup = get_soup_from_webpage(posturl, header)

    # Dump the rest contents.
    for script in soup.find_all("script"):
        script.decompose()
    for style in soup.find_all("style"):
        style.decompose()

    print(f"  {get_dir(soup)}  ")
    downlist = extract_image_url(soup)
    if not downlist:
        print("There is no images in this page, skip.")
    else:
        # Remove duplicated links, if there is any
        downlist = list(set(downlist))  
        dir_name = 'D:/RMT/TRY/vmg/' + get_dir(soup)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)  # Create folder.
        threads = []
        for url in downlist:
            if not str(url).startswith('https://'):
                print("This url is not valid: " + url)
                continue
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
        # Remove anything such as below.
        # tag/%e6%91%84%e5%bd%b1/
        if 'img' in img_url_incomplete or 'image' in img_url_incomplete:
            img_url = str('https:' + img_url_incomplete).replace("-scaled", "")
            downlist.append(img_url)

    # CASE 2 ANY IMAGE OLDER AROUND 2239
    img = div_nc_light_gallery.find_all('img')
    for n in img:
        img_url_incomplete = n.get('src')
        if 'img' in img_url_incomplete or 'image' in img_url_incomplete:
            img_url = str('https:' + img_url_incomplete).replace("-scaled", "")
            downlist.append(img_url)

    return downlist


def i_dnt_wanna_cache(url):
    '''
    To prevent the Cloudflare's feature of cf-polish to resize our origin image.
    We use an random number after URL, to cheat the server.
    This will make sure that we can get the original size of image, with best iamge quality.
    '''
    false_random_number = random.randint(1533834270359, 1553834270359)
    return "".join([url, '?_=', str(false_random_number)])


def rillaget(url, dir_name, header):
    filename = url.split("/")[-1]
    total_path = dir_name + '/' + filename

    attempts = 0
    success = False

    while success is not True and attempts < 8:
        # Add a random time waiting period, reduce server's workload.
        time.sleep(random.uniform(1.1, 3.4))  
        try:
            response = requests.get(
                i_dnt_wanna_cache(url), headers=header, timeout=5)
        except:
            print(f"{filename} difficult to download, trying again.")
            try:
                response = requests.get(
                    i_dnt_wanna_cache(url), headers=header, timeout=5)
            except:
                print(f'{filename} really difficult to download.')
                attempts += 1
                continue

        if 'Content-Length' in response.headers:
            if len(response.content) == int(response.headers['Content-Length']):
                with open(total_path, 'wb') as fd:
                    for chunk in response.iter_content(1024):
                        fd.write(chunk)
                print(f"{filename}  {len(response.content)//1000}KB  Successfully downloaded. ")
                success = True

        elif len(response.content) > 100000:
            with open(total_path, 'wb') as fd:
                for chunk in response.iter_content(1024):
                    fd.write(chunk)
            print(
                f"{filename}  {len(response.content)//1000}KB  Successfully downloaded. But the image might not be complete.")
            success = True

        else:
            attempts += 1
            print(
                f"{filename} is only {len(response.content)}bytes. Will try {attempts + 1} times.  Status_code:{response.status_code}")
            time.sleep(random.uniform(1.1, 3.4))

        if attempts == 6:
            # The server may not has original resolution file exists.
            # Try use its original name, which contains"-scaled".
            url = str(url).replace(".jpeg", "-scaled.jpeg")
            url = str(url).replace(".png", "-scaled.png")
            url = str(url).replace(".jpg", "-scaled.jpg")
            url = str(url).replace(".webp", "-scaled.webp")
            total_path = str(total_path).replace(".jpeg", "-scaled.jpeg")
            total_path = str(total_path).replace(".png", "-scaled.png")
            total_path = str(total_path).replace(".jpg", "-scaled.jpg")
            total_path = str(total_path).replace(".webp", "-scaled.webp")
            print("Try to save the download with lower-resolution.")

        if attempts == 8:
            print(f'{filename}  Failed to download.  Status_code:{response.status_code}')


def bring_mms_home():
    soup = get_soup_from_webpage(
        'https://www.vmgirls.com/archives.html', header)

    # Dump all the unwanted elements from HTML.
    for script in soup.find_all("script"):
        script.decompose()
    for style in soup.find_all("style"):
        style.decompose()

    postdict = make_list(soup)

    for posturl in postdict:
        print(f'Now opens：  {posturl}  {postdict[posturl]}')
        download_single_post(posturl, header)


if __name__ == '__main__':
    header = {
        'Referer': 'https://www.vmgirls.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.70',
    }
    bring_mms_home()
    print("~~Fin~~")


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

