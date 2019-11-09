'''
Author:Chen Wei

date: 19:26

Repetition is  the key to success!
'''


# 导入第三方的库
import requests
from lxml import etree
import os
from PIL import Image
from PyPDF2 import PdfFileReader as reader,PdfFileWriter as writer

class MHdownloader():
    '''
    属性说明:
    url：爬取的网址
    text：网页的源码
    img_urls：网页中所有漫画图片的网址
    img_datas：所有图片的数据
    '''

    def __init__(self,url):
        self.url = url     # 爬取的网页网址
        self.img_datas = []

    # 一、获取网页的数据(网页源代码)
    def get_text(self):
        # 模拟浏览器（使用浏览器的User-Agent）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        response = requests.get(self.url,headers)   # 返回的response为'Status Code'
        self.text = response.text

    # 二、获取网页图片的链接(爬取的图片)
    def html_result(self):
        '''这一部分使用xpath技术，通过元素和属性进行导航，简单来讲就是通过地址找人'''
        html = etree.HTML(self.text)    # 将网页源码转为一个HTML对象

        # '//'表示可以提取某个标签所有的信息，'/'表示可以选择某个标签,'@'表示选取属性
        # 选取所有class属性值为'main-content'的div的所有img标签的src属性的值
        self.img_urls = html.xpath('//div[@class="main-content"]//img/@src')    # 所有图片的网址

    # 三、下载网页数据(下载图片)
    def download_img(self):
        i = 1
        for url in self.img_urls:
            # 获取图片的名字
            img_name = url.split('-')[-1].split('.')[0]
            # 爬取图片，这时候返回值里面应该包含图片数据
            img_data = requests.get(url)
            # 保存图片数据
            self.img_datas.append(img_data.content)
            i += 1
            with open('./allimgs/'+str(i)+'.jpg','wb') as f:
                f.write(img_data.content)
                print("第"+str(i)+"张图片写入成功")

    # 四、将下载下来的图片全部转为PDF
    def img2pdf(self):
        '''将所有的图片全部转为PDF'''
        # 生成文件夹
        try:  # 因为文件夹可能已经存在，这时候是会报错的
            os.makedirs('./漫画')
        except:
            print('文件夹已经存在！')
        else:
            print("所爬取的内容保存在程序所在文件夹下的allimgs文件夹里!")

        # 批量生成PDF文件
        pdf_writer = writer()
        files_path  = './漫画'
        i = 1
        for img in self.img_datas:
            # 保存为PDF
            img_path = files_path+'/'+str(i)+'.pdf'
            img.save(img_path,'PDF')
            # 合并PDF
            pdf_writer.appendPagesFromReader(reader(open(img_path,'rb')))
            i+=1
        pdf_path = files_path+'/总的.pdf'
        pdf_writer.write(open(pdf_path,'wb'))
        print('漫画保存在{}路径下'.format(pdf_path))


# 启动程序
if __name__ == '__main__':
    # 目标网站
    url = r'https://www.manhuadao.cn/Comic/ComicView?comicid=58ddb0fb27a7c1392c23a3d1&chapterid=3855662'
    MHdownloader1 = MHdownloader(url)
    MHdownloader1.get_text()
    MHdownloader1.html_result()
    MHdownloader1.download_img()
    MHdownloader1.img2pdf()