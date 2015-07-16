# -*-coding: utf-8 -*-


import re
import time
import json
import logging
import hashlib
import asyncio
import markdown2
from aiohttp import web
from coroweb import get, post
from models import User, Blog, Comment, next_id
from config import configs
from apis import Page, APIError, APIValueError


@get("/")
def index(request):
    blogs = yield from Blog.findall(orderby='created_at')
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }


@get('/register')
def register():
    logging.info("do register")
    return {'__template__': 'register.html' }


@get('/signin')
def signin():
    return { '__template__': 'signin.html' }


@post('/api/authenticate')
def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email')
    if not passwd:
        raise APIValueError('password', 'Invalid password')

    users = yield from User.findall('email=?', email)

    if len(users) == 0:
        raise APIValueError('email', 'Email not found')

    user = users[0]

    # check password
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))

    if user.passwd != sha1.hexdigest():
        raise APIValueError('password', 'Invalid password')

    # authenticate ok. set cookie
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=True).encode('utf-8')
    return r


@get('/signout')
def sigout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user sigout')
    return r


_RE_EMAIL = re.compile(r'^[a-z0-9A-Z]+\@[a-z0-9\-\_]+([\.a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

COOKIE_NAME = 'webblog'
_COOKIE_KEY = configs.session.secret


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def text2html(text):
    lines = map(lambda s : '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s:s.strip() != '', text.split('\n')))
    return ''.join(lines)


def user2cookie(user, max_age):
    '''
    Generate cookie by user
    user_id+expires+sha1(user_id+password+expires+secretkey)
    '''
    expires = str(int(time.time()) + max_age)
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


@asyncio.coroutine
def cookie2user(cookie_str):
    if not cookie_str:
        return None

    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None

        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None

        user = yield from User.find(uid)
        if user is None:
            return None

        s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            return None

        user.passwd = "*****"
        logging.info('cooke2user %s' % user.email)
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }


@get('/manage/blogs/edit')
def manage_edit_blog(*, id):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s' % id
    }


@get('/manage/blogs')
def manage_blogs(*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }


@get('/manage/users')
def manage_users(*, page='1'):
    return {
        '__template__': 'manage_users.html',
        'page_index':  get_page_index(page)
    }


@get('/manage/comments')
def manage_comments(*, page='1'):
    return {
        '__template__': 'manage_comments.html',
        'page_index':  get_page_index(page)
    }


@get('/manage/')
def manage():
    return 'redirect:/manage/comments'


@get('/blog/{id}')
def get_blog(id):
    blog = yield from Blog.find(id)
    comments = yield from Comment.findall('blog_id=?', [id], orderby='created_at')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


@post('/api/users')
def aip_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('eamil')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('password')

    users = yield from User.findall('email=?', [email])
    if len(users) > 0:
        raise APIError('reigster failile', 'email', 'Email is already in use')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id = uid,
                name=name.strip(),
                email = email.strip(),
                passwd = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image = 'http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest()
                )
    yield from user.save()

    # make cookie
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400,httponly=True)
    user.passwd = "*****"
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=True).encode('utf-8')
    return r


@post('/api/blogs')
def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise AIPValueError('name', 'name can not be empty')
    if not summary or not summary.strip():
        raise AIPValueError('summary', 'summary can not be empty')
    if not content or not content.strip():
        raise AIPValueError('content', 'content can not be empty')

    blog = Blog(user_id=request.__user__.id,
                user_name = request.__user__.name,
                user_image = request.__user__.image,
                name = name.strip(),
                summary = summary.strip(),
                content = content.strip()
                )
    yield from blog.save()
    return blog


@post('/api/blogs/{id}')
def api_update_blog(id, request, *, name, summary, content):
    check_admin(request)
    blog = yield from Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('blog not found')
    if not name or not name.strip():
        raise AIPValueError('name', 'name can not be empty')
    if not summary or not summary.strip():
        raise AIPValueError('summary', 'summary can not be empty')
    if not content or not content.strip():
        raise AIPValueError('content', 'content can not be empty')

    blog.name = name
    blog.summary = summary
    blog.content = content
    yield from blog.update()
    return blog


@post('/api/blogs/{id}/delete')
def api_delete_blog(request, *, id):
    check_admin(request)
    blog = yield from Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('blog not found')
    yield from blog.delete()
    return dict(id=id)


@get('/api/blogs/{id}')
def api_get_blog(*, id):
    blog = yield from Blog.find(id)
    return blog


@get('/api/users')
def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    num = yield from User.findnumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = yield from User.findall(orderby='created_at desc', limit=(p.offset, p.limit))
    for user in users:
        user.password='******'
    return dict(page=p, users=users)


@get('/api/blogs')
def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Blog.findnumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = yield from Blog.findall(orderby='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)


@get('/api/comments')
def api_comments(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Comment.findnumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = yield from Comment.findall(orderby='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)


@post('/api/blogs/{id}/comments')
def api_create_comment(id, request, *, content):
    user = request.__user__
    if user is None:
        raise APIPermissionError('please sign first')
    if not content or not content.strip():
        raise APIValueError('content')
    blog = yield from Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('resource not found')
    comment = Comment(blog_id=id,
                      user_id = user.id,
                      user_name = user.name,
                      user_image = user.image,
                      content = content.strip())
    yield from comment.save()
    return comment


@post('/api/comments/{id}/delete')
def api_delete_comment(id, request):
    check_admin(request)
    comment = yield from Comment.find(id)
    if comment is None:
        raise APIResourceNotFoundError('comment not found')
    yield from comment.remove()
    return dict(id=id)
