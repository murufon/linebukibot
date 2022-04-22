# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from cgi import print_environ
import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

from datetime import datetime, timedelta, timezone
import requests
import json
import random
import urllib

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

def getJsonFromAPI(link):
    headers = {"User-Agent": "@murufon"}
    url = "https://spla2.yuu26.com/" + link
    response = requests.get(url,headers=headers)
    json_data = json.loads(response.text)
    return json_data

def getStageInfo(link, key, showRule=True):
    json_data = getJsonFromAPI(link)
    r = json_data['result']
    time_format = '%Y-%m-%dT%H:%M:%S'
    msg = f"{key}のスケジュールはこちら！"
    # msg += "```\n"
    for i in range(3):
        start = datetime.strptime(r[i]['start'], time_format)
        end = datetime.strptime(r[i]['end'], time_format)
        msg += "\n\n"
        msg += f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}\n"
        if showRule:
            msg += f"{r[i]['rule']}\n"
        msg += f"{r[i]['maps'][0]}/{r[i]['maps'][1]}"
    # msg += "```\n"
    return msg

def getCoopInfo(link, key):
    json_data = getJsonFromAPI(link)
    r = json_data['result']
    time_format = '%Y-%m-%dT%H:%M:%S'
    msg = f"{key}のスケジュールはこちら！"
    # msg += "```\n"
    for i in range(2):
        start = datetime.strptime(r[i]['start'], time_format)
        end = datetime.strptime(r[i]['end'], time_format)
        msg += "\n\n"
        msg += f"{start.strftime('%m/%d %H:%M')} - {end.strftime('%m/%d %H:%M')}\n"
        msg += f"{r[i]['stage']['name']}\n"
        msg += f"{r[i]['weapons'][0]['name']}/{r[i]['weapons'][1]['name']}/{r[i]['weapons'][2]['name']}/{r[i]['weapons'][3]['name']}"
    # msg += "```\n"
    return msg

