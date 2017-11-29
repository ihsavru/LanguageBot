from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json, requests, random, re
from pprint import pprint

class EchoBotView(generic.View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('hub.verify_token', '') == '987654321':
            return HttpResponse(self.request.GET.get('hub.challenge'))
        else:
            return HttpResponse('Error, invalid token')

    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    pprint(message)
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()

def post_facebook_message(fbid, recevied_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAADGpiR3vo4BANDMkbaPGor8AdvsCaXe83DkOLq4fdiLfzFyT7xkDpfshyADILbSplWvoN2xH9CU9liMZBxInLp0yoH2rHZAYOgZBbL5ZAbVFiW4DJSfJZA6C7Aj8eZCpAnYsm5ZBcyXuGCY7NyXzk89ee2XyDSYn81LKbVfv0u7GltXBh929wZC'
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())

