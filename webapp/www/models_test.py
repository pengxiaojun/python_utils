import orm
from models import User
import random
import asyncio


def test(loop):
    yield from orm.create_pool(loop, user = 'root',
                               password = 'password',
                               database = 'webblog')


    s = str(random.randint(1,1000))
    user = User(name = 'Test-%s' % s,
                email = 'test%s@gmail.com' % s,
                passwd = 'password',
                admin = True,
                image = 'about:blank')

    yield from user.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
