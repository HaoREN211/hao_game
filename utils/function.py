# -*- coding: UTF-8 -*- 
# 作者：hao.ren3
# 时间：2020/1/31 13:53
# IDE：PyCharm

# 判断card1和card2的牌指数是否相等
def is_card_number_equal(card1, card2):
    divisor_1 = int((int(card1)-1)/4)
    divisor_2 = int((int(card2)-1)/4)
    if divisor_1 == divisor_2:
        return 1
    return 0

# 根据是否有红3分队
def verify_group(cards):
    if 49 in cards:
        return 1
    if 50 in cards:
        return 1
    return 0