'''
@author: LG
@software: pycharm
@application:
@file: 一索扑克牌.py
@time: 2020/7/21 0021 10:28
'''
import collections
Card=collections.namedtuple('Card',['rank','suit'])

# 让类对象变成可迭代对象
class FrenchDeck:
    ranks=[str(n) for  n in range(2,11)]+list("JQKA")
    suits="spades diamonds clubs hearts".split()

    def __init__(self):
        self.card=[Card(rank,suit) for suit in self.suits for rank in self.ranks]

    def __len__(self):
        return len(self.card)
    # 实现可迭代
    def __getitem__(self, item):
        return self.card[item]
frenchDeck=FrenchDeck()
# 牌的长度
print(len(frenchDeck))
# for index in range(len(frenchDeck)):
#     print(frenchDeck[index])
print(frenchDeck[12::13])