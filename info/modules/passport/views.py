import datetime
import random
import re
from flask import request, current_app, abort, make_response, jsonify, session

from info import redis_store, constants, db

from info.models import User
from utils.response_code import RET
from . import passport_blu
from utils.captcha.captcha import captcha




@passport_blu.route('/image_code')
def image_code():
    '''
    生成图片验证码
    '''
    # 获取图片验证码的UUID即code_id

    image_code_id = request.args.get("image_Code")
    print(image_code_id)

    if not image_code_id:
        abort(403)


    # 生成图片验证码，其返回为名字、文本、以及图片
    name, text, image = captcha.generate_captcha()

    # name,text, image = generate_code()
    print("图片验证码是：{}".format(text))

    # 将图形验证码保存到redis数据库中
    try:
        # 保存当前生成的图片验证码内容，并且设置过期时间
        redis_store.setex('ImageCode_' + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)

    response = make_response(image)

    # 设置请求头属性-Content-Type响应的格式
    response.headers["Content-Type"] = "image/png"

    return response

@passport_blu.route('/sms_code', methods=["POST"])
def send_sms_code():
    """
    发送短信的逻辑
    :return:
    """
    # 1.将前端参数转为字典
    # 2. 校验参数(参数是否符合规则，判断是否有值)
    # 判断参数是否有值
    # 3. 先从redis中取出真实的验证码内容
    # 4. 与用户的验证码内容进行对比，如果对比不一致，那么返回验证码输入错误
    # 5. 如果一致，生成短信验证码的内容(随机数据)
    # 6. 发送短信验证码
    # 保存验证码内容到redis
    # 7. 告知发送结果
    json_data = request.json
    mobile = json_data.get("mobile")
    print(mobile)
    image_code = json_data.get("image_code")
    image_code_id = json_data.get("image_code_id")

    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not re.match("^1[3578][0-9]{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号不正确")

    try:
        real_image_code = redis_store.get("ImageCode_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not real_image_code:
        return jsonify(errno=RET.DBERR, errmsg="验证码已经过期")

    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")
    # num1 = int(real_image_code[:1])
    # num2 = int(real_image_code[2:3])
    # num = num1 + num2
    # if num != int(image_code):
    #     return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机号已经被注册")

    # 后端自己生成验证码
    result = random.randint(0, 999999)
    get_sms_code = "%06d" % result
    print("短信验证码是：{}".format(get_sms_code))
    # 屌用第三方去发送短信
    # result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], "1")
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")

    try:
        redis_store.set("SMS_" + mobile, get_sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="手机验证码保存失败")

    return jsonify(errno=RET.OK, errmsg="发送成功")





@passport_blu.route('/register', methods=["POST"])
def register():
    """
    注册功能
    :return:
    """

    # 1. 获取参数和判断是否有值

    mobile = request.json.get('mobile')
    sms_code = request.json.get('smscode')
    password = request.json.get('password')
    print("1",mobile)
    print("2",password)
    print("3",sms_code)
    if not all([mobile,sms_code,password]):
        return jsonify(errno = RET.DATAERR,errmsg = "参数有误")
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    # 2. 从redis中获取指定手机号对应的短信验证码的
    try:
        real_sms_code = redis_store.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')
    # 3. 校验验证码
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')

    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')

    try:
        redis_store.delete('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已注册')

    # 4. 初始化 user 模型，并设置数据并添加到数据库
    user = User()
    user.mobile = mobile
    user.password = password
    user.nick_name = mobile
    user.last_login = datetime.now()
    # 5. 保存用户登录状态
    try:
        db.session.sdd(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR, errmsg = "数据保存失败")
    session['user_id'] = user.id
    session['mobile'] = mobile
    session['nick_name'] = mobile
    # 6. 返回注册结果
    return jsonify(errno=RET.OK, errmsg='注册成功')

@passport_blu.route('/login', methods=["POST"])
def login():
    """
    登陆功能
    :return:
    """

    # 1. 获取参数和判断是否有值
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    if not all([mobile,password]):
        return jsonify(errno = RET.DATAERR,errmsg = "")
    # 2. 从数据库查询出指定的用户
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)

    # 3. 校验密码
    if user is None or not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码错误')
    # 4. 保存用户登录状态
        session['user_id'] = user.id
        session['mobile'] = user.mobile

        session['nick_name'] = user.nick_name

        user.last_login = datetime.now()
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    # 5. 登录成功返回
    return jsonify(errno = RET.OK, errmsg = '登陆成功')
