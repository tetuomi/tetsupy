from main import (app, db, request, abort,line_bot_api, handler, owner_id)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, VideoSendMessage, FollowEvent, ImageMessage)
import os
from main.models.user import User
#import cv2
from pathlib import Path

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

# MessageEvent
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.type == "message" and event.message.type == "text":
        if event.message.text == "show":
            messages = []
            contents = db.session.query(User).filter_by(user_id=event.source.user_id).all()

            for content in contents:
                messages.append(TextSendMessage(content.content))

            line_bot_api.reply_message(event.reply_token, messages[-5:])

        elif event.message.text == "画像":
            main_image_path = "static/images/hina.jpg"
            preview_image_path = "static/images/hina.jpg"

            image_message = ImageSendMessage(
                original_content_url=f"https://tetsupy.herokuapp.com/{main_image_path}",
                preview_image_url=f"https://tetsupy.herokuapp.com/{preview_image_path}",
            )

            line_bot_api.reply_message(event.reply_token, image_message)

        elif event.message.text == "動画":
            main_video_path = "static/videos/hina.MP4"
            preview_video_path = "static/videos/hina.MP4"

            video_message = VideoSendMessage(
                original_content_url=f"https://tetsupy.herokuapp.com/{main_video_path}",
                preview_image_url=f"https://tetsupy.herokuapp.com/{preview_video_path}",
            )
            line_bot_api.reply_message(event.reply_token, video_message)
            
        else:
            #データベースに追加
            user = User(event.source.user_id, event.message.text)
            db.session.add(user)
            db.session.commit()
        
            line_bot_api.reply_message(event.reply_token,TextSendMessage("記憶しました"))


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    file_path = f"main/static/images/{event.message.id}.jpg"
    with open(Path(file_path).absolute(), 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    main_image_path = f"static/images/{event.message.id}.jpg"
    preview_video_path = f"static/images/{event.message.id}.jpg"

    image_message = ImageSendMessage(
        original_content_url=f"https://tetsupy.herokuapp.com/{main_image_path}",
        preview_image_url=f"https://tetsupy.herokuapp.com/{preview_image_path}",
    )

    line_bot_api.reply_message(event.reply_token, image_message)


@handler.add(FollowEvent)
def handle_follow(event):
    if event.type == "follow":
        profile = line_bot_api.get_profile(event.source.user_id)
        line_bot_api.push_message(
            owner_id,
            TextSendMessage(text='「' + profile.display_name + '」さんが追加しました')
        )
