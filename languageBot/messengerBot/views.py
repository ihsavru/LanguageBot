from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json, requests
from pprint import pprint
import random

page_access_token = 'EAAUDpluM64kBAHUIpJLUuZAQkLByg95Om3aR0QZADw9FBNkSUqCpN6RV56r6BLBHVMbzP99JQiRIaXDmVsjjhVYSt3HQMwZBqVyROE8ZAVTUdgWnxu7pm2Cxcp7JWecqxNLklxJTwwq0amnqmvCZBsIZABOos6XKdHkM3UlwCAndYZBoLHGWr9D'

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
        get_started()
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    pprint(message)
                    if message['sender']['id'] != '351106498695933':
                        seen_message(message['sender']['id'])
                        typing_message(message['sender']['id'])
                        post_facebook_message(message['sender']['id'], message['message']['text'], message['message'])
        return HttpResponse()

def seen_message(fbid):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + page_access_token
    response_msg = json.dumps(
        {
            "recipient": {"id": fbid},
            "sender_action": "mark_seen"
                })
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())

def typing_message(fbid):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + page_access_token
    response_msg = json.dumps(
        {
            "recipient": {"id": fbid},
            "sender_action": "typing_on"
                })
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())

def firstEntity(nlp, name):
    try:
        return nlp and nlp['entities'] and nlp['entities'] and nlp['entities'][name] and nlp['entities'][name][0]
    except:
        return 0

def post_facebook_message(fbid, received_message, message):
    user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
    user_details_params = {'fields': 'first_name,last_name', 'access_token': page_access_token}
    user_details = requests.get(user_details_url, user_details_params).json()
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + page_access_token
    response_msg = json.dumps(
        {
         "recipient": {"id": fbid},
         "message": {"text": "Sorry, we didn't quite understand. Type 'Help' to see the available commands :)",
         "quick_replies": [
             {
                 "content_type": "text",
                 "title": "Help",
                 "payload": "<STRING_SENT_TO_WEBHOOK>"
             }]
         }})

    greeting = firstEntity(message['nlp'], 'greetings')
    if greeting and greeting['confidence'] > 0.8:
        greetings = [
            "Hello! Hola! Bonjour! Namaste! To begin learning choose from the following languages: German. Type 'German'.",
            "Hey "+ user_details['first_name']+ "! Type the name of the language to start learning",
            'Welcome ' + user_details['first_name'] + ', to language learning bot! Click on one of the quick replies to begin learning.'
        ]
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(greetings),
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "German",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }]
            }})

    thank = firstEntity(message['nlp'], 'thanks')
    if thank and thank['confidence'] > 0.8:
        thanks = [
            'I hope you are enjoying the experience so far :)',
            'No problem. It is my duty.',
            'Hope you are enjoying learning.',
            'You are welcome!'
        ]
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(thanks)
            }})

    bye = firstEntity(message['nlp'], 'bye')
    if bye and bye['confidence'] > 0.8:
        bye_message = [
            'See you again ' + user_details['first_name'] + '. Have a great day!',
            'Bye '+ user_details['first_name'] + '.',
            'Hope you had a great time learning.'
        ]
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(bye_message)
            }})

    if received_message == "About":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Hi! I am a demo bot written in Python (Django). I help you to learn languages. Currently I only know German.",
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Help",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }})

    if received_message == "German":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Get ready to learn German! Currently available topics are: Months, Weekdays, Numbers.",
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Months",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Weekdays",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Numbers",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }})

    if received_message == "Months":
        months = "The months are:\n Januar, Februar, Marz, April, Mai, Juni, Juli, August, September, Oktober, November, Dezember"
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": months}})

    if received_message == "Weekdays":
        weekdays = "The weekdays are:\n Montag (Monday) \n Dienstag (Tuesday) \n Mittwoch (Wednesday) \n Donnerstag (Thursday) \n Freitag (Friday) \n Samstag (Saturday) \n Sonntag (Sunday)"
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": weekdays}})

    if received_message == "Numbers":
        numbers =" \n 1	eins \n 2	zwei \n 3	drei \n 4	vier \n 5	funf \n 6	sechs\n 7	sieben \n 8	acht \n 9	neun \n 10	zehn"
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": numbers}})

    if received_message == "Help":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Try any of the following: ",
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "About",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "German",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Months",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Weekdays",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Numbers",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }})

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())

def get_started():
    post_message_url = 'https://graph.facebook.com/v2.6/me/threadsettings?accesstoken=' + page_access_token
    response_msg = json.dumps({"get_started":{
        "payload":"<GET_STARTED_PAYLOAD>"
      }})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())