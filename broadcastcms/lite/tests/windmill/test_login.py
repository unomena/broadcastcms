from windmill.authoring import WindmillTestClient

from django.contrib.auth.models import User

from common import *

def test_login():
    # setup
    client = WindmillTestClient(__name__)
    #user = User.objects.create_user(username='username', password='password', email='foo@bar.com')
    #user.save()


    load_home(client)
    client.click(link=u'Sign in')
    client.waits.forElement(xpath=u'//*[@id="TB_ajaxContent"]', timeout=u'8000')
    client.type(text=u'test_user', id=u'id_username')
    client.type(text=u'test_password', id=u'id_password')
    client.click(id=u'login_submit')

    """
    # Errors when no fields supplied
    client.click(link=u'Login')
    client.waits.forElement(timeout=u'5000', id=u'TB_ajaxContent')
    client.click(id=u'login')
    client.waits.forElement(timeout=u'5000', id=u'TB_ajaxContent')
    client.asserts.assertText(xpath=u"//form[@id='frmLogin']/div/p[2]/span", validator=u'Please enter a username.')
    client.asserts.assertText(xpath=u"//form[@id='frmLogin']/div[2]/p[2]/span", validator=u'Please enter a password.')

    # Errors when authorization fails
    client.type(text=u'foo', id=u'id_username')
    client.type(text=u'bar', id=u'id_password')
    client.click(id=u'login')
    client.waits.sleep(milliseconds=u'5000')
    client.asserts.assertText(xpath=u"//form[@id='frmLogin']/div/span", validator=u'The username and password you entered is incorrect.')

    # Login success
    client.type(text=u'username', id=u'id_username')
    client.type(text=u'password', id=u'id_password')
    client.click(id=u'login')
    client.waits.forElement(timeout=u'5000', id=u'logout_link')
    """

