import storage as storage
from flask import render_template, g, request, jsonify, current_app, session, abort
from werkzeug.utils import redirect

from info import db, constants
from info.models import Category, News, User
from info.modules import news
from info.modules.index import index_blu
from utils.common import user_login_data
from utils.response_code import RET
from . import profile_blu
from info.constants import *



@profile_blu.route('/other_info')
@user_login_data
def other_info():
    user = g.user

    # 去查询其他人的用户信息
    other_id = request.args.get("user_id")

    if not other_id:
        abort(404)

    # 查询指定id的用户信息
    other = None
    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)

    if not other:
        abort(404)

    # 判断当前登录用户是否关注过该用户
    is_followed = False
    if other and user:
        if other in user.followed:
            is_followed = True

    data = {
        "is_followed": is_followed,
        "user": g.user.to_dict() if g.user else None,
        "other_info": other.to_dict()
    }
    return render_template('news/other.html', data=data)



@profile_blu.route('/other_news_list')
def other_news_list():
    """返回指定用户的发布的新闻"""

    # 1. 取参数
    other_id = request.args.get("user_id")
    page = request.args.get("p", 1)

    # 2. 判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not other:
        return jsonify(errno=RET.NODATA, errmsg="当前用户不存在")

    try:
        paginate = other.news_list.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取当前页数据
        news_li = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    news_dict_list = []
    for news_item in news_li:
        news_dict_list.append(news_item.to_basic_dict())

    data = {
        "news_list": news_dict_list,
        "total_page": total_page,
        "current_page": current_page
    }
    return jsonify(errno=RET.OK, errmsg="OK", data=data)



