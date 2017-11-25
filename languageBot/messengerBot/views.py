from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json, requests
from pprint import pprint


class messengerBotView(generic.View):
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

def post_facebook_message(fbid, received_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAUDpluM64kBAHUIpJLUuZAQkLByg95Om3aR0QZADw9FBNkSUqCpN6RV56r6BLBHVMbzP99JQiRIaXDmVsjjhVYSt3HQMwZBqVyROE8ZAVTUdgWnxu7pm2Cxcp7JWecqxNLklxJTwwq0amnqmvCZBsIZABOos6XKdHkM3UlwCAndYZBoLHGWr9D'
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": "Hello! Welcome to Language Learning Bot. This is a demo :) To begin learning choose from the following languages: German. Type 'German'."}})

    if received_message == "hi":
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": "Hello! Hola! Bonjour! Namaste!"}})

    if received_message == "German":
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": "Get ready to learn German! Type: Months, Weekdays, Numbers."}})

    if received_message == "Months":
        months = "The months are:\n Januar, Februar, Marz, April, Mai, Juni, Juli, August, September, Oktober, November, Dezember"
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": months}})

    if received_message == "Weekdays":
        weekdays = "The weekdays are:\n Montag (Monday) \n Dienstag (Tuesday) \n Mittwoch (Wednesday) \n Donnerstag (Thursday) \n Freitag (Friday) \n Samstag (Saturday) \n Sonntag (Sunday)"
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": weekdays}})

    if received_message == "Numbers":
        numbers =" \n 1	eins \n 2	zwei \n 3	drei \n 4	vier \n 5	funf \n 6	sechs\n 7	sieben \n 8	acht \n 9	neun \n 10	zehn"
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": numbers}})

    if received_message == "bye" or received_message == "Bye":
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": "Bye! See you again :)"}})

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())
