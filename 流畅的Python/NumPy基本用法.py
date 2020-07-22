'''
@author: LG
@software: pycharm
@application:
@file: NumPy基本用法.py
@time: 2020/7/21 0021 14:17
'''
"""
凭借着 NumPy 和 SciPy 提供的高阶数组和矩阵操作，Python 成为科学计
算应用的主流语言。NumPy 实现了多维同质数组（homogeneous array）
和矩阵，这些数据结构不但能处理数字，还能存放其他由用户定义的记
录。通过 NumPy，用户能对这些数据结构里的元素进行高效的操作。
"""
import numpy
a=numpy.arange(1,26)
# 默认为len(a)一列
# 将numpy.arange分成3行4列
a.shape=5,5
print(a)
# [[ 1  2  3  4  5]
#  [ 6  7  8  9 10]
#  [11 12 13 14 15]
#  [16 17 18 19 20]
#  [21 22 23 24 25]]

# 多维的切片
print(a[1:3,2:5])
#[[ 8  9 10]
# [13 14 15]]
# 打印一个列
print(a[:, 1])
# 将行和列进行交换
print(a.transpose())