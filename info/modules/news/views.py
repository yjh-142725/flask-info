from info import db
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, Comment, CommentLike, Category
from utils.common import user_login_data
from utils.response_code import RET
from . import news_blu
from flask import render_template, g, jsonify, request, abort
import logging

@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):

    # 查询新闻数据
    news = News.request.get(news_id)
    # 校验报404错误
    if not news:
        abort(404)
    # 进入详情页后要更新新闻的点击次数

    # 返回数据
    pass

@news_blu.route('/<int:news_id>')
@user_login_data
def news_collect():
    pass

    """新闻收藏"""

    user = g.user
    # 获取参数
    # 判断参数
    # action在不在指定的两个值：'collect', 'cancel_collect'内
    # 查询新闻,并判断新闻是否存在

    # 收藏/取消收藏
    # if action == "cancel_collect":
    #     # 取消收藏
    #     if XXXXXX:
    # else:
    #     # 收藏
    #     if XXXXXX:

    # 返回