# from . import index_blu
from flask import render_template, session, current_app, g

from info.constants import CLICK_RANK_MAX_NEWS
from info.models import User, Category, News
from . import index_blu

# 测试
@index_blu.route('/')
def index():
    # return '<h1>index-text</h1>'
    user_id = session.get('user_id')
    print(user_id)
    print("+++++++++++++++")
    user = User()
    if user_id:
        try:
            uer = user.query.get(user_id)
            print(uer)
        except BaseException as e:
            current_app.logger.error(e)

    user = User.query.filter_by(id=user_id).first()
    # data = {
    #     "user" :user
    # }
    data = {
        "user":user.to_dict() if user else None,
    }

    return render_template("news/index.html",data = data)

    # user = g.user
    #
    # news_click_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    # click_news_list = []
    # for news in news_click_list if news_click_list else []:
    #     click_news_list.append(news.to_dict())
    #
    # category_lsit = Category.query.all()
    # categories = []
    # for category in category_lsit if category_lsit else []:
    #     categories.append(category.to_dict())
    #
    # data = {
    #     'user_info': user.to_dict() if user else None,
    #     'click_news_list': click_news_list,
    #     'categories': categories,
    # }
    # return render_template('news/index.html', data=data)


