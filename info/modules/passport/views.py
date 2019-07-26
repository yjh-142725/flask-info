from datetime import datetime
import random
import re
from flask import request, current_app, abort, make_response, jsonify, session

from info import redis_store, constants, db
from info.constants import SMS_CODE_REDIS_EXPIRES, IMAGE_CODE_REDIS_EXPIRES

from info.models import User
from utils.response_code import RET

from . import passport_blu
from utils.captcha.captcha import captcha




@passport_blu.route('/image_code')
def image_code():
    '''
    生成图片验证码
    '''

    # 获取图片验证的UUID
    # 1：获取参数
    image_code_id = request.args.get('image_Code')

    # 2：检验参数
    if not image_code_id:
        abort(403)

    # 3：生成图片验证码，其返回为名字、文本、以及图片
    name, text, image = captcha.generate_captcha()

    # 将图片存到redis中，并设置过期时间
    redis_store.set('image_code_' + image_code_id, text, IMAGE_CODE_REDIS_EXPIRES)
    resp = make_response(image)

    # 设置请求头属性-Content-Type响应的格式
    resp.headers['Content-Type'] = 'image/jpg'
    print('图片验证码为: %s' % text)
    return resp


@passport_blu.route('/sms_code', methods=["POST"])
def send_sms_code():
    """
    发送短信的逻辑
    :return:
    """


    # 1.将前端的参数转为字典
    mobile = request.json.get('mobile')
    print(mobile)
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')

    # 2.检验是否有值
    if not all([mobile, image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    if not re.match(r'1[^269]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入正确的电话号码')

    # 3. 先从redis中取出真实的验证码内容
    redis_image_code = redis_store.get('image_code_' + image_code_id)

    # 4. 与用户的验证码内容进行对比，如果对比不一致，那么返回验证码输入错误
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')
    if redis_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.PARAMERR, errmsg='请输入正确的图片验证码')

    # 5. 如果一致，生成短信验证码的内容(随机数据)
    random_sms = '%06d' % random.randint(0, 999999)
    # status_code = CCP().send_template_sms(mobile, [random_sms, 2], 1)
    # if status_code != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg='第三方系统错误')

    # 6. 发送短信验证码，保存验证码内容到redis
    redis_store.set('random_sms_' + mobile, random_sms, SMS_CODE_REDIS_EXPIRES)

    # 7. 告知发送结果
    print('手机验证码为: %s' % random_sms)

    # 8. 返回注册结果
    return jsonify(errno=RET.OK, errmsg='发送短信成功')



@passport_blu.route('/register', methods=["POST"])
def register():
    """
    注册功能
    :return:
    """

    # 1.获取参数
    mobile = request.json.get('mobile')
    smscode = request.json.get('smscode')
    password = request.json.get('password')

    # 判断获取的参数是否有值
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    if not re.match(r'1[^269]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入正确的电话号码')

    # 从redis中获取短信验证码
    redis_sms_code = redis_store.get('random_sms_' + mobile)
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')
    if redis_sms_code != smscode:
        return jsonify(errno=RET.PARAMERR, errmsg='请输入正确的短信验证码')

    # 4. 初始化 user 模型，并设置数据并添加到数据库
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password

    # 5. 保存用户登录状态
    db.session.add(user)
    db.session.commit()

    # 6.返回注册结果
    return jsonify(errno=RET.OK, errmsg='注册成功')

@passport_blu.route('/login', methods=["POST"])
def login():
    """
    登陆功能
    :return:
    """


    # 1.获取参数并判断是否有值
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    if not re.match(r'1[^269]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入正确的电话号码')

    # 2.从数据库中查询指定的用户，检验用户名密码
    user = User.query.filter(User.mobile == mobile).first()
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='没有此账号, 请先注册')
    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg='请输入正确的密码')

    # 3.保存用户登录状态
    session['user_id'] = user.id
    session['user_name'] = user.nick_name
    session['user_mobile'] = user.mobile

    # user.last_login = datetime.now()
    # db.session.add(user)
    # db.session.commit()

    # 4.返回注册结果
    return jsonify(errno=RET.OK, errmsg='登录成功')

@passport_blu.route("/logout", methods=['POST'])
def logout():
    """
    清除session中的对应登录之后保存的信息

    """

    # 清除session中的对应登录之后保存的信息
    session.pop("user_id", None)
    session.pop("mobile", None)
    session.pop("nick_name", None)

    # 返回结果
    return jsonify(errno=RET.OK,errmsg=RET.OK)
