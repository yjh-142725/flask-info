# from . import index_blu
import logging

from flask import render_template, session, current_app, g, jsonify, request

from info import constants
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import User, Category, News
from utils.common import user_login_data
from utils.response_code import RET
from . import index_blu

# 测试
@index_blu.route('/')
@user_login_data
def index():
    #demo
    # return '<h1>index-text</h1>'

    #demo
    # user_id = session.get('user_id')
    # user = User()
    # if user_id:
    #     try:
    #         uer = user.query.get(user_id)
    #         print(uer)
    #     except BaseException as e:
    #         current_app.logger.error(e)
    #
    # user = User.query.filter_by(id=user_id).first()
    # data = {
    #     "user":user.to_dict() if user else None,
    # }
    #
    # return render_template("news/index.html",data = data)

    # demo
    # # 获取当前的登录用户的ID
    # user_id = session.get('user_id')
    # user = None
    # try:
    #     user = User.query.filter_by(id = user_id).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #
    # # 右侧新闻排行
    # clicks_news = []
    # try:
    #     clicks_news = News.query.order_by(News.clicks.desc()).limit(10).all()
    # except Exception as e:
    #     current_app.logger.error(e)
    #
    # # 按照点击量排序查询出点击最高的前10条新闻
    # clicks_news_li = []
    # for new_abj in clicks_news:
    #     clicks_news_dict = new_abj.to_basic_dict()
    #     clicks_news_li.append(clicks_news_dict)
    # # 获取新闻分类
    # category_all = Category.query.all()
    # # 定义列表保存分类数据
    # categories = []
    # for category_abj in category_all:
    #     category_dict = category_abj.to_dict()
    #     categories.append(category_dict)
    # # 拼接内容
    #     data = {
    #         "user": user,
    #         "news_dict": clicks_news_li,
    #         "categories": categories,
    #
    #     }
    # return render_template("news/index.html",data = data)

    # demo
    user = g.user

    news_click_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    click_news_list = []
    for news in news_click_list if news_click_list else []:
        click_news_list.append(news.to_dict())

    # print(click_news_list)

    category_list = Category.query.all()
    # print(category_list)
    categories = []
    for category in category_list if category_list else []:
        categories.append(category.to_dict())

    data = {
        'user_info': user.to_dict() if user else None,
        'news_dict': click_news_list,
        'category_list': categories,
    }

    return render_template('news/index.html', data=data)


@index_blu.route('/news_list')
def news_list():
    """
    获取首页新闻数据
    :return:
    """

    # 获取当前参数，并指定默认为最新分类，第一页，一页显示10条数据
    try:
        cid = int(request.args.get('cid',"1"))
        page = int(request.args.get('page',"1"))
    except:
        data = {
            'current_page': 1,
            'total_page': 1,
            'news_dict_list': [],
        }
        return jsonify(data=data,errno=RET.PARAMERR,errmsg="参数类型异常")

    # 校检参数
    if not all([cid,page]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    filter = [News.status == 0]
    if cid != 1:
        filter.append(News.category_id == cid)

    # 查询数据
    paginate = News.query.order_by(News.create_time.desc()).paginate(page, constants.HOME_PAGE_MAX_NEWS, False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    # 将模型对象转换成字典列表
    news_dict_list = []
    for item in items:
        news_dict_list.append(item.to_dict())
    data = {
        'current_page': current_page,
        'total_page': total_page,
        'news_dict_list': news_dict_list,
    }

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK', data=data)
