from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json, requests, random
from pprint import pprint
from googletrans import Translator
from questions import generate_question
from datetime import datetime

page_access_token = '<page_access_token>'

lang = {}
quiz_mode = {}
quiz = {}
answer = {}
score = {}
count = {}


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
                    "type": "web_url",
                    "title": "Source Code",
                    "url": "https://github.com/ihsavru/LanguageBot",
                    "webview_height_ratio": "full"
                },
                {
                    "title": "About",
                    "type": "postback",
                    "payload": "ABOUT_PAYLOAD"
                }
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
    if translator.detect(received_message).lang == 'en':
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

def handle_postbacks(fbid, postback):
    if postback['payload'] == '<GET_STARTED_PAYLOAD>':
        response_msg = json.dumps(
            {
                "recipient": {"id": fbid},
                "message": {
                    "text": "Welcome to Language Bot! We are currently in the development phase. If you're seeing this,"
                            " it means you have been added as a tester :) Thankyou for messaging us. To begin learning,"
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
                        }
                    ]}
            })
    if postback['payload'] == 'ABOUT_PAYLOAD':
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Hi! I am a demo bot written in Python (Django). I help you to learn languages. Currently"
                        " I only know German, French, Spanish and Swedish.",
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
                    }
                ]
            }})
    return response_msg

def post_facebook_message(fbid, fb_message):

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
    try:
        if lang[fbid] != '':
            message_text = translate_text(received_message, lang[fbid])
            response_msg = json.dumps({
                "recipient": {"id": fbid},
                "message": {
                    "text": message_text
                }
            })
    except:
        print("Exception: lang not set")


    if received_message.lower() == "/about bot":
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "Hi! I am a demo bot written in Python (Django). I help you to learn languages. Currently"
                        " I only know German, French, Spanish and Swedish.",
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

    if received_message.lower() == "/spanish":
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
                    }
                ]
            }})

    if received_message.lower() == "/swedish":
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
                    }
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

    try:
        if quiz[fbid] == True:
            response_msg = check_answer(received_message, fbid)
    except:
        print("Exception: quiz not true")

    if "test my german" in received_message.lower():
        global quiz_mode
        quiz_mode[fbid] = 'de'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "What is a table called in German?"
            }
        })
        global quiz
        global answer
        quiz[fbid] = True
        answer[fbid] = "table"

    if "test my french" in received_message.lower():
        global quiz_mode
        quiz_mode[fbid] = 'fr'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "What is a chair called in French?"
            }
        })
        global quiz
        global answer
        quiz[fbid] = True
        answer[fbid] = "chair"

    if "test my spanish" in received_message.lower():
        global quiz_mode
        quiz_mode[fbid] = 'es'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "How many days are there in December?"
            }
        })
        global quiz
        global answer
        quiz[fbid] = True
        answer[fbid] = "thirty one"

    if "test my swedish" in received_message.lower():
        global quiz_mode
        quiz_mode[fbid] = 'sv'
        response_msg = json.dumps({
            "recipient": {"id": fbid},
            "message": {
                "text": "What apple called in Swedish?"
            }
        })
        global quiz
        global answer
        quiz[fbid] = True
        answer[fbid] = "apple"

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
                    }
                ]
            }
        })
        global  quiz, quiz_mode
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
                    }
                ]
            }
        })

    if received_message.lower() == "translate in german":
        global lang
        lang[fbid] = 'de'
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
        lang[fbid] = 'fr'
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
        global lang
        lang[fbid] = 'es'
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
        global lang
        lang[fbid] = 'sv'
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

    if received_message.lower() == "/exit translation":
        global lang
        lang[fbid] = ''
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
