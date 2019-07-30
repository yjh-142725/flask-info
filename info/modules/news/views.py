from sqlalchemy.sql.functions import user

from info import db
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, Comment, CommentLike, Category, User
from utils.common import user_login_data
from utils.response_code import RET, error_map
from . import news_blu
from flask import render_template, g, jsonify, request, abort, current_app
import logging





@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    # print(123456465465)



    user = g.user
    news_click_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    click_news_list = []
    for news in news_click_list if news_click_list else []:
        click_news_list.append(news.to_dict())

    news = News.query.get(news_id)

    is_collected = False
    is_followed = False
    comment_list = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
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
    data = {
        'news_dict': news_click_list,
        'user': user.to_dict() if user else None,
        'news': news.to_dict() if news else None,
        'is_collected': is_collected,
        'comments': comments,
        'is_followed': is_followed,
    }

    return render_template('news/detail.html', data=data)



@news_blu.route('/news_collect',methods=["POST"])
@user_login_data
def news_collect():
    """新闻收藏"""

    news_id = request.json.get('news_id')
    action = request.json.get('action')
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    if action == "collect":
        user.collection_news.append(news)
    else:
        user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败")
    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_blu.route('/news_comment', methods=["POST"])
@user_login_data
def add_news_comment():
    """添加评论"""



    # 用户是否登陆
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 获取参数
    data_dict = request.json
    news_id = data_dict.get("news_id")
    comment_str = data_dict.get("comment")
    parent_id = data_dict.get("parent_id")
    if not all([news_id, comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")
    # 初始化模型,保存数据
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id
    #     保存到数据库
    # 保存到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存评论数据失败")

    # 返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())


@news_blu.route('/comment_like', methods=["POST"])
@user_login_data
def comment_like():
    """
    评论点赞
    :return:
    """
    # 用户是否登陆
    print(123132132132132)
    user = g.user
    if not user:
        return jsonify(errno =RET.SESSIONERR ,errmsg = '用户未登录')
    # 取到请求参数
    comment_id = request.json.get('comment_id')
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 判断参数
    if not all([comment_id,news_id,action]):
        return jsonify(errno = RET.PARAMERR,errmsg = '参数错误')
    if action not in ('add','remove'):
        return jsonify(errno = RET.PARAMERR,errmsg = '参数错误')
    # 获取到要被点赞的评论模型
	# action的状态,如果点赞,则查询后将用户id和评论id添加到数据库
            # 点赞评论
            # 更新点赞次数
    # 查询评论数据
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.errnor(e)
        return jsonify(errno= RET.DBERR,errmsg='查询参数失败')
    if not comment:
        return jsonify(errno=RET.NODATA,errmsg = '评论数据不存在')
    if action == 'add':
        comment_like = CommentLike.query.filter_by(comment_id=comment_id,user_id=user.id).first()


        if not comment_like:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = user.id
            db.session.add(comment_like)
            comment.like_count += 1
    # 取消点赞评论,查询数据库,如果以点在,则删除点赞信息
    # 更新点赞次数
    else:
        comment_like = CommentLike.query.filter_by(user_id=user.id, comment_id=comment_id).first()
        if comment_like:
            db.session.delete(comment_like)
            # 减小点赞条数
            comment.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.errnor(e)
        db.session.rollback()
        return jsonify(errno = RET.DBERR,errmsg = '操作失败')
    # 返回结果
    return jsonify(errno = RET.OK,errmsmg = '操作成功')



@news_blu.route('/followed_user', methods=["POST"])
@user_login_data
def followed_user():
    """关注或者取消关注用户"""

    # 获取自己登录信息

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='请先登录')
    action = request.json.get('action')
    other_id = request.json.get('user_id')
    if not all([action, other_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    other_user = User.query.get(other_id)
    if action == 'follow':
        if other_user not in user.followed:
            user.followed.append(other_user)
        else:
            return jsonify(errno=RET.PARAMERR, errmsg='已经关注过了')
    else:
        if other_user in user.followed:
            user.followed.remove(other_user)
        else:
            return jsonify(errno=RET.PARAMERR, errmsg='已经取消关注过了')
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='OK')