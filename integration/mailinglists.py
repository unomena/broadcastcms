from urllib import urlopen

class PMailer(object):
    def __init__(self, list_id, form_id, email):
        self.request_base_url = "http://pmailer.prefix.co.za/box.php?email=%s&p=%s&nlbox[1]=%s" % (email, str(form_id), str(list_id))

    def subscribe(self):
        request_url = self.request_base_url + "&funcml=add"
        self.send_request(request_url)
        return True

    def unsubscribe(self):
        request_url = self.request_base_url + "&funcml=unsub2"
        self.send_request(request_url)
        return True

    def send_request(self, url):
        try:
            f = urlopen(url)
        except IOError:
            #pmailer fails here although registration occured. ignore
            pass
