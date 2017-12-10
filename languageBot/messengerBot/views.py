from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json, requests, random
from pprint import pprint
from googletrans import Translator
from questionsGerman import generate_question_german
from questionsFrench import generate_question_french

page_access_token = '<page_access_token>'
lang = ''
quiz_mode = ''
quiz = False
answer = ''


class messengerBotView(generic.View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('hub.verify_token', '') == '<verify_token>':
            return HttpResponse(self.request.GET.get('hub.challenge'))
        else:
            return HttpResponse('Error, invalid token')

    def post(self, request, *args, **kwargs):
        get_started()
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    pprint(message)
                    seen_message(message['sender']['id'])
                    typing_message(message['sender']['id'])
                    post_facebook_message(message['sender']['id'], message['message'])
        return HttpResponse()


def set_persistent_menu():
    post_message_url = "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=" + page_access_token
    response_msg = json.dumps({
        "persistent_menu": [{
            "call_to_actions": [
                {
                    "type": "postback",
                    "title": "Get Started",
                    "payload": "_PAYLOAD"
                },
                {
                    "type": "web_url",
                    "title": "Review",
                    "url": "https://www.facebook.com/pg/Language-Bot-351106498695933/reviews/?ref=page_internal",
                    "webview_height_ratio": "full"
                }
            ]
        }]
    })
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())


# mark message as seen
def seen_message(fbid):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + page_access_token
    response_msg = json.dumps(
        {
            "recipient": {"id": fbid},
            "sender_action": "mark_seen"
        })
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())


# mark as typing
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


# get details of the user like first name,last name, profile picture etc
def get_user_details(fbid):
    user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
    user_details_params = {'fields': 'first_name,last_name', 'access_token': page_access_token}
    return requests.get(user_details_url, user_details_params).json()


def translate_text(lang, received_message):
    translator = Translator()
    message_text = translator.translate(received_message, dest=lang).text
    return message_text


def check_answer(received_message, fbid):
    if quiz_mode == 'de':
        question = generate_question_german()
    if quiz_mode == 'fr':
        question = generate_question_french()
    global answer
    right = [
        'Right! Next question: ',
        'Right answer! ;) ',
        'Correct! Next, ',
        'Bravo! Onto to the next one. ',
        'Right answer, keep it up! '
    ]
    wrong = [
        'Uh oh, wrong answer.',
        'Wrong :\ Better luck next question? ',
        'Incorrect! ',
        "Wrong answer! Keep going, don't get sad. "
    ]
    if received_message.lower() == answer:
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(right) + question['question']
            }
        })
    else:
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(wrong) + " Right answer is: " + answer + " " + question['question']
            }
        })
    answer = question['answer']
    return response_msg


def post_facebook_message(fbid, message):
    user_details = get_user_details(fbid)
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + page_access_token
    # check whether the received message is text or an attachment
    try:
        received_message = message['text']
    except:
        response_msg = json.dumps(
            {
                "recipient": {"id": fbid},
                "message": {"text": ":)"}
            })
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
        pprint(status.json())
        return 0

    response_msg = json.dumps(
        {
            "recipient": {"id": fbid},
            "message": {"text": "Sorry, we didn't quite understand. Type 'Help' to see the available commands :)",
                        "quick_replies": [
                            {
                                "content_type": "text",
                                "title": "/Help",
                                "payload": "<STRING_SENT_TO_WEBHOOK>"
                            }]
                        }})

    greeting = firstEntity(message['nlp'], 'greetings')
    if greeting and greeting['confidence'] > 0.8:
        greetings = [
            "Hello! Hola! Bonjour! Namaste! To begin learning choose from the following languages: ",
            "Hey " + user_details['first_name'] + "! Type the name of the language to start learning",
            'Welcome ' + user_details['first_name'] + ', to language learning bot! Click on one of the quick replies'
                                                      ' to begin learning.'
        ]
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(greetings),
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "/German",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/French",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
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
            'Bye ' + user_details['first_name'] + '.',
            'Hope you had a great time learning.'
        ]
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(bye_message)
            }})

    if lang != '':
        message_text = translate_text(lang, received_message)
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": message_text
            }
        })

    if received_message.lower() == "/about bot":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Hi! I am a demo bot written in Python (Django). I help you to learn languages. Currently"
                        " I only know German and French.",
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "/Help",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }})

    if received_message.lower() == "/german":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Get ready to learn German!",
                                "image_url": "https://upload.wikimedia.org/wikipedia/en/thumb/b/ba/Flag_of_Germany"
                                             ".svg/1200px-Flag_of_Germany.svg.png",
                                "subtitle": "Choose from the following"
                            }
                        ]
                    }
                },
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "German culture",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Translate in German",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "German quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }})

    if received_message.lower() == "/french":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Get ready to learn Fran\xc3\xa7ais!",
                                "image_url": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c3/Flag_of_France."
                                             "svg/1280px-Flag_of_France.svg.png",
                                "subtitle": "Choose from the following"
                            }
                        ]
                    }
                },
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "French culture",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Translate in French",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "French quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }})

    if received_message.lower() == "german quiz":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'Okay. So I am going to ask you simple question to start with. '
                        'Type "exit quiz" to quit. Shall we begin?',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "TEST MY GERMAN",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]

            }
        })

    if received_message.lower() == "french quiz":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'Okay. So I am going to ask you simple question to start with. '
                        'Type "exit quiz" to quit. Shall we begin?',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "TEST MY FRENCH",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]

            }
        })

    if quiz == True:
        response_msg = check_answer(received_message, fbid)

    if received_message.lower() == "test my german":
        global quiz_mode
        quiz_mode = 'de'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "What is your first name? (Answer goes like 'My name is... but in German obviously ;) )"
            }
        })
        global quiz
        global answer
        quiz = True
        answer = "ich bin " + user_details['first_name'].lower()

    if received_message.lower() == "test my french":
        global quiz_mode
        quiz_mode = 'fr'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "What is your first name? (Answer goes like 'My name is... but in French obviously ;) )"
            }
        })
        global quiz
        global answer
        quiz = True
        answer = "je suis " + user_details['first_name'].lower()

    if received_message.lower() == 'exit quiz':
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Okay. No more questions for you."
            }
        })
        quiz = False

    if received_message.lower() == "german culture":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Germany",
                                "image_url": 'http://www.middlebury.edu/system/files/media/Germany%20031%20bright.jpg',
                                "subtitle": 'Germany; German: Deutschland, officially the Federal Republic of'
                                            ' Germany (German: Bundesrepublik Deutschland),is a federal'
                                            ' parliamentary republic in central-western Europe.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://en.wikipedia.org/wiki/Germany",
                                        "title": "Read More"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        })

    if received_message.lower() == "french culture":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "France",
                                "image_url": 'http://www.socialmatter.net/wp-content/uploads/2015/11/france.jpg',
                                "subtitle" : 'France, officially the French Republic, is a country whose territory '
                                            'consists of metropolitan France in western Europe, as well as several '
                                            'overseas regions and territories.',
                                "buttons" : [
                                    {
                                        "type": "web_url",
                                        "url": "https://en.wikipedia.org/wiki/France",
                                        "title": "Read More"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        })

    if received_message.lower() == "translate in german":
        global lang
        lang = 'de'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'Send what you want to translate and we will do it for you! To exit translation mode, type "/Exit Translation" To begin, start with any of the '
                        'following:',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Good morning",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "How are you?",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": 'Have a great day!',
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": '/Exit Translation',
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }
        })

    if received_message.lower() == "translate in french":
        global lang
        lang = 'fr'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'Send what you want to translate and we will do it for you! To exit translation mode, type '
                        '"/Exit Translation" To begin, start with any of the '
                        'following:',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Good morning",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "How are you?",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": 'Have a great day!',
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": '/Exit Translation',
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }
        })

    if received_message.lower() == "/exit translation":
        global lang
        lang = ''
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'You have exited the translation mode.',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "/About Bot",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/German",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/French",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }

                ]
            }
        })

    if received_message.lower() == "/help":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Try any of the following: ",
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "/About Bot",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/German",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/French",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }})

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())


def get_started():
    post_message_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token=' + page_access_token
    response_msg = json.dumps({"get_started": {
        "payload": "<GET_STARTED_PAYLOAD>"
    }})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())
