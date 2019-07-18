# from . import index_blu
from flask import render_template,  session

from info.models import User
from . import index_blu

# 测试
@index_blu.route('/')
def index():
    # return '<h1>index-text</h1>'
    user_id = session.get('user_id')
    print(123)




    user = User.query.filter_by(id=user_id).first()
    data = {
        "user" :user
    }


    return render_template("news/index.html",data=data)
