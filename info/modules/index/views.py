# from . import index_blu
from flask import render_template, session, current_app

from info.models import User
from . import index_blu

# 测试
@index_blu.route('/')
def index():
    # return '<h1>index-text</h1>'
    user_id = session.get('user_id')
    print(123)
    user = None
    if user_id:
        try:
            uer = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)

    # user = User.query.filter_by(id=user_id).first()
    # data = {
        # "user" :user
    # }
    data = {
        "user":user.to_dict() if user else None,
    }

    return render_template("news/index.html",data=data)
