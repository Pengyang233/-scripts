# -*- coding: UTF-8 -*-
import os
import shutil
import time
import datetime
import re
import filecmp

NOTE_ROOT = 'Notes' #笔记文件夹
SRC_ROOT = 'wiki-source' # 博客的源文件

def mkdir_if_missing(path):
    if not os.path.exists(path):
        os.makedirs(path)

def add_head_and_copy(note_path, wiki_path):
    # ---
    # title: 常用命令
    # toc: true
    # date: 2020-07-24 21:00:14
    # tags: ubuntu
    # categories: ubuntu
    # ---
    if not os.path.splitext(note_path)[-1] == '.md':
        raise Exception('File: {} is not .md file'.format(path))
    else:
        # 判定分类情况，若直接在 Notes目录下，则认为是待分类
        # 注意不同系统下的地址分隔符，默认Notes下第一个子文件夹为分类
        if os.path.splitext(note_path.split('\\')[1])[-1]=='.md':
            cate = ['待分类']
        else:
            cate = note_path.split('\\')[1]
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        # 替换图片的路径
        note_name = os.path.splitext(note_path.split('\\')[-1])[0]
        for (ind,x) in enumerate(content):
            if '_asset/' in x:
                content[ind] = x.replace('_asset/{}/'.format(note_name),'')

        with open(wiki_path, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write('title: {}\n'.format(os.path.split(note_path)[-1].split('.')[0]))
            f.write('toc: true\n')
            f.write('data: {}\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) ))
            f.write('tags: \n')
            f.write('categories: {}\n'.format(cate)) 
            f.write('---\n')
            f.write('\n')
            f.writelines(content)

def move_img(note_path, wiki_path):
    note_name = os.path.split(note_path)[-1].split('.')[0]
    img_folder = os.path.join(os.path.split(note_path)[0], '_asset',note_name)
    if os.path.exists(img_folder):
        dst_img_folder = os.path.join(os.path.split(wiki_path)[0], note_name)
        mkdir_if_missing(dst_img_folder)
        for i in os.listdir(img_folder):
            shutil.copy(os.path.join(img_folder, i), os.path.join(dst_img_folder, i))

def same_check(note_path):
    # 若笔记文件七天内有修改，则认为笔记和wiki上的备份是不同的
    last_modify_time = datetime.datetime.fromtimestamp(os.path.getmtime(note_path))
    now = now=datetime.datetime.now()
    diff = (now-last_modify_time).days
    return (diff > 7)

def main():
    for root,folder,files in os.walk(NOTE_ROOT):
        for f in files:
            if os.path.splitext(f)[-1]=='.md':
                note_path = os.path.join(root, f)
                wiki_path = os.path.join(SRC_ROOT, 'source', note_path.replace(NOTE_ROOT,'_posts'))
                if same_check(note_path): #判断文件内容是否相同
                    continue
                else:
                    mkdir_if_missing(os.path.split(wiki_path)[0])
                    add_head_and_copy(note_path, wiki_path)
                    move_img(note_path, wiki_path)
                    # 输出信息
                    # note_name = os.path.splitext(note_path.split('\\')[-1])[0]
                    # print('Update note: {}'.format(note_name))
    # print('== Done ==')
    os.chdir(SRC_ROOT)
    os.system("git add .")
    os.system("git commit -m 'update'")
    os.system("git push")

if __name__ == '__main__':
    main()



