'''
@author: LG
@software: pycharm
@application:
@file: bisect用法.py
@time: 2020/7/21 0021 13:31
'''
import random

"""
bisect(haystack, needle) 在 haystack（干草垛）里搜索
needle（针）的位置，该位置满足的条件是，把 needle 插入这个位置
之后，haystack 还能保持升序。也就是在说这个函数返回的位置前面
的值，都小于或等于 needle 的值。其中 haystack 必须是一个有序的
序列。你可以先用 bisect(haystack, needle) 查找位置 index，再
用 haystack.insert(index, needle) 来插入新值。但你也可用
insort 来一步到位，并且后者的速度更快一些
"""
import bisect
import sys
HAYSTACK=[1,4,5,6,8,12,15,20,21,23,23,26,29,30]
NEEDLES=[0,1,2,5,8,10,22,23,29,30,31]
ROW_FMT='{0:2d} @ {1:2d}   {2}{0:<2d}'

def demo(bisect_fn):
    for needle in reversed(NEEDLES):
        position=bisect_fn(HAYSTACK,needle) #用特定的 bisect 函数来计算元素应该出现的位置。
        offset=position*'   |'
        print(ROW_FMT.format(needle,position,offset))
def demo2():
    Size=7
    random.seed(1779)
    my_lst=[]
    for i in range(Size):
        new_item=random.randrange(Size*2)
        bisect.insort(my_lst,new_item)
        print('%2d ->' %new_item,my_lst)
if __name__ == '__main__':
    if sys.argv[-1]=='left': #根据命令上最后一个参数来选用 bisect 函数
        bisect_fn=bisect.bisect_left
    else:
        bisect_fn=bisect.bisect
    # print('DEMO:',bisect_fn.__name__)
    # print('haystack ->',' '.join('%2d'%n for n in HAYSTACK))
    # demo(bisect_fn)
    #DEMO: bisect_right
    # haystack ->  1  4  5  6  8 12 15 20 21 23 23 26 29 30
    # 31 @ 14      |   |   |   |   |   |   |   |   |   |   |   |   |   |31
    # 30 @ 14      |   |   |   |   |   |   |   |   |   |   |   |   |   |30
    # 29 @ 13      |   |   |   |   |   |   |   |   |   |   |   |   |29
    # 23 @ 11      |   |   |   |   |   |   |   |   |   |   |23
    # 22 @  9      |   |   |   |   |   |   |   |   |22
    # 10 @  5      |   |   |   |   |10
    #  8 @  5      |   |   |   |   |8
    #  5 @  3      |   |   |5
    #  2 @  1      |2
    #  1 @  1      |1
    #  0 @  0   0

    demo2()
    #8 -> [8]
    # 4 -> [4, 8]
    # 12 -> [4, 8, 12]
    #  0 -> [0, 4, 8, 12]
    # 10 -> [0, 4, 8, 10, 12]
    #  9 -> [0, 4, 8, 9, 10, 12]
    # 13 -> [0, 4, 8, 9, 10, 12, 13]