def getDailyRandomString():
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    now_str = str(now.strftime("%Y%m%d"))
    return now_str

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):

    if event.message.text.lower() in ['buki', 'ぶき', 'ブキ', '武器', 'weapon', 'うえぽん', 'ウエポン']:
        json_data = json.load(open('weapon.json','r'))
        buki = random.choice(json_data)
        ja_name = buki["name"]["ja_JP"]
        en_name = buki["name"]["en_US"]
        image_name = buki["name"]["ja_JP"] + ".jpg"
        profile = line_bot_api.get_profile(event.source.user_id)
        user = profile.display_name
        msg=f"{user}さんにおすすめのブキは{ja_name}({en_name})！"
        text_send_message = TextSendMessage(text=msg)

        # NOTE: URL全体をクオートするとコロンなども変換されて無効なURLになるので注意
        original_content_url = "https://linebukibot.herokuapp.com/static/twitter_images_orig/" + urllib.parse.quote(image_name)
        preview_image_url = "https://linebukibot.herokuapp.com/static/twitter_images_small/" + urllib.parse.quote(image_name)
        image_send_message = ImageSendMessage(
            original_content_url=original_content_url,
            preview_image_url=preview_image_url
        )

        line_bot_api.reply_message(
           event.reply_token,
           [text_send_message, image_send_message]
        )
        return

    if event.message.text.lower() in ['シューター', 'ブラスター', 'リールガン', 'マニューバー', 'ローラー', 'フデ', 'チャージャー', 'スロッシャー', 'スピナー', 'シェルター']:
        type_name = event.message.text.lower()
        json_data = json.load(open('weapon.json','r'))
        filtered_data = list(filter(lambda x: x["type"]["name"]["ja_JP"] == type_name, json_data))
        if filtered_data:
            buki = random.choice(filtered_data)
            ja_name = buki["name"]["ja_JP"]
            en_name = buki["name"]["en_US"]
            image_name = buki["name"]["ja_JP"] + ".jpg"
            profile = line_bot_api.get_profile(event.source.user_id)
            user = profile.display_name
            msg=f"{user}さんにおすすめの{type_name}は{ja_name}({en_name})！"
            text_send_message = TextSendMessage(text=msg)

            # NOTE: URL全体をクオートするとコロンなども変換されて無効なURLになるので注意
            original_content_url = "https://linebukibot.herokuapp.com/static/twitter_images_orig/" + urllib.parse.quote(image_name)
            preview_image_url = "https://linebukibot.herokuapp.com/static/twitter_images_small/" + urllib.parse.quote(image_name)
            image_send_message = ImageSendMessage(
                original_content_url=original_content_url,
                preview_image_url=preview_image_url
            )

            line_bot_api.reply_message(
            event.reply_token,
            [text_send_message, image_send_message]
            )
            return

    if event.message.text.lower() in ['gachi', 'ガチ', 'がち', 'gachima', 'ガチマ', 'がちま', 'ガチマッチ', 'がちまっち']:
        key = "ガチマッチ"
        link = "gachi/schedule"
        msg = getStageInfo(link, key)
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return

    if event.message.text.lower() in ['league', 'riguma', 'リグマ', 'りぐま', 'リーグマッチ', 'りーぐまっち']:
        key = "リーグマッチ"
        link = "league/schedule"
        msg = getStageInfo(link, key)
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return

    if event.message.text.lower() in ['regular', 'レギュラー', 'れぎゅらー', 'レギュラーマッチ', 'れぎゅらーまっち', 'nawabari', 'ナワバリ', 'なわばり', 'ナワバリバトル', 'なわばりばとる']:
        key = "ナワバリバトル"
        link = "regular/schedule"
        msg = getStageInfo(link, key, showRule=False)
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return

    if event.message.text.lower() in ['salmon', 'samon', 'sa-mon', 'サーモン', 'さーもん', 'サーモンラン', 'さーもんらん', 'サモラン', 'さもらん', 'coop', 'コープ', 'こーぷ', 'サケ', 'さけ', 'シャケ', 'しゃけ', '鮭']:
        key = "サーモンラン"
        link = "coop/schedule"
        msg = getCoopInfo(link, key)
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return

    if 'まそ語録' == event.message.text.lower():
        with open('maso.txt', 'r') as f:
            maso_list = f.read().split("\n")
        profile = line_bot_api.get_profile(event.source.user_id)
        user = profile.display_name
        seed = getDailyRandomString() + user
        random.seed(seed)
        maso_goroku = random.choice(maso_list)
        msg = f"今日のまそ語録: {maso_goroku}"
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return
    if 'おはよ' in event.message.text.lower():
        msg = "おはようございます！"
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return
    if 'こんにちは' in event.message.text.lower():
        msg = "こんにちは！"
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return
    if 'こんばんは' in event.message.text.lower():
        msg = "こんばんは！"
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return
    if 'おやすみ' in event.message.text.lower():
        msg = "おやすみなさい！"
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return
    # if '好き' in event.message.text.lower():
    #     msg = "僕も好き！"
    #     line_bot_api.reply_message(
    #        event.reply_token,
    #         TextSendMessage(text=msg)
    #     )
    #     return
    if event.message.text.lower() in ['たんたん', 'たんたん麺', 'たんたんめん']:
        msg = "初めましてたんたん麺ですよろしくお願いします！"
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return
    if 'りつ晩御飯' == event.message.text.lower():
        with open('ice.txt', 'r') as f:
            ice_list = f.read().split("\n")
        ice = random.choice(ice_list)
        msg = f"りつのおすすめ晩御飯: {ice}"
        line_bot_api.reply_message(
           event.reply_token,
            TextSendMessage(text=msg)
        )
        return


    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text)
    # )


# if __name__ == "__main__":
#     arg_parser = ArgumentParser(
#         usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
#     )
#     arg_parser.add_argument('-p', '--port', default=8000, help='port')
#     arg_parser.add_argument('-d', '--debug', default=False, help='debug')
#     options = arg_parser.parse_args()

#     app.run(debug=options.debug, port=options.port)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)