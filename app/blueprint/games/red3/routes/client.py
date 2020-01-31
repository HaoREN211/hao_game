# -*- coding: UTF-8 -*- 
# 作者：hao.ren3
# 时间：2020/1/29 22:14
# IDE：PyCharm

from flask import current_app
from app.blueprint.games import bp
from flask_login import current_user, login_required
from flask import render_template
from utils.upload_message import FileObj
import os
import json
from flask_socketio import emit, send
from app import socketio
from config import Poker
from utils.function import is_card_number_equal, verify_group
import random


def ack(value):
    #客户端传递
    print( value)

@bp.route('/red3', methods=['GET', 'POST'])
@login_required
def red3():
    file_path = os.path.join(current_app.root_path+"/static/message", 'messages.txt')
    file = FileObj(file_path)
    before_message = file.to_list()

    # 当前在线的用户
    if len(str(before_message).strip()) < 5:
        before_message = []
        list_user_name = []
    else:
        list_user_name = [x['user']['name'] for x in before_message[0]["users"]]
        before_message = before_message[0]["users"]

    # 新进来的用户
    if not current_user.real_name in list_user_name:
        # 第五个及以上的人进入房间的时候，则提示房间满员的信息
        if (len(str(before_message).strip()) > 5) and (len(before_message)>=4):
            return render_template("game/full.html")
        before_message += [{'user': {
                    'name': current_user.real_name,
                    'ready': "F"}}]
        context = {
            'start': "F",
            'users': before_message
        }
        os.remove(file_path)
        file.write(json.dumps(context, ensure_ascii=False) + '\n')
        emit('recive_msg', context["users"], broadcast=True, callback=ack, namespace="/game/red3")
    before_message = file.to_list()
    context = {'start': "F", 'users': before_message[0]["users"]}
    return render_template("game/red3.html", **context)


# 用户准备和取消准备
@socketio.on('change_status', namespace="/game/red3")
def handle_change_status(msg):
    name = msg.get('name')
    action = msg.get("action")
    file_path = os.path.join(current_app.root_path + "/static/message", 'messages.txt')
    file = FileObj(file_path)
    messages = file.to_list()[0]

    file_score_path = os.path.join(current_app.root_path + "/static/message", 'scores.txt')
    file_score = FileObj(file_score_path)

    if not os.path.exists(file_score_path):
        index = 0
        scores = []
        for user in messages["users"]:
            scores.append({"user":{"name":user["user"]["name"], "score":0}})
        file_score.write(json.dumps(scores, ensure_ascii=False) + '\n')

    index = 0
    for user in messages["users"]:
        if user["user"]["name"] == name:
            if action == "cancel":
                messages["users"][index]["user"]["ready"] = "F"
            else:
                messages["users"][index]["user"]["ready"] = "T"
        index += 1
    os.remove(file_path)
    file.write(json.dumps(messages, ensure_ascii=False) + '\n')
    emit('recive_msg', messages["users"], broadcast=True, callback=ack, namespace="/game/red3")

    if len(messages["users"])>0:
        list_status = [x["user"]["ready"] for x in messages["users"]]

        term = 0

        # 当准备人数等于4的时候开始游戏
        if len(list(filter(lambda x: x=="T", list_status))) == 4:
            # 给每个用户发牌
            pocker = Poker()
            cards = random.sample(pocker.cards, 52)
            index = 0
            current_user_name = ""
            for user in messages["users"]:
                current_cards = cards[index*13:index*13+13]
                current_cards = sorted(current_cards, key=lambda x:x[2], reverse=False)
                messages["users"][index]["user"]["cards"] = current_cards
                current_temp_card = [x[2] for x in current_cards]
                if (49 in current_temp_card) and (50 in current_temp_card):
                    messages["users"][index]["user"]["is_business"] = "T"
                else:
                    messages["users"][index]["user"]["is_business"] = "F"
                messages["users"][index]["user"]["can_surrender"] = "T"

                # 用户编号
                messages["users"][index]["user"]["numero"] = index

                # 用户当前赢得卡片
                messages["users"][index]["user"]["collect"] = 0

                # 当前用户不出牌
                messages["users"][index]["user"]["pass"] = "F"

                # 用户走的顺序
                messages["users"][index]["user"]["order"] = -1

                # 出红3的次数
                messages["users"][index]["user"]["show_red"] = 0

                # 队伍：1-红3队伍，0非红3队伍
                current_card_numero = [x[2] for x in messages["users"][index]["user"]["cards"]]
                messages["users"][index]["user"]["group"] = verify_group(current_card_numero)

                list_card_numero = [x[2] for x in messages["users"][index]["user"]["cards"]]
                if 1 in list_card_numero:
                    term = index
                    current_user_name = user["user"]["name"]

                index += 1

            # 游戏开始的第一轮
            messages["start"] = "F"

            # 当前出牌的玩家
            messages["term"] = term
            messages["term_name"] = current_user_name

            # 新的一轮
            messages["new_term"] = "T"

            # 考虑到有“扯”和“过”的情况
            messages["temp_term"] = term

            # 当前是否是扯的情况
            messages["is_che"] = "F"
            messages["is_che_term"] = "F"

            # 当前桌面上的牌数
            messages["collect"] = 0

            # 上一轮出的牌
            messages["last_cards"] = []
            # 上一轮出牌的人
            messages["last_user"] = ""

            os.remove(file_path)
            file.write(json.dumps(messages, ensure_ascii=False) + '\n')
            emit('send_cards', messages, broadcast=True, callback=ack, namespace="/game/red3")


# 用户出牌
@socketio.on('send_card', namespace="/game/red3")
def handle_send_card(msg):
    name = msg["name"]
    numero = int(msg["numero"])
    cards = msg["cards"]

    file_path = os.path.join(current_app.root_path + "/static/message", 'messages.txt')
    file = FileObj(file_path)
    messages = file.to_list()[0]

    messages["users"][numero]["user"]["can_surrender"] = "F"
    temp_new_card = [x[2] for x in messages["users"][numero]["user"]["cards"]]
    if cards[0] in temp_new_card:
        # 将出的牌从玩家手中剔除去
        messages["users"][numero]["user"]["cards"] = list(
            filter(lambda x: x[2] not in cards, messages["users"][numero]["user"]["cards"]))

        # 每有个用户走完，判断游戏是否结束
        if len(messages["users"][numero]["user"]["cards"])==0:
            list_order = [x["user"]["order"] for x in messages["users"]]
            messages["users"][numero]["user"]["order"] = max(list_order)+1
            group_left = []
            nb_user_left = 0
            has_business = False
            group = [0, 0, 0, 0]
            index = 0
            for cu_user in messages["users"]:
                c_user = cu_user["user"]
                group[index] = cu_user["group"]
                if len(c_user["cards"]>0):
                    group_left.append(c_user["group"])
                    nb_user_left += 1
                if c_user["is_business"]=="T":
                    has_business = True
                index += 1
            group_left = list(set(group_left))
            # 如果剩下的只有一组，则比赛结束
            if len(group_left) == 1:
                file_score_path = os.path.join(current_app.root_path + "/static/message", 'scores.txt')
                file_score = FileObj(file_score_path)
                scores = file_score.to_list()[0]

                send_to =""
                group_left = group_left[0]
                # 被双关的情况
                if (nb_user_left == 2) and (not has_business):
                    index = 0
                    send_to = "被双关，"
                    if group_left == 1:
                        send_to += "黑3队胜利"
                    else:
                        send_to += "红3队胜利"
                    for cu_user in messages["users"]:
                        if group_left == cu_user["group"]:
                            scores[index]["user"]["score"] -= 2
                        else:
                            scores[index]["user"]["score"] += 2
                        index += 1
                # 业务关三家
                elif (nb_user_left == 3) and has_business:
                    index = 0
                    send_to = "业务成功，关三家"
                    for cu_user in messages["users"]:
                        if group_left == cu_user["group"]:
                            scores[index]["user"]["score"] -= 3
                        else:
                            scores[index]["user"]["score"] += 9
                        index += 1
                # 业务关两家
                elif (nb_user_left == 2) and has_business:
                    index = 0
                    send_to = "业务成功，关两家"
                    for cu_user in messages["users"]:
                        if group_left == cu_user["group"]:
                            scores[index]["user"]["score"] -= 2
                        else:
                            scores[index]["user"]["score"] += 6
                        index += 1
                # 业务关一家
                elif (nb_user_left == 1) and has_business and group_left==0:
                    index = 0
                    send_to = "业务成功，关一家"
                    for cu_user in messages["users"]:
                        if group_left == cu_user["group"]:
                            scores[index]["user"]["score"] -= 1
                        else:
                            scores[index]["user"]["score"] += 3
                        index += 1
                # 业务被关
                elif (nb_user_left == 1) and has_business and group_left == 1:
                    index = 0
                    send_to = "业务失败"
                    for cu_user in messages["users"]:
                        if group_left == cu_user["group"]:
                            scores[index]["user"]["score"] -= 9
                        else:
                            scores[index]["user"]["score"] += 3
                        index += 1
                else:
                    score_group_left = 0
                    index = 0
                    for cu_user in messages["users"]:
                        if group_left == cu_user["group"]:
                            score_group_left += cu_user["collect"]
                        index += 1
                    score_group_gone = 52 - score_group_left + 5
                    score_group_left -= 5
                    if score_group_gone > score_group_left:
                        if group_left == 0:
                            send_to = "红队"+str(score_group_gone)+"分；"+"黑队"+str(score_group_left)+"分；红队胜利"
                        else:
                            send_to = "红队" + str(score_group_left) + "分；" + "黑队" + str(score_group_gone) + "分；黑队胜利"
                        index = 0
                        for cu_user in messages["users"]:
                            if group_left == cu_user["group"]:
                                scores[index]["user"]["score"] -= 1
                            else:
                                scores[index]["user"]["score"] += 1
                            index += 1
                    elif score_group_gone < score_group_left:
                        if group_left == 0:
                            send_to = "红队"+str(score_group_gone)+"分；"+"黑队"+str(score_group_left)+"分；黑队胜利"
                        else:
                            send_to = "红队" + str(score_group_left) + "分；" + "黑队" + str(score_group_gone) + "分；红队胜利"
                        index = 0
                        for cu_user in messages["users"]:
                            if group_left == cu_user["group"]:
                                scores[index]["user"]["score"] += 1
                            else:
                                scores[index]["user"]["score"] -= 1
                            index += 1
                    os.remove(file_score_path)
                    os.remove(file_path)
                    file_score.write(json.dumps(scores, ensure_ascii=False) + '\n')
                    index = 0
                    for cu_user in messages["users"]:
                        messages["users"][index]["user"]["ready"] = "F"
                        index += 1
                    file.write(json.dumps(messages, ensure_ascii=False) + '\n')
                    emit('finish', {"result": send_to, "scores":scores}, broadcast=True, callback=ack, namespace="/game/red3")

        # 游戏已经开始
        messages["start"] = "T"
        # 上一轮出牌的人和出的牌
        messages["last_user"] = name
        messages["last_cards"] = cards

        messages["collect"] += len(cards)

        nb_user = len(messages["users"])

        # 当前是有有用户有两及以上的卡
        has_nb_plus_2 = False
        if (messages["new_term"] == "T") and (len(cards) == 1):
            for i in range(nb_user):
                curr_user = messages["users"][i]["user"]
                nb_card_equal = sum(list(map(lambda x: is_card_number_equal(cards[0], x[2]), curr_user["cards"])))
                if nb_card_equal >= 2:
                    has_nb_plus_2 = True

        # 如果是新一轮的出牌，则考虑到“扯”的情况。“扯”只有在只有一张牌的情况下
        if (messages["new_term"] == "T") and (len(cards) == 1) and has_nb_plus_2:
            for i in range(nb_user):
                curr_user = messages["users"][i]["user"]
                nb_card_equal = sum(list(map(lambda x: is_card_number_equal(cards[0], x[2]), curr_user["cards"])))
                if nb_card_equal >= 2:
                    messages["term"] = i
                    messages["term_name"] = curr_user["name"]
                    messages["is_che"] = "T"
                    messages["is_che_term"] = "T"
        else:
            messages["is_che"] = "F"
            messages["term"] = int((numero+1)%4)
            messages["term_name"] = messages["users"][messages["term"]]["user"]["name"]
        messages["new_term"] = "F"
        messages["temp_term"] = numero

        temp = [str(x) for x in cards]
        print(",".join(temp))
        if 49 in cards:
            messages["users"][numero]["user"]["show_red"] += 1
        if 50 in cards:
            messages["users"][numero]["user"]["show_red"] += 1

        # 只要有用户出牌，“过”的标记就全部取消
        for i in range(nb_user):
            messages["users"][i]["user"]["pass"] = "F"
        os.remove(file_path)
        file.write(json.dumps(messages, ensure_ascii=False) + '\n')
        emit('send_cards', messages, broadcast=True, callback=ack, namespace="/game/red3")


# 用户跳过出牌
@socketio.on('pass', namespace="/game/red3")
def handle_pass(msg):
    name = msg["name"]
    numero = int(msg["numero"])

    file_path = os.path.join(current_app.root_path + "/static/message", 'messages.txt')
    file = FileObj(file_path)
    messages = file.to_list()[0]

    messages["users"][numero]["user"]["can_surrender"] = "F"
    # 如果是扯的情况
    if messages["is_che"] == "T":
        messages["is_che"] = "F"
        messages["is_che_term"] = "F"
        messages["term"] = int((int(messages["temp_term"])+1)%4)
    else:
        messages["term"] = int((int(messages["term"]) + 1) % 4)
        messages["users"][numero]["user"]["pass"] = "T"

    # 如果下一个玩家的牌走完了，则再下一个玩家出牌
    while len(messages["users"][messages["term"]]["user"]["cards"])==0:
        messages["term"] = int((int(messages["term"]) + 1) % 4)
    messages["term_name"] = messages["users"][int(messages["term"])]["user"]["name"]
    messages["new_term"] = "F"

    # 统计走的人加上pass的人
    nb_pass_gone = 0
    nb_user = len(messages["users"])
    for i in range(nb_user):
        curr_user = messages["users"][i]["user"]
        if len(curr_user["cards"]) == 0:
            nb_pass_gone += 1
        elif curr_user["pass"] == "T":
            nb_pass_gone += 1

    # 如果走的人加上pass的人等于3，则新的一轮开始
    if (nb_pass_gone == 3) and (messages["term"] == messages["temp_term"]):
        messages["new_term"] = "T"
        messages["users"][messages["term"]]["user"]["collect"] += messages["collect"]
        messages["collect"] = 0
        messages["is_che"] = "F"
        messages["is_che_term"] = "F"
        for i in range(nb_user):
            messages["users"][i]["user"]["pass"] = "F"
        while len(messages["users"][messages['term']]["user"]["cards"])==0:
            messages['term'] = (messages['term']+1)%4

    os.remove(file_path)
    file.write(json.dumps(messages, ensure_ascii=False) + '\n')
    emit('send_cards', messages, broadcast=True, callback=ack, namespace="/game/red3")

# 用户认输
@socketio.on('surrender', namespace="/game/red3")
def handle_surrender(msg):
    name = msg["name"]
    numero = int(msg["numero"])

    file_path = os.path.join(current_app.root_path + "/static/message", 'messages.txt')
    file = FileObj(file_path)
    messages = file.to_list()[0]

    file_score_path = os.path.join(current_app.root_path + "/static/message", 'scores.txt')
    file_score = FileObj(file_score_path)
    scores = file_score.to_list()[0]

    send_to = name + "认输"
    index = 0
    for score in scores:
        if score['user']["name"] == name:
            scores[index]['user']["score"] -= 6
        else:
            scores[index]['user']["score"] += 2
        index += 1
    os.remove(file_score_path)
    os.remove(file_path)
    file_score.write(json.dumps(scores, ensure_ascii=False) + '\n')
    index = 0
    for cu_user in messages["users"]:
        messages["users"][index]["user"]["ready"] = "F"
        index += 1
    file.write(json.dumps(messages, ensure_ascii=False) + '\n')
    emit('finish', {"result": send_to, "scores":scores}, broadcast=True, callback=ack, namespace="/game/red3")