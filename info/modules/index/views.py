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


    user = g.user

    # 右侧的新闻排行榜
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    click_news_list = []
    for news in news_list if news_list else []:
        click_news_list.append(news.to_basic_dict())

    # 新闻分类页面
    # (1)获取新闻分类
    categories = Category.query.all()
    # (2)定义列表保存分类
    categories_dicts = []
    for category in categories:
        # 拼接内容
        categories_dicts.append(category.to_dict())

    data = {

        'user': user.to_dict() if user else None,
        'news_dict': click_news_list,
        'category_list': categories_dicts,
    }

    return render_template('news/index.html', data=data)


@index_blu.route('/news_list')
def news_list():
    """
    获取首页新闻数据
    :return:
    """

    # 获取当前参数，并指定默认为最新分类，第一页，一页显示10条数据
    # cid = int(request.args.get('cid', 1))
    # page = int(request.args.get('page', 1))
    # per_page = int(request.args.get('per_page', 10))
    #
    # if not all([cid, per_page]):
    #     return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    # filter = [News.status == 0]
    # if cid != 1:
    #     filter.append(News.category_id == cid)
    # paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(page, per_page, False)
    # items = paginate.items
    # current_page = paginate.page
    # total_page = paginate.pages
    # news_dict_list = []
    # for item in items:
    #     news_dict_list.append(item.to_dict())
    # data = {
    #     'current_page': current_page,
    #     'total_page': total_page,
    #     'news_dict_list': news_dict_list,
    # }

    # 1.获取参数
    page = request.args.get('p', '1')
    per_page = request.args.get('per_page', constants.HOME_PAGE_MAX_NEWS)
    category_id = request.args.get('cid', '1')
    # 2.检验参数
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 3.查询数据并分页
    filters = []
    #   如果分类id不为1,那么添加分类伪id的过滤
    if category_id != '1':
        filters.append(News.category_id == category_id)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
        items = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    news_li = []
    for news in items:
        news_li.append(news.to_basic_dict())
    # 返回结果
    data = {
        'total_page' : total_page ,
        'current_page' : current_page ,
        'news_dict_list':  news_li ,
        'cid' : category_id ,
    }
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


