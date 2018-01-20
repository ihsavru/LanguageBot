# This Python file uses the following encoding: utf-8
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json, requests, random
from pprint import pprint
from googletrans import Translator
from questions import generate_question
from datetime import datetime

page_access_token = ''

lang = {}
quiz_mode = {}
speech_mode = {}
quiz = {}
speech = {}
answer = {}
score = {}
count = {}


class messengerBotView(generic.View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('hub.verify_token', '') == '':
            return HttpResponse(self.request.GET.get('hub.challenge'))

        else:
            return HttpResponse('Error, invalid token')

    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                pprint(message)
                post_facebook_message(message['sender']['id'], message)
            return HttpResponse()

def persistent_menu():
    post_message_url = "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=" + page_access_token
    response_msg = json.dumps({
        "persistent_menu": [{
            "locale": "default",
            "call_to_actions": [
                {
                    "type": "web_url",
                    "title": "Review",
                    "url": "https://www.facebook.com/pg/Language-Bot-351106498695933/reviews/?ref=page_internal",
                    "webview_height_ratio": "full"
                },
                {
                    "title": "Languages",
                    "type": "postback",
                    "payload": "LANGUAGE_PAYLOAD"
                },
                {
                    "type": "web_url",
                    "title": "Source Code",
                    "url": "https://github.com/ihsavru/LanguageBot",
                    "webview_height_ratio": "full"
                },
            ]
        }]
    })
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    print("Persistent menu")
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


def translate_text(received_message, destination):
    translator = Translator()
    message_text = translator.translate(received_message, dest=destination).text
    return message_text

def translate_answer(received_message, source, destination ):
    translator = Translator()
    if len(received_message.split())>1 and translator.detect(received_message).lang != source:
        answer_text = 'aaaa'
    else:
        answer_text = translator.translate(received_message, src=source,dest=destination).text
    return answer_text


def check_answer(received_message, fbid):
    global count
    if quiz_mode[fbid] == 'de':
        question = generate_question('German')
    if quiz_mode[fbid] == 'fr':
        question = generate_question('French')
    if quiz_mode[fbid] == 'es':
        question = generate_question('Spanish')
    if quiz_mode[fbid] == 'sv':
        question = generate_question('Swedish')
    if quiz_mode[fbid] == 'ja':
        question = generate_question('Japanese')
    if quiz_mode[fbid] == 'ko':
        question = generate_question('Korean')
    count[fbid] = count[fbid] + 1
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
    if answer[fbid].lower() in translate_answer(received_message, quiz_mode[fbid], 'en').lower():
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(right) + question['question']
            }
        })
        score[fbid] = score[fbid] + 1
    else:
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(wrong) +" Right answer is "+ translate_text(answer[fbid], quiz_mode[fbid]).lower() + ". " + question['question']
            }
        })
    answer[fbid] = question['answer']
    return response_msg

def handle_audio(received_message,fbid):
    url = "https://translate.google.com/translate_tts?ie=UTF-8&tl="+speech[fbid]+"-TR&client=tw-ob&q="+received_message.encode('utf-8').replace(" ","+")
    print(url)
    response_msg = json.dumps(
        {
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "audio",
                    "payload": {
                        "url": url,
                        "is_reusable": "true"
                    }
                }
            }
        })
    return response_msg

