from windmill.authoring import WindmillTestClient

from django.conf import settings
from django.contrib.auth.models import User

from common import *

def test_register():
    # setup
    client = WindmillTestClient(__name__)
    settings.DEBUG = True
    # create a dummy existing user
    user = User.objects.create_user(username='existing_user', password='password', email='existing@user.com')
    user.save()
    load_home(client)

    # launch sign in modal
    client.click(link=u'Sign up')
    client.waits.forElement(xpath=u'//*[@id="TB_ajaxContent"]', timeout=u'')

    # test if required validators fire
    client.click(id=u'register_submit')
    client.asserts.assertText(xpath=u"//form[@id='frmRegister']/div[1]/p[1]/label", validator=u'This field is required.')
    client.asserts.assertText(xpath=u"//form[@id='frmRegister']/div[2]/p[1]/label", validator=u'This field is required.')
    client.asserts.assertText(xpath=u"//form[@id='frmRegister']/div[2]/p[2]/label", validator=u'This field is required.')
    client.asserts.assertText(xpath=u"//form[@id='frmRegister']/div[3]/p[1]/label", validator=u'This field is required.')
    client.asserts.assertText(xpath=u"//form[@id='frmRegister']/div[6]/p/label", validator=u'This field is required.')
    client.asserts.assertNotNode(xpath=u"//form[@id='frmRegister']/div[5]/p[1]/label")
    client.asserts.assertNotNode(xpath=u"//form[@id='frmRegister']/div[5]/p[2]/label")
    client.asserts.assertText(xpath=u"//form[@id='frmRegister']/div[4]/p[1]/label", validator=u'This field is required.')

    # test if existing username generates an error
    client.type(text=u'existing_user', id=u'id_username')
    client.triggerEvent(option=u'blur', id=u'id_username')
    client.waits.forElement(xpath=u"//form[@id='frmRegister']/div[1]/p[1]/label[@class='error']", timeout=u'')
    client.asserts.assertText(xpath=u"//form[@id='frmRegister']/div[1]/p[1]/label[@class='error']", validator=u'Sorry, that username already exists.')

    # test if new username is accepted
    client.type(text=u'new_user', id=u'id_username')
    client.triggerEvent(option=u'blur', id=u'id_username')

    client.type(text=u'Firstname', id=u'id_first_name')
    client.type(text=u'Lastname', id=u'id_last_name')

    # test if invalid email address generates an error
    client.type(text=u'invalid email', id=u'id_email_address')
    client.triggerEvent(option=u'blur', id=u'id_email_address')
    client.asserts.assertText(xpath=u"//form[@id='frmRegister']/div[3]/p[1]/label", validator=u'Please enter a valid email address.')

    # test if valid email address is accepted
    client.type(text=u'valid@dress.com', id=u'id_email_address')

    # test if invalid captcha generates an error
    client.type(text=u'invalid captcha', id=u'recaptcha_response_field')
    client.triggerEvent(option=u'blur', id=u'recaptcha_response_field')
    client.asserts.assertNode(xpath=u"//form[@id='frmRegister']/div[4]/p[1]/label[@class='busy']")
    client.waits.forElement(xpath=u"//form[@id='frmRegister']/div[4]/p[1]/label[@class='error']", timeout=u'')
    client.asserts.assertText(xpath=u"//form[@id='frmRegister']/div[4]/p[1]/label[@class='error']", validator=u'Incorrect, please try again.')
    client.waits.sleep(milliseconds=u'1000')

    # test if valid captcha is accepted (debug is a valid captcha when settings.DEBUG is True)
    client.type(text=u'debug', id=u'recaptcha_response_field')
    client.triggerEvent(option=u'blur', id=u'recaptcha_response_field')

    # test is terms acceptance is accepted
    client.check(id=u'id_accept_terms')

    # check if registration and login occurs
    client.click(id=u'register_submit')
    client.waits.forElement(link=u'Profile', timeout=u'')
    client.asserts.assertText(xpath=u"//div[@id='account_links']/p[2]/span[1]", validator=u'Hello new_user')
    load_home(client)
    client.waits.forElement(link=u'Profile', timeout=u'')
    client.asserts.assertText(xpath=u"//div[@id='account_links']/p[2]/span[1]", validator=u'Hello new_user')
