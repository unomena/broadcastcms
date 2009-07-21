import urllib

class ReCaptcha(object):

    def verify(self, request):
        remote_ip = request.META.get('REMOTE_ADDR')
        challenge = request.REQUEST.get('recaptcha_challenge_field', '')
        response = request.REQUEST.get('recaptcha_response_field', '')

        params = urllib.urlencode({
            'privatekey': '6LdcYgcAAAAAANbLm37E8r-A4_IlgdUap4ryVql-', 
            'remoteip': remote_ip,
            'challenge': challenge,
            'response': response
        })
        f = urllib.urlopen("http://api-verify.recaptcha.net/verify", params)
        result = f.read().split('\n')[0]
        
        return result == 'true'
