# 图片托管在Cloudflare被压缩过的，如何下载原始无压缩图片  

本文转自： 

[Jeepeng的博客](https://blog.jeepeng.com/)  格式有改动

Posted on 2018-12-03

[https://blog.jeepeng.com/2018/图片托管在Cloudflare被压缩过的，如何下载原始无压缩图片/](https://blog.jeepeng.com/2018/%E5%9B%BE%E7%89%87%E6%89%98%E7%AE%A1%E5%9C%A8Cloudflare%E8%A2%AB%E5%8E%8B%E7%BC%A9%E8%BF%87%E7%9A%84%EF%BC%8C%E5%A6%82%E4%BD%95%E4%B8%8B%E8%BD%BD%E5%8E%9F%E5%A7%8B%E6%97%A0%E5%8E%8B%E7%BC%A9%E5%9B%BE%E7%89%87/)

---

最近在写一个下载图片的爬虫，跑了一段时间，中间操作不慎删除了部分图片，于是重新下载，发现两次下载的图片大小不一样。

于是分析了一波，最后在 response headers 上发现 **cf-bgj**、**cf-polished**、**cf-cache-status** 这些字段：

```
{ date: 'Mon, 03 Dec 2018 09:06:53 GMT',
  'content-type': 'image/jpeg',
  'content-length': '775327',
  connection: 'keep-alive',
  'cache-control': 'public, max-age=31536000',
  'cf-bgj': 'imgq:85',
  'cf-polished': 'degrade=85, origSize=2376032',
  etag: '"5b0646f6-244160"',
  expires: 'Tue, 03 Dec 2019 09:06:53 GMT',
  'last-modified': 'Thu, 24 May 2018 05:00:38 GMT',
  vary: 'Accept',
  'cf-cache-status': 'HIT',
  'accept-ranges': 'bytes',
  'expect-ct': 'max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"',
  server: 'cloudflare',
  'cf-ray': '4834e13b29efa2fc-HKG' }
```

挑重点

```
'content-length': '775327', 'cf-bgj': 'imgq:85','cf-polished': 'degrade=85, origSize=2376032', cf-cache-status': 'HIT'
```

也就是说原图大小是 2376032 ，下载下来的只有 775327

查阅 Cloudflare 官方这篇文件： 

[https://support.cloudflare.com/hc/en-us/articles/360000607372-Using-Polish-to-compress-images-on-Cloudflare](https://support.cloudflare.com/hc/en-us/articles/360000607372-Using-Polish-to-compress-images-on-Cloudflare)

文章上面介绍cloudflare有两种压缩方式，一种是无损压缩：

>    Only strips metadata, e.g. EXIF data, but doesn’t change the image

仅剥离元数据，例如EXIF数据，但不更改图片。  

实质上，这种无损压缩也可能会使图片颜色失真，参考这篇文章： 

[https://pwmon.org/p/5470/cloudflare-discolors-web/](https://pwmon.org/p/5470/cloudflare-discolors-web/)

另一种是有损压缩：

>    Strips metadata and Compresses image to ~”85%”

删除元数据并压缩图片

即无论那种压缩，或多或少都会对图片造成失真。

## 方案

尝试一种方法是使用缓存控制，设置 request headers 的 **Cache-Control: no-cache, no-store, no-transform**，但是发现还是返回了 **cf-cache-status': 'HIT'**，似乎不生效。

尝试另一种更简单的方式，向URL添加随机伪参数以防止缓存命中，  

如在 URL 后添加时间戳：

> https://xxx.com/xxx.jpg?_=1543834270359

问题解决！
