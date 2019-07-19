# from . import index_blu
from flask import render_template, session, current_app, g, jsonify, request

from info.constants import CLICK_RANK_MAX_NEWS
from info.models import User, Category, News
from utils.response_code import RET
from . import index_blu

# 测试
@index_blu.route('/')
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
    # 获取当前的登录用户的ID
    user_id = session.get('user_id')
    user = None
    try:
        user = User.query.filter_by(id = user_id).first()
    except Exception as e:
        current_app.logger.error(e)

    # 右侧新闻排行
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)

    # 按照点击量排序查询出点击最高的前10条新闻
    clicks_news_li = []
    for new_abj in clicks_news:
        clicks_news_dict = new_abj.to_basic_dict()
        clicks_news_li.append(clicks_news_dict)
    # 获取新闻分类
    category_all = Category.query.all()
    # 定义列表保存分类数据
    categories = []
    for category_abj in category_all:
        category_dict = category_abj.to_dict()
        categories.append(category_dict)
    # 拼接内容
        data = {
            "user": user,
            "news_dict": clicks_news_li,
            "categories": categories,

        }
    return render_template("news/index.html",data = data)


@index_blu.route('/news_list')
def news_list():
    """
    获取首页新闻数据
    :return:
    """

    # 获取当前参数，并指定默认为最新分类，第一页，一页显示10条数据
    try:
        cid = int(request.args.get('cid'))
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
    except:
        cid = 1
        page = 1
        per_page = 10

    # 校检参数
    if not all([cid, per_page]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    filter = [News.status == 0]
    if cid != 1:
        filter.append(News.category_id == cid)

    # 查询数据
    paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(page, per_page, False)
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
        'news_dict_li': news_dict_list,
    }

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='OK', data=data)
