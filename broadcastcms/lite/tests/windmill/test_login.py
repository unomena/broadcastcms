from windmill.authoring import WindmillTestClient

from django.contrib.auth.models import User

from common import *

def test_login():
    # setup
    user = User.objects.create_user(username='valid_username', password='valid_password', email='email@ddress.com')
    user.save()
    client = WindmillTestClient(__name__)
    load_home(client)

    client.click(link=u'Sign in')
    client.waits.forElement(timeout=u'', id=u'login_submit')
    # empty fields
    client.click(id=u'login_submit')
    client.asserts.assertText(xpath=u"//form[@id='frmLogin']/div[1]/p/label", validator=u'This field is required.')
    client.asserts.assertText(xpath=u"//form[@id='frmLogin']/div[2]/p/label", validator=u'This field is required.')
    # incorrect fields
    client.type(text=u'incorrect username', id=u'id_username')
    client.type(text=u'incorrect password', id=u'id_password')
    client.click(id=u'login_submit')
    # correct fields
    client.type(text=u'valid_username', id=u'id_username')
    client.type(text=u'valid_password', id=u'id_password')
    client.click(id=u'login_submit')
    # login success
    client.waits.forElement(timeout=u'', id=u'sign_out')
