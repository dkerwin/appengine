from django.utils import simplejson as json
import urllib
import urllib2
import logging
 
from google.appengine.api import xmpp
from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

API_KEY = None

if API_KEY:
    api_key = 'key=%s' % API_KEY
else:
    api_key = ''

class XMPPHandler(xmpp_handlers.CommandHandler):
    """My commando bot to play with"""
    
    def text_message(self, message):
        """Act like a echo server"""
        
        if message.body[0:4] == "ping":
            message.reply("pong")
        else:
            message.reply(message.body[::-1])
    
    def help_command(self, message):
        """Help command"""
        
        h = """
        /short URL
            Short the given URL via goo.gl
        
        /translate [TARGET_LANG] TEXT
            Translate given text to optional target lang (default=EN)
        """
        
        message.reply(h)
    
    def short_command(self, message):
        """URL shortening"""
        
        logging.debug("Received URL %s" % message.arg)
        msg = message.arg.split()[0]
        url = "https://www.googleapis.com/urlshortener/v1/url?%s" % api_key
        req = urllib2.Request(url, json.dumps({"longUrl": msg}))
        req.add_header('Content-Type', 'application/json')
        res = urllib2.urlopen(req)
        message.reply("Short URL: %s" % json.loads(res.read())["id"])
    
    def translate_command(self, message):
        """Translate"""
        
        if message.arg[0:2] in ('de', 'en'):
            t = message.arg[0:2]
            m = message.arg[3:]
        else:
            t = 'en'
            m = message.arg
        
        url = "https://www.googleapis.com/language/translate/v2?%s&target=%s" % (api_key, t)
        url += "&%s" % urllib.urlencode({'q': m})
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        answer = json.loads(res.read())['data']['translations'][0]
        
        message.reply("%s => %s: %s" % (answer['detectedSourceLanguage'], t,
                                        answer['translatedText']))
    
application = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', XMPPHandler)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