def handle_postbacks(fbid, postback):
    if postback['payload'] == '<GET_STARTED_PAYLOAD>':
        response_msg = json.dumps(
            {
                "recipient": {"id": fbid},
                "message": {
                    "text": "Welcome to Language Bot! Thankyou for messaging us. To begin learning,"
                            " choose from the following:",
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
                        },
                        {
                            "content_type": "text",
                            "title": "/Spanish",
                            "payload": "<STRING_SENT_TO_WEBHOOK>"
                        },
                        {
                            "content_type": "text",
                            "title": "/Swedish",
                            "payload": "<STRING_SENT_TO_WEBHOOK>"
                        },
                        {
                            "content_type": "text",
                            "title": "/Japanese",
                            "payload": "<STRING_SENT_TO_WEBHOOK>"
                        },
                        {
                            "content_type": "text",
                            "title": "/Korean",
                            "payload": "<STRING_SENT_TO_WEBHOOK>"
                        }
                    ]}
            })
        return response_msg
    if postback['payload'] == 'LANGUAGE_PAYLOAD':
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Following languages are currently supported:",
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
                    },
                    {
                        "content_type": "text",
                        "title": "/Spanish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Swedish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Japanese",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Korean",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }})
        return response_msg

def post_facebook_message(fbid, fb_message):
    global speech_mode, speech, quiz_mode, quiz, answer, lang
    user_details = get_user_details(fbid)
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + page_access_token
    try:
        postback = fb_message['postback']
        response_msg = handle_postbacks(fbid, postback)
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
        pprint(status.json())
        return 0
    except KeyError:
        message = fb_message['message']
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

    default_text = [
        "Sorry, I didn't quite understand. Type 'Help' to see the available commands :)",
        "I don't quite know the answer to that. But you can try doing the following:",
        "Select from the following:",
        "I have some quick replies ready for you:",
        "Try any of these instead:"
    ]
    response_msg = json.dumps(
        {
            "recipient": {"id": fbid},
            "message": {"text": random.choice(default_text),
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
                    },
                    {
                        "content_type": "text",
                        "title": "/Spanish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Swedish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Japanese",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Korean",
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

    datetime_msg = firstEntity(message['nlp'], 'datetime')
    if datetime_msg and datetime_msg['confidence'] > 0.8 and datetime_msg['grain'] =="day":
        d = datetime.now()
        date = [
            d.strftime("%d,%B") + " isn't such a bad day.",
            d.strftime("%A") + "s are fundays!",
        ]
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(date)
            }})

    bye = firstEntity(message['nlp'], 'bye')
    if bye and bye['confidence'] > 0.8:
        bye_message = [
            'See you again ' + user_details['first_name'] + '. Have a great day!',
            'Bye ' + user_details['first_name'] + '.',
            'Hope you had a great time learning.',
            'Goodbye ' + user_details['first_name'] + ". Let's catchup later.",
        ]
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": random.choice(bye_message)
            }})
    if "how are you" in received_message.lower():
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "I am fine, thank you!"
            }})

    if "what is your name" in received_message.lower():
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Call me whatever you want ;)"
            }})

    if "how old are you" in received_message.lower():
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "I was born when the third edition of LITG started!"
            }})


    if received_message.lower() == "/about bot":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Hi! I am a demo bot written in Python (Django). I help you to learn languages. Currently"
                        " I only know German, French, Spanish, Swedish, Japanese and Korean.",
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "/Help",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }})

    if received_message.lower() == "/german":
        #initialise variables
        lang[fbid] = ''
        speech_mode[fbid] = False
        speech[fbid] = ''
        score[fbid] = 0
        count[fbid] = 0
        quiz_mode[fbid] = ''
        quiz[fbid] = False

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
                    },
                ]
            }})

    if received_message.lower() == "/french":
        #initialise variables
        lang[fbid] = ''
        speech_mode[fbid] = False
        speech[fbid] = ''
        score[fbid] = 0
        count[fbid] = 0
        quiz_mode[fbid] = ''
        quiz[fbid] = False
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
                    },
                ]
            }})

    if received_message.lower() == "/spanish":
        # initialise variables
        lang[fbid] = ''
        speech_mode[fbid] = False
        speech[fbid] = ''
        score[fbid] = 0
        count[fbid] = 0
        quiz_mode[fbid] = ''
        quiz[fbid] = False
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Get ready to learn Espa\xc3\xb1ol!",
                                "image_url": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Flag_of_Spain."
                                             "svg/1200px-Flag_of_Spain.svg.png",
                                "subtitle": "Choose from the following"
                            }
                        ]
                    }
                },
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Spanish culture",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Translate in Spanish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Spanish quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                ]
            }})

    if received_message.lower() == "/swedish":
        # initialise variables
        lang[fbid] = ''
        speech_mode[fbid] = False
        speech[fbid] = ''
        score[fbid] = 0
        count[fbid] = 0
        quiz_mode[fbid] = ''
        quiz[fbid] = False
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Get ready to learn Svenska!",
                                "image_url": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4c/Flag_of_Sweden.svg/"
                                             "1200px-Flag_of_Sweden.svg.png",
                                "subtitle": "Choose from the following"
                            }
                        ]
                    }
                },
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Swedish culture",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Translate in Swedish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Swedish quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                ]
            }})

    if received_message.lower() == "/japanese":
        # initialise variables
        lang[fbid] = ''
        speech_mode[fbid] = False
        speech[fbid] = ''
        score[fbid] = 0
        count[fbid] = 0
        quiz_mode[fbid] = ''
        quiz[fbid] = False
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Get ready to learn 日本語!",
                                "image_url": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9e/Flag_of_Japan.svg/"
                                             "1200px-Flag_of_Japan.svg.png",
                                "subtitle": "Choose from the following"
                            }
                        ]
                    }
                },
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Japanese culture",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Translate in Japanese",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Japanese quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                ]
            }})

    if received_message.lower() == "/korean":
        # initialise variables
        lang[fbid] = ''
        speech_mode[fbid] = False
        speech[fbid] = ''
        score[fbid] = 0
        count[fbid] = 0
        quiz_mode[fbid] = ''
        quiz[fbid] = False
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Get ready to learn 한국어!",
                                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Flag_of_South_Korea.svg/1200px-Flag_of_South_Korea.svg.png",
                                "subtitle": "Choose from the following"
                            }
                        ]
                    }
                },
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Korean culture",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Translate in Korean",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Korean quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                ]
            }})

    global count, score

    if received_message.lower() == "german quiz":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'Okay. So I am going to ask you simple question to start with. '
                        'Type "/exit quiz" to quit. Shall we begin?',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "TEST MY GERMAN",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]

            }
        })
        count[fbid] = 0
        score[fbid] = 0

    if received_message.lower() == "french quiz":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'Okay. So I am going to ask you simple question to start with. '
                        'Type "/exit quiz" to quit. Shall we begin?',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "TEST MY FRENCH",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]

            }
        })
        count[fbid] = 0
        score[fbid] = 0

    if received_message.lower() == "spanish quiz":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'Okay. So I am going to ask you simple question to start with. '
                        'Type "/exit quiz" to quit. Shall we begin?',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "TEST MY SPANISH",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]

            }
        })
        count[fbid] = 0
        score[fbid] = 0

    if received_message.lower() == "swedish quiz":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'Okay. So I am going to ask you simple question to start with. '
                        'Type "/exit quiz" to quit. Shall we begin?',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "TEST MY SWEDISH",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]

            }
        })
        count[fbid] = 0
        score[fbid] = 0

    if received_message.lower() == "japanese quiz":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'Okay. So I am going to ask you simple question to start with. '
                        'Type "/exit quiz" to quit. Shall we begin?',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "TEST MY JAPANESE",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]

            }
        })
        count[fbid] = 0
        score[fbid] = 0

    if received_message.lower() == "korean quiz":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": 'Okay. So I am going to ask you simple question to start with. '
                        'Type "/exit quiz" to quit. Shall we begin?',
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "TEST MY KOREAN",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]

            }
        })
        count[fbid] = 0
        score[fbid] = 0

    try:
        if quiz[fbid] == True:
            response_msg = check_answer(received_message, fbid)
    except:
        print("Exception: quiz not true")

    if "test my german" in received_message.lower():
        quiz_mode[fbid] = 'de'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "What is a table called in German?"
            }
        })
        quiz[fbid] = True
        answer[fbid] = "table"

    if "test my french" in received_message.lower():
        quiz_mode[fbid] = 'fr'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "What is a chair called in French?"
            }
        })
        quiz[fbid] = True
        answer[fbid] = "chair"

    if "test my spanish" in received_message.lower():
        quiz_mode[fbid] = 'es'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "How many days are there in December?"
            }
        })
        quiz[fbid] = True
        answer[fbid] = "thirty one"

    if "test my swedish" in received_message.lower():
        quiz_mode[fbid] = 'sv'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "What is apple called in Swedish?"
            }
        })
        quiz[fbid] = True
        answer[fbid] = "apple"

    if "test my japanese" in received_message.lower():
        quiz_mode[fbid] = 'ja'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "What is sky called in Japanese?"
            }
        })
        quiz[fbid] = True
        answer[fbid] = "sky"

    if "test my korean" in received_message.lower():
        quiz_mode[fbid] = 'ko'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "What is milk called in Korean?"
            }
        })
        quiz[fbid] = True
        answer[fbid] = "milk"

    if received_message.lower() == '/exit quiz':
        try:
            exit_text = "Okay. No more questions for you. *You scored " + str(score[fbid]) + "/" + str(
                count[fbid]) + "*. Want to try something else?"
        except:
            exit_text = "No quiz is running. Want to try something else?"
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": exit_text,
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
                    },
                    {
                        "content_type": "text",
                        "title": "/Spanish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Swedish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Japanese",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Korean",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }
        })
        score[fbid] = 0
        count[fbid] = 0
        quiz_mode[fbid] = ''
        quiz[fbid] = False

    if received_message.lower() == "german culture":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "list",
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
                                        "title": "Read on Wikipedia"
                                    }
                                ]
                            },
                            {
                                "title": "Trending music in Germany right now:",
                                "image_url": 'https://i.scdn.co/image/2326cec8b084055d2b367a9832dbb2ac3561e9c5',
                                "subtitle": 'Check out the Top 50 songs on Spotify in Deutschland.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://open.spotify.com/user/spotifycharts/playlist/37i9dQZEVXbJiZcmkrIHGU",
                                        "title": "Listen on Spotify"
                                    }
                                ]
                            },
                            {
                                "title": "10 epic German movies you have to watch before you die:",
                                "image_url": 'https://www.thelocal.de/userdata/images/article/81f29395ba5384469931c57c8'
                                             '832e191ee057d74d3062fdff761f675e4fe8278.jpg',
                                "subtitle": 'These German films are so good, not even The Cabinet of Dr. Caligari made'
                                            ' the list.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://www.thelocal.de/20160927/10-german-films-to-watch-before-you-die"
                                               "-cinema-tv-oscars",
                                        "title": "Read More"
                                    }
                                ]
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
                    },
                    {
                        "content_type": "text",
                        "title": "Pronounce in German",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }
        })

    if received_message.lower() == "french culture":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "list",
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
                                        "title": "Read on Wikipedia"
                                    }
                                ]
                            },
                            {
                                "title": "Trending music in France right now:",
                                "image_url": 'https://i.scdn.co/image/5d4c015586839d8be283f6762fdf847129f35d2f',
                                "subtitle": 'Check out the Top 50 songs on Spotify in France.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://open.spotify.com/user/spotifycharts/playlist/37i9dQZEVXbIPWwFss"
                                               "bupI",
                                        "title": "Listen on Spotify"
                                    }
                                ]
                            },
                            {
                                "title": "The 25 best French movies of the 21st century, from ‘Amélie’ to ‘Cache’",
                                "image_url": 'https://pmd205465tn-a.akamaihd.net/Miramax/292/783/hoZGh3NTp_kCe_bj8enLPd'
                                             'KFmD_TPQkp_640x360_251740227538.jpg',
                                "subtitle": 'The best French films of the 21st Century remind us why France is still as'
                                            ' important to cinema as light itself.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "http://www.indiewire.com/2017/06/best-french-movies-films-21st-century"
                                               "-so-far-1201848966/"
                                               "bupI",
                                        "title": "Read More"
                                    }
                                ]
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
                        "title": 'Translate in French',
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "French quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Pronounce in French",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }
        })

    if received_message.lower() == "spanish culture":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "list",
                        "elements": [
                            {
                                "title": "Spain",
                                "image_url": 'https://secure.parksandresorts.wdpromedia.com/resize/mwImage/1/1200/600/9'
                                             '0/secure.parksandresorts.wdpromedia.com/media/abd/refresh/europe/spain-va'
                                             'cations/adventures-by-disney-europe-spain-hero-03-great-mosque-of-cordo'
                                             'ba.jpg',
                                "subtitle" : 'Spain, officially the Kingdom of Spain, is a sovereign state located on '
                                             'the Iberian Peninsula in southwestern Europe, with two large archipelag',
                                "buttons" : [
                                    {
                                        "type": "web_url",
                                        "url": "https://en.wikipedia.org/wiki/Spain",
                                        "title": "Read on Wikipedia"
                                    }
                                ]
                            },
                            {
                                "title": "Trending music in Spain right now:",
                                "image_url": 'https://i.scdn.co/image/d63704d94ab97f6ebe2633e877bb6764ec31dc2e',
                                "subtitle": 'Check out the Top 50 songs on Spotify in Spain.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://open.spotify.com/user/spotifycharts/playlist/37i9dQZEVXbNFJfN"
                                               "1Vw8d9",
                                        "title": "Listen on Spotify"
                                    }
                                ]
                            },
                            {
                                "title": "8 incredible Spanish movies on Netflix that you’ve gotta see",
                                "image_url": 'https://www.fluentu.com/blog/spanish/wp-content/uploads/sites/2/2015/09/'
                                             'spanish-movies-netflix7.jpg',
                                "subtitle": 'As language learners, learning to listen is a vital part of our '
                                            'informational intake and advancement.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://www.fluentu.com/blog/spanish/spanish-movies-netflix/",
                                        "title": "Read More"
                                    }
                                ]
                            }
                        ]
                    }
                },
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Spanish culture",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Translate in Spanish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Spanish quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Pronounce in Spanish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }
        })

    if received_message.lower() == "swedish culture":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "list",
                        "top_element_style": "large",
                        "elements": [
                            {
                                "title": "Sweden",
                                "image_url": 'http://www.globalblue.com/tax-free-shopping/sweden/article641223.ece/al'
                                             'ternates/LANDSCAPE2_970/Gamla-Stan-View-Stockholm-Sweden.jpg',
                                "subtitle" : 'Sweden is a Scandinavian nation with thousands of coastal islands and'
                                             ' inland lakes, along with vast boreal forests and glaciated mountains.',
                                "buttons" : [
                                    {
                                        "type": "web_url",
                                        "url": "https://en.wikipedia.org/wiki/Sweden",
                                        "title": "Read on Wikipedia"
                                    }
                                ]
                            },
                            {
                                "title": "Trending music in Sweden right now:",
                                "image_url": 'https://i.scdn.co/image/58ce31b40bf6a44849e7678a065a754a9d22e47c',
                                "subtitle": 'Check out the Top 50 songs on Spotify in Sweden.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://open.spotify.com/user/spotifycharts/playlist/37i9dQZEVXbLoATJ81JYXz",
                                        "title": "Listen on Spotify"
                                    }
                                ]
                            },
                            {
                                "title": "30 Swedish movies you must see before you die",
                                "image_url": 'https://www.thelocal.se/userdata/images/article/b8032c48587fc44bec8c458b6'
                                             '2f65bff22e03dd0fd3aa53fa8f760973864e000.jpg',
                                "subtitle": 'To help us grasp the soul of Swedish film, expert Christian Ekvall picks '
                                            'out 30 Swedish movies to see before you die.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://www.thelocal.se/20160824/30-swedish-movies-you-must-see-before-you-die",
                                        "title": "Read More"
                                    }
                                ]
                            }
                        ]
                    }
                },
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Swedish culture",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Translate in Swedish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Swedish quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Pronounce in Swedish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }
        })

    if received_message.lower() == "japanese culture":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "list",
                        "top_element_style": "large",
                        "elements": [
                            {
                                "title": "Japan",
                                "image_url": 'http://japan-magazine.jnto.go.jp/jnto2wm/wp-content/uploads/1608_special'
                                             '_TOTO_main.jpg',
                                "subtitle" : 'Japan (Japanese: 日本 Nippon [ɲippoɴ] or Nihon [ɲihoɴ]; formally 日本国 '
                                             'About this sound Nippon-koku or Nihon-koku, meaning "State of Japan") is'
                                             ' a sovereign island nation in East Asia. Located in the Pacific Ocean',
                                "buttons" : [
                                    {
                                        "type": "web_url",
                                        "url": "https://en.wikipedia.org/wiki/Japan",
                                        "title": "Read on Wikipedia"
                                    }
                                ]
                            },
                            {
                                "title": "Trending music in Japan right now:",
                                "image_url": 'https://i.scdn.co/image/a750303368c5439903c4e9771a95e6361b9195e2',
                                "subtitle": 'Check out the Top 50 songs on Spotify in Japan.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://open.spotify.com/user/spotifycharts/playlist/37i9dQZEVXbKXQ4mDTEBXq",
                                        "title": "Listen on Spotify"
                                    }
                                ]
                            },
                            {
                                "title": "20 epic Japanese movies that every movie buff should watch",
                                "image_url": 'http://www.tasteofcinema.com/wp-content/uploads/2014/12/Battle-Royale-2000.jpg',
                                "subtitle": 'Here are a few of the best Japanese movies to get you started.',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://www.scoopwhoop.com/20-Of-The-Best-Japanese-Movies/#.5edjm82q2",
                                        "title": "Read More"
                                    }
                                ]
                            }
                        ]
                    }
                },
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Japanese culture",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Translate in Japanese",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Japanese quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Pronounce in Japanese",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }
        })

    if received_message.lower() == "korean culture":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "list",
                        "top_element_style": "large",
                        "elements": [
                            {
                                "title": "South Korea",
                                "image_url": 'https://cnet2.cbsistatic.com/img/p3BjmuMZvi7wUPZkMm4Vtg23xqc=/fit-in/57'
                                             '0x0/2015/04/07/350b630d-a2ac-48e0-aacd-860df5574665/chaebols-south-korea.jpg',
                                "subtitle" : 'South Korea, officially the Republic of Korea (abbreviated ROK), is a '
                                             'sovereign state in East Asia, constituting the southern part of the Korean Peninsula.',
                                "buttons" : [
                                    {
                                        "type": "web_url",
                                        "url": "https://en.wikipedia.org/wiki/South_Korea",
                                        "title": "Read on Wikipedia"
                                    }
                                ]
                            },
                            {
                                "title": "Trending music in South Korea right now:",
                                "image_url": 'https://www.allkpop.com/plugin/artisttag_link/img/artist_1484770287_bts.jpg',
                                "subtitle": 'Check out the Top 100 songs on MelOn',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "http://www.melon.com/chart/",
                                        "title": "Listen on MelOn"
                                    }
                                ]
                            },
                            {
                                "title": "20 Korean movies every movie buff should have on their must-watch list",
                                "image_url": 'https://s3.scoopwhoop.com/anj/20/559055314.jpg',
                                "subtitle": '20 Korean movies we felt you should have on your foreign movies bucket list:',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://www.scoopwhoop.com/entertainment/20-best-korean-movies/#.n9vj9evp2",
                                        "title": "Read More"
                                    }
                                ]
                            },
                            {
                                "title": "Learn Korean on YouTube",
                                "image_url": 'http://image.kdramastars.com/data/images/full/216111/professor-oh-shares-her-knowledge-of-korean-language-and-culture-through-sweet-and-tasty-tv.jpg',
                                "subtitle": 'Subscribe to sweetandtastyTV for Korean language lessons, travel vlogs, cultural insight, and everything about Korea!',
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "https://www.youtube.com/user/sweetandtasty",
                                        "title": "Go to YouTube"
                                    }
                                ]
                            }

                        ]
                    }
                },
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": "Korean culture",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Translate in Korean",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Korean quiz",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "Pronounce in Korean",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }
        })

    if received_message.lower() == "/exit translation":
        lang[fbid] = ''
        speech_mode[fbid] = False
        speech[fbid] = ''
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
                    },
                    {
                        "content_type": "text",
                        "title": "/Spanish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Swedish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Japanese",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Korean",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }

                ]
            }
        })

    try:
        if lang[fbid] != '':
            message_text = translate_text(received_message, lang[fbid])
            tts_msg = handle_audio(message_text, fbid)
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=tts_msg)
            pprint(status.json())
            response_msg = json.dumps({
                "recipient": {"id": fbid},
                "message": {
                    "text": message_text
                }
            })
    except:
        print("Exception: lang not set")

    if received_message.lower() == "translate in german":
        lang[fbid] = 'de'
        speech_mode[fbid] = True
        speech[fbid] = 'de'
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
        lang[fbid] = 'fr'
        speech_mode[fbid] = True
        speech[fbid] = 'fr'
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

    if received_message.lower() == "translate in spanish":
        lang[fbid] = 'es'
        speech_mode[fbid] = True
        speech[fbid] = 'es'
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

    if received_message.lower() == "translate in swedish":
        lang[fbid] = 'sv'
        speech_mode[fbid] = True
        speech[fbid] = 'sv'
        print(lang[fbid])
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

    if "translate in japanes" in received_message.lower() :
        lang[fbid] = 'ja'
        speech_mode[fbid] = True
        speech[fbid] = 'ja'
        print(lang[fbid])
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

    if "translate in korean" in received_message.lower() :
        lang[fbid] = 'ko'
        speech_mode[fbid] = True
        speech[fbid] = 'ko'
        print(lang[fbid])
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
                    },
                    {
                        "content_type": "text",
                        "title": "/Spanish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Swedish",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Japanese",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    },
                    {
                        "content_type": "text",
                        "title": "/Korean",
                        "payload": "<STRING_SENT_TO_WEBHOOK>"
                    }
                ]
            }})

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())


def get_started():
    post_message_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token=' + page_access_token
    response_msg = json.dumps({
        "get_started": {
            "payload": "<GET_STARTED_PAYLOAD>"
        }
    })
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    print("Get started")
    pprint(status.json())
