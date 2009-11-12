def load_home(client):
    client.open(url=u'/')
    client.waits.forElement(xpath=u'/html/body/div[2]', timeout=u'')
