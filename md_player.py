from time import strftime, localtime, time
from os import path, walk, mkdir, rename, remove
from re import findall

import cv2
import pypinyin
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

import config
import transform_md


class MDPlayer:

    def __init__(self):
        if config.Platform == 'Windows':
            self.split_str = '\\'
        else:
            self.split_str = '/'
        self.md_content = str()

    @staticmethod
    def mkdir_config_folder():
        if not path.exists(config.COMPRESS_IMG_SAVE_PATH):
            mkdir(config.COMPRESS_IMG_SAVE_PATH)
            print('|-- 配置文件中设置的压缩图片保存路径不存在！\n|-- 已创建压缩图片保存文件夹')
        if not path.exists(config.RESULT_MD_PATH):
            mkdir(config.RESULT_MD_PATH)
            print('|-- 配置文件中设置的md转换保存路径不存在！\n|-- 已创建md保存文件夹')

    def read_md(self, md_path):
        with open(md_path, 'r', encoding='UTF-8') as f:
            self.md_content = f.read()
        # 如果设置不保留源文件，那么读取后直接删除
        if config.MD_Delete:
            remove(md_path)

    # 获取目录下所有的md文档
    @staticmethod
    def get_md():
        md_list = [path.join(root, file) for root, dirs, files in walk(config.MD_PATH, topdown=True)
                   for file in files if file.endswith('.md')]
        return md_list

    # 判断是否全部转换
    def transform_all(self):
        md_list = self.get_md()
        transform = input('是否需要全部转换路径下的所有文档[Yes/No]：').lower()
        if transform == "yes":
            print('|-- 已经将全部任务添加到待处理列表中！\n')
            return md_list
        elif transform == 'no':
            # 开始循环遍历所有的md文档，与配置文件中的Transform_MD字典进行对比
            pending_md_list = []
            for md in md_list:
                md_name = md.split(self.split_str)[-1]
                if md_name not in transform_md.Transform_MD:
                    # 加入待处理
                    pending_md_list.append(md)
            return pending_md_list

    # 解析MD获取到图片路径
    def get_md_img_path(self):
        img_list = []
        img_str_list = findall(config.Re_Image_Path, self.md_content)
        for img_path in img_str_list:
            img_list.append(path.join(config.MD_PATH, self.split_str.join(img_path.split('/')[1:])))
        # 返回的时图片的绝对路径
        return img_list, img_str_list

    # 压缩图片，判断图片是否可以压缩，可以压缩的返回压缩后的图片绝对路径，如果不可以压缩，直接返回路路径
    def compress_image(self, img_path):
        # 判断文件夹下是否有文件
        if not path.exists(img_path):
            return None
        img_name = img_path.split(self.split_str)[-1]
        if img_name.lower().endswith(('.png', '.jpg')) and path.getsize(img_path) >= config.IMG_SIZE:
            # 中文文件名转化成拼音
            if findall(u'[\u4e00-\u9fa5]+', img_name):
                img_pinyin_name = pypinyin.lazy_pinyin(img_name, style=pypinyin.STYLE_NORMAL)
                img_pinyin_path = path.join(self.split_str.join(img_path.split(self.split_str)[:-1]),
                                            ''.join(img_pinyin_name))
                # 修改源文件名称
                try:
                    rename(img_path, img_pinyin_path)
                except OSError as e:
                    print(e)

                img = cv2.imread(img_pinyin_path)
            else:
                img = cv2.imread(img_path)

            width, height = img.shape[:2]
            # 双三次插值
            img_resize = cv2.resize(img, (int(height * config.COMPRESS_RATE), int(width * config.COMPRESS_RATE)),
                                    interpolation=cv2.INTER_AREA)

            save_img_path = '%s/%s' % (config.COMPRESS_IMG_SAVE_PATH, img_name)
            cv2.imwrite(save_img_path, img_resize)

            # 压缩后返回压缩的路径
            return save_img_path
        else:
            # 直接返回路径
            return img_path

    # 上传图片，返回链接
    def upload_img(self, img_path):
        secret_id = config.Secret_Id
        secret_key = config.Secret_Key
        region = config.Region
        client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key))
        with open(img_path, 'rb') as fp:
            client.put_object(
                Bucket='picture-bed-1259591647',
                Body=fp,
                Key="Hexo_Images/" + strftime('%Y-%m-%d', localtime(time())) + "/" + img_path.split(self.split_str)[-1],
                StorageClass='STANDARD',
                EnableMD5=False
            )

        #  将上传文件的链接添加到列表中， 方便后续查找替换
        img_url = 'https://picture-bed-1259591647.cos.ap-chengdu.myqcloud.com/' + "Hexo_Images/" + \
                  strftime('%Y-%m-%d', localtime(time())) + "/" + img_path.split(self.split_str)[-1]
        # 返回上传后的图片地址
        return img_url

    # 替换本地图片路径
    def replace_img_url(self, url, upload_url):
        self.md_content.replace(url, upload_url)

    # 写出文件
    def write_md_to_folder(self, md):
        with open(config.RESULT_MD_PATH + md.split(self.split_str)[-1], 'w', encoding='UTF-8') as f:
            f.write(self.md_content)

    def add_hexo_title(self, md_name):
        title = config.Hexo_Title.format(md_name, strftime('%Y-%m-%d %H:%M:%S', localtime(time())))
        if config.Add_Hexo:
            self.md_content = title + self.md_content

    def main(self):
        self.mkdir_config_folder()
        md_list = self.transform_all()
        print('|-- 共获取到%s个需要处理的md文档\n' % len(md_list))

        for md in md_list:
            self.read_md(md)
            md_name = md.split(self.split_str)[-1]
            md_img_list, img_path_list = self.get_md_img_path()
            print('|-- [%s] 文档一共有 [%s] 张图片待处理' % (md_name, len(md_img_list)))
            for x, img in enumerate(md_img_list):
                # 压缩图片
                img_path = self.compress_image(img)
                if img_path is None:
                    print('|-- 不存在图片文件，请检查文件是否存在')
                    break
                # 上传图片,路径
                upload_img_url = self.upload_img(img_path)
                # 替换本地图片链接
                self.md_content = self.md_content.replace('..%s' % img_path_list[x], upload_img_url)

            # 是否添加hexo信息头
            self.add_hexo_title(md_name)
            # 写入到指定的位置
            self.write_md_to_folder(md)
            
            # 添加记录到config文件中
            transform_md.Transform_MD[md_name] = strftime('%Y-%m-%d', localtime(time()))
            tr_md = transform_md.Transform_MD

        # 删除压缩图片文件夹
        if config.CompressPicture_Delete:
            print('\n|-- 已经删除压缩文件存放目录')
            remove(config.COMPRESS_IMG_SAVE_PATH)

        if len(md_list) >= 1:
            with open('transform_md.py', 'w', encoding="UTF_8") as f:
                f.write('Transform_MD = ' + str(tr_md))


if __name__ == '__main__':
    md_player = MDPlayer()
    md_player.main()
