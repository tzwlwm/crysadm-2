# API 权限管理
__author__ = 'powergx'
from functools import wraps
from flask import session, url_for, redirect
from crysadm import r_session
import json

# 需要管理员权限
def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_info') is None:
            return redirect(url_for('login'))

        user = session.get('user_info')

        user_key = '%s:%s' % ('user', user.get('username'))
        if r_session.get(user_key) is None:
            session.clear()
            return redirect(url_for('login'))

        user_info = json.loads(r_session.get(user_key).decode('utf-8'))

        if user_info.get('is_admin') is None or not user_info.get('is_admin'):
            session['user_info'] = user_info
            return redirect(url_for('dashboard'))
        __handshake()
        return f(*args, **kwargs)

    return decorated

# 需要用户权限
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_info') is None:
            return redirect(url_for('login'))

        user = session.get('user_info')

        user_key = '%s:%s' % ('user', user.get('username'))
        if r_session.get(user_key) is None:
            session.clear()
            session['error_message'] = '用户不存在'
            return redirect(url_for('login'))

        user_info = json.loads(r_session.get(user_key).decode('utf-8'))

        if user_info.get('active') is None or not user_info.get('active'):
            session.clear()
            session['error_message'] = '您的账号已被禁用.'
            return redirect(url_for('login'))
        __handshake()
        return f(*args, **kwargs)

    return decorated

# 加入在线用户列表
def __handshake():
    user = session.get('user_info')
    username = user.get('username')
    r_session.setex('user:%s:is_online' % username, '1', 120)
    r_session.sadd('global:online.users', username)