@profile_blu.route('/user_follow')
@user_login_data
def user_follow():
    # 获取页数
    p = request.args.get("p", 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    user = g.user

    follows = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.followed.paginate(p, constants.USER_FOLLOWED_MAX_COUNT, False)
        # 获取当前页数据
        follows = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    user_dict_li = []

    for follow_user in follows:
        user_dict_li.append(follow_user.to_dict())
    data = {"users": user_dict_li,
            "total_page": total_page,
            "current_page": current_page
            }
    return render_template('news/user_follow.html', data=data)


@profile_blu.route('/news_list')
@user_login_data
def user_news_list():

    # 查询数据
    # 返回数据
    user = g.user
    print(user,'新闻列表')
    if not user:
        return redirect('/')
    try:
        p = int(request.args.get('p', 1))
    except:
        p = 1
    paginate = user.news_list.paginate(p,USER_COLLECTION_MAX_NEWS, False)
    news_items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_list = []
    for news in news_items if news_items else []:
        news_list.append(news.to_review_dict())
    data = {
        'news_list': news_list,
        'total_page': total_page,
        'current_page': current_page,
    }
    return render_template('news/user_news_list.html', data=data)





@profile_blu.route('/news_release', methods=["GET", "POST"])
@user_login_data
def news_release():
    """发布新闻"""

    user = g.user
    if request.method == "GET":
        if not user:
            return redirect('/')
        category_list = Category.query.all()
        categories = []
        for category in category_list if category_list else []:
            categories.append(category.to_dict())
        categories.pop(0)
        data = {
            'categories': categories,
        }
        return render_template('news/user_news_release.html', data=data)

    title = request.form.get('title')
    category_id = request.form.get('category_id')
    digest = request.form.get('digest')
    # index_image = request.files.get('index_image')
    content = request.form.get('content')
    print(title,category_id,digest,content)
    if not all([title, category_id, digest, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    # image = index_image.read()
    # key_url = storage(image)
    news = News()
    print(content)
    news.title = title
    news.source = '个人用户'
    news.user_id = user.id
    news.status = 1
    news.category_id = category_id
    news.digest = digest
    # news.index_image_url = QINIU_DOMIN_PREFIX + key_url
    news.content = content
    db.session.add(news)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='发布新闻成功')



@profile_blu.route('/collection')
@user_login_data
def user_collection():
    """新闻收藏"""

    # 1. 获取参数
    user = g.user
    print(user,'新闻收藏')
    # 2. 判断参数
    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户未登录')
    # 3. 查询用户指定页数的收藏的新闻
    p = request.args.get('p', 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1
    collections = []
    current_page = 1
    total_page = 1
    # 进行分页数据查询
    try:
        paginate = user.collection_news.paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
        collections = paginate.items
    # 当前页数
        current_page = paginate.page
    # 总页数
        total_page = paginate.pages
    # 总数据
    except Exception as e:
        current_app.logger.error(e)
    # 收藏列表
    collection_dict_li = []
    for news in collections:
        collection_dict_li.append(news.to_basic_dict())
    # 返回数据
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "collections": collection_dict_li
    }

    return render_template('news/user_collection.html',data = data)






@profile_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    """修改密码"""

    # GET请求,返回
    # print(11111111111111)
    user = g.user
    print(user,'修改密码')
    if request.method == "GET":
        return render_template('news/user_pass_info.html')
    else:
        # print(22222222222222222222)
        # 1. 获取参数
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')
        # 2. 校验参数
        if not all([old_password,new_password]):
            return jsonify(errno = RET.PARAMERR,errmsg = '参数不足')
        # 3. 判断旧密码是否正确
        if not user.check_password(old_password):
            return jsonify(errno = RET.PWDERR,errmsg = '原密码错误')
        # 4. 设置新密码
        user.password = new_password
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno = RET.DBERR,errmsg = '保存数据失败')
        # print(33333333333333)
        # 返回
        return jsonify(errno = RET.OK,errmsg = 'OK')

@profile_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    """图片上传"""

    user = g.user
    print(user,"图片上传")
    if request.method == "GET":
        if not user:
            return redirect('/')
        data = {
            'user_info': user.to_dict() if user else None
        }
        return render_template('news/user_pic_info.html', data=data)
    avatar = request.files.get('avatar')
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg='请传入图片')
    image = avatar.read()
    key = storage(image)
    if not key:
        return jsonify(errno=RET.THIRDERR, errmsg='第三方系统出现问题')
    user.avatar_url = key
    db.session.commit()
    data = {
        'avatar_url': QINIU_DOMIN_PREFIX + key
    }
    return jsonify(errno=RET.OK, errmsg='设置成功', data=data)
    # return render_template('news/user_pic_info.html', data=data)


@profile_blu.route('/base_info',methods = ['GET','POST'])
@user_login_data
def base_info():
    """
    用户基本信息
    :return:
    """
    # 不同的请求方式，做不同的事情
    # 如果是GET请求,返回用户数据

    user = g.user
    print(user)
    print("用户基本信息")
    if request.method =='GET':
        # print('*'*100)
        return render_template('news/user_base_info.html', data={"user": g.user.to_dict()})

    else:
    # 修改用户数据
    # 获取传入参数
        nick_name = request.json.get('nick_name')
        print(nick_name)
        signature = request.json.get('signature')
        print(signature)
        gender = request.json.get('gender')
        print(gender)
    # 校验参数
        if not all([nick_name, signature, gender]):
            return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
        if gender not in (['MAN', 'WOMAN']):
            return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    # 修改用户数据
        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender
    # print('*' * 100)
    # 返回
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存信息失败')
    session['nick_name']=nick_name
    # print(2132465)
    return jsonify(errno=RET.OK,errmsg='OK')







@profile_blu.route('/info')
@user_login_data
def user_info():

    # 如果用户登陆则进入个人中心
    user = g.user
    print(user)
    print("进入个人中心")
    # 如果没有登陆,跳转主页
    if not user:
        return redirect('/')
    # 返回用户数据
    data = {
        'user':user.to_dict()
    }
    return render_template('news/user.html',data = data)