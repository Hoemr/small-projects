# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Created on Fri Oct 25 21:16:30 2019

@author: cw817615
"""

# -*-coding:utf-8-*-

## 实现图片的放缩
from PIL import Image
from PyPDF2 import PdfFileReader as reader,PdfFileWriter as writer
import os

class Graphics:
    '''封装的图片截取类'''
    infile = ""  # 输入路径
    outfile = ""   # 输出路径
    
    def __init__(self):
        self.outpath_resize = ""   # 放缩图片保存路径
        self.crop_imgs = []   # 裁剪后的图片列表
        self.slices = 0    # 总共切成了slices片
        #self.outpath_pdf = ""    # 裁剪后合成的PDF保存的路径
    
    def get_path(self):
        self.infile = input("请输入文件获取路径：")
        self.outfile = input("请输入文件保存路径：")
        
    def resizeimg(self):
        '''图片放缩函数'''
        # 打开图片
        img = Image.open(self.infile)
        # 获取图片尺寸,元组第一个元素为宽度
        img_size = img.size
        # 图片放缩[A4大小为210*297mm，2480*3508px，分辨率300dpi]
        if img_size[0] >2244:
            print("图片宽度已经超过了A4要求，继续缩放可能会影响画质，是否继续？")
            flag = '0'
            while True:
                if flag == 'y' or flag == 'n':
                    break
                else:
                    flag = input("输入错误，请输入y/n(小写)")
            if flag == 'n':
                return
        # 上下左右各留1cm，变为190*277mm,2244*3271px
        width = 2244   # 左右各留1cm
        length = img_size[1]*width//img_size[0]
        out=img.resize((width, length),Image.ANTIALIAS)
        print("图片缩放成功，左右已各留1cm")
        print("图片宽度和高度分别是{}(单位:像素)".format(out.size))
        self.outpath_resize = self.outfile+r"\img_resized.jpg"
        out.save(self.outpath_resize)
        
    
    def cropimg(self):
        '''按照图片长宽分割图片'''
        # 打开放缩后的图片
        img = Image.open(self.outpath_resize)
        img_size = img.size
        '''
        裁剪：传入一个元组作为参数
        元组里的元素分别是：
        距离图片左边界距离x， 距离图片上边界距离y，
        距离图片左边界距离+裁剪框宽度x+w，距离图片上边界距离+裁剪框高度y+h
        x,y是裁剪框左上角的坐标， x+w,y+h是右下角的坐标
        '''
        # 初始化参数，在之后只需要改变y值即可
        x,y = 0,0
        w,h = 2244,3271
        
        # 确定分成多少片
        if img_size[1] % h == 0:
            self.slices = img_size[1]//h
        else:
            self.slices = img_size[1]//h+1
            
        # 循环截取图片
        for i in range(self.slices):
            y = i*h
            # 截取第i张图片
            img_copy = img.copy()
            self.crop_imgs.append(img_copy.crop((x,y,x+w,y+h)))  

    
    def img2pdf(self):
        '''将文件批量转为PDF'''
        out_pdf = writer()
        
         # 创建文件夹
        try:
            os.makedirs(self.outfile+r"\PDF_files")
        except Exception as e:
            print("创建文件夹出错，错误为----->",e)
        
        # 逐一转为PDF
        path = self.outfile+r"\PDF_files"
        i = 0
        for img in self.crop_imgs:
            outpath_pdf = path+r"\img_pdf"+str(i+1)+".pdf"
            #outpath_pdf = self.outfile+r"\img_pdf"+str(i+1)+".pdf"
            img.save(outpath_pdf,'PDF')
            out_pdf.appendPagesFromReader(reader(open(outpath_pdf,'rb')))
            i += 1
        out_pdf.write(open(path+r"\totalpdf.pdf",'wb'))
        print("PDF文件保存在{}文件夹里".format(path))
        
  
class PDFHandleMode(object):
    '''
    处理PDF文件的模式
    '''
    # 保留源PDF文件的所有内容和信息，在此基础上修改
    COPY = 'copy'
    # 仅保留源PDF文件的页面内容，在此基础上修改
    NEWLY = 'newly'
    

class MyPDFHandler(object):
    '''
    封装的PDF文件处理类
    '''
    def __init__(self,pdf_file_path,slices=0,mode = PDFHandleMode.COPY):
        '''
        用一个PDF文件初始化
        :param pdf_file_path: PDF文件路径
        :param mode: 处理PDF文件的模式，默认为PDFHandleMode.COPY模式
        '''
        self.slices = slices
        # 只读的PDF对象
        self.__pdf = reader(pdf_file_path)

        # 获取PDF文件名（不带路径）
        self.file_name = os.path.basename(pdf_file_path)
        #
        self.metadata = self.__pdf.getXmpMetadata()
        #
        self.doc_info = self.__pdf.getDocumentInfo()
        #
        self.pages_num = self.__pdf.getNumPages()

        # 可写的PDF对象，根据不同的模式进行初始化
        self.__writeable_pdf = writer()
        if mode == PDFHandleMode.COPY:
            self.__writeable_pdf.cloneDocumentFromReader(self.__pdf)
        elif mode == PDFHandleMode.NEWLY:
            for idx in range(self.pages_num):
                page = self.__pdf.getPage(idx)
                self.__writeable_pdf.insertPage(page, idx)

    def save2file(self,new_file_name='./'):
        '''
        将修改后的PDF保存成文件
        :param new_file_name: 新文件名，不要和原文件名相同
        :return: None
        '''
        # 保存修改后的PDF文件内容到文件中
        with open(new_file_name, 'wb') as fout:
            self.__writeable_pdf.write(fout)

    def add_one_bookmark(self,title,page,parent = None, color = None,fit = '/Fit'):
        '''
        往PDF文件中添加单条书签，并且保存为一个新的PDF文件
        :param str title: 书签标题
        :param int page: 书签跳转到的页码，表示的是PDF中的绝对页码，值为1表示第一页
        :paran parent: A reference to a parent bookmark to create nested bookmarks.
        :param tuple color: Color of the bookmark as a red, green, blue tuple from 0.0 to 1.0
        :param list bookmarks: 是一个'(书签标题，页码)'二元组列表，举例：[(u'tag1',1),(u'tag2',5)]，页码为1代表第一页
        :param str fit: 跳转到书签页后的缩放方式
        :return: None
        '''
        # 为了防止乱码，这里对title进行utf-8编码
        self.__writeable_pdf.addBookmark(title,page - 1,parent = parent,color = color,fit = fit)
        print('添加页码成功: {0}'.format(title))

    def add_bookmarks(self):
        '''
        批量添加书签
        :param bookmarks: 书签元组列表，其中的页码表示的是PDF中的绝对页码，值为1表示第一页
        :return: None
        '''
        # 生成书签(页码)
        bookmarks = [(str(i),i) for i in range(1,self.slices+1)]
        
        for title,page in bookmarks:
            self.add_one_bookmark(title,page,color = (0.0,0.0,0.0))
        print("添加页码成功")


        
if __name__ == "__main__":
    #
    #inputpath = r"C:\Users\cw817615\Desktop\img2.jpg"
    #outpath = r"C:\Users\cw817615\Desktop"
    graphics = Graphics()
    graphics.get_path()
    #graphics.infile = inputpath
    #graphics.outfile = outpath
    graphics.resizeimg()
    graphics.cropimg()
    graphics.img2pdf()
    #pdf_handle = MyPDFHandler(pdf_path,graphics.slices,PDFHandleMode.COPY)
    #pdf_handle.add_bookmarks()
    #pdf_handle.save2file(pdf_path.replace('totalpdf','totalpdf2'))
    
    