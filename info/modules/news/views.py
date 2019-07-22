from info import db
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, Comment, CommentLike, Category
from utils.common import user_login_data
from utils.response_code import RET
from . import news_blu
from flask import render_template, g, jsonify, request


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):

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
    # data = {
    #
    #            'user_info': user.to_dict() if g.user else None,
    #             'click_news_list': click_news_list,
    #             'categories': categories,
    # }
    #
    # return render_template('news/detail.html', data=data)


   # 查询新闻数据
   # 校验报404错误
   # 进入详情页后要更新新闻的点击次数
   # 返回数据
    user = g.user
    try:
        news_click_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    except Exception as e:
        return "asdfasdfasdffsda"
    click_news_list = []
    for news in news_click_list if news_click_list else []:
        click_news_list.append(news.to_dict())

    news = News.query.get(news_id)

    is_collected = False
    is_followed = False
    comment_list = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
    print(comment_list)
    comments = []
    if user:
        if news in user.collection_news:
            is_collected = True
        if news.user in user.followed:
            is_followed = True
        user_comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
        user_comment_ids = [comment_like.comment_id for comment_like in user_comment_likes]
        for comment in comment_list if comment_list else []:
            comment_dict = comment.to_dict()
            comment_dict['is_like'] = False
            if comment.id in user_comment_ids:
                comment_dict['is_like'] = True
            comments.append(comment_dict)
    print("asdfasdfasfdasfd")
    # comment_list = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
    # comments = []
    # if user:
    #     user_comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
    #     user_comment_ids = [comment_like.comment_id for comment_like in user_comment_likes]
    #     for comment in comment_list if comment_list else []:
    #         comment_dict = comment.to_dict()
    #         comment_dict['is_like'] = False
    #         if comment.id in user_comment_ids:
    #             comment_dict['is_like'] = True
    #         comments.append(comment_dict)

    data = {
        'click_news_list': news_click_list,
        'user_info': user.to_dict() if user else None,
        'news': news.to_dict() if news else None,
        'is_collected': is_collected,
        'comments': comments,
        'is_followed': is_followed,
    }
    # print('*'*50)
    print(data["click_news_list"])
    print("asdfasdfsafd")
    return render_template('news/detail.html', data=data)



@news_blu.route("/news_collect", methods=['GET','POST'])
@user_login_data
def news_collect():
    """新闻收藏"""

    user = g.user
    if not user:
        return jsonify(errno = RET.SESSIONERR,errmsg = '请先登录')

    # 获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 判断参数
    if not all([news_id,action]):
        return jsonify(errno = RET.PARAMERR, errmsg = '请输入参数')

    # action在不在指定的两个值：'collect', 'cancel_collect'内
    # 查询新闻,并判断新闻是否存在
    news = News.query.get(news_id)

    # 收藏/取消收藏
    if action == "cancel_collect":
        # 取消收藏
        if news not in user.collection_news:
            user.collection_news.append(news)
        else:
            return jsonify(errno = RET.PARAMERR, errmsg = '已经收藏过了')
    else:
        # 收藏
        if news in user.collection_news:
            user.collection_news.remove(news)
        else:
            return jsonify(errno = RET.PARAMERR, errmsg = '已经取消收藏了')
    db.session.commit()

    # 返回
    return jsonify(errno = RET.OK,errmsg = 'OK')

