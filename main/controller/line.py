from main import (app, db, request, abort,line_bot_api, handler, owner_id)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, FollowEvent)
import os
from main.models.user import User

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
            
        else:
            #データベースに追加
            user = User(event.source.user_id, event.message.text)
            db.session.add(user)
            db.session.commit()
        
            line_bot_api.reply_message(event.reply_token,TextSendMessage("記憶しました"))

@handler.add(FollowEvent)
def handle_follow(event):
    if event.type == "follow":
        profile = line_bot_api.get_profile(event.source.user_id)
        line_bot_api.push_message(
            owner_id,
            TextSendMessage(text='「' + profile.display_name + '」さんが追加しました')
        )
