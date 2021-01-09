# MD原文档路径
MD_PATH = 'E:\\Blog\\Local_MD\\'

# 图片压缩率
COMPRESS_RATE = 0.6

# 设定小于多少b的图片不进行压缩[1024b = 1k]
IMG_SIZE = 512000

# 压缩图片保存路径
COMPRESS_IMG_SAVE_PATH = 'E:\\Blog\\Local_MD\\_resources\\compression\\'

# 图片上传后的图片链接地址
Upload_Img_Url = 'https://picture-bed-1259591647.cos.ap-chengdu.myqcloud.com/'

# 转换后的MD文档保存位置
RESULT_MD_PATH = 'E:\\Blog\\Result_MD\\'

# 压缩图片是否删除
CompressPicture_Delete = False

# 源MD文档是否删除
MD_Delete = False

# 平台[Android, Windows]，因为路径格式不一致
Platform = 'Windows'

# 是否添加Hexo信息头部
Add_Hexo = True

# Hexo头部信息
Hexo_Title = '''
---

title: {}
author: 清酒
top: false
cover: false
toc: true
mathjax: false
date: {}
img: 
coverImg:
password:
tags:
  - 
categories:
  - 
summary:

---
'''

# 图片信息提取正则
Re_Image_Path = r'/.*\.?jpg|/.*\.?png|/.*\.?jpeg|/.*\.?gif|/.*\.?PNG|/.*\.?JPG'

# 腾讯云oss配置
Secret_Id = ''
Secret_Key = ''
Region = ''