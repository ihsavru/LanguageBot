import random

def generate_question_swedish():
    list = [
        {
            'question' : "What comes after sunday?",
            'answer': "m\xc3\xa5ndag"
        },
        {
            'question' : "What is 5+4?",
            'answer' : "nio"
        },
        {
            'question': "How would you say 'red' in Swedish?",
            'answer': "r\xc3\xb6d"
        },
        {
            'question': "What is father called in Swedish?",
            'answer': "far"
        },
        {
            'question': "Christmas comes in?",
            'answer': "december"
        },
        {
            'question': "How will you ask someone if they speak English?",
            'answer': "pratar du engelska?"
        },
        {
            'question': "'Where' in Swedish?",
            'answer': "var"
        },
        {
            'question': "How do you say thank you in Swedish?",
            'answer': "tack"
        },
        {
            'question': "How will you say 'please' in Swedish?",
            'answer': "sn\xc3\xa5lla du"
        },
        {
            'question': "'No' in Swedish is?",
            'answer': "nej"
        },
        {
            'question': "'North' is called?",
            'answer': "norr"
        },
        {
            'question' : "How will you say 'south' in Swedish?",
            'answer' : "s\xc3\xb6der"
        },
        {
            'question': "'East' is called?",
            'answer': "\xc3\xb6ster"
        },
        {
            'question': "'West' is called?",
            'answer': "v\xc3\xa4ster"
        },
        {
            'question': "What will you call a 'spoon'?",
            'answer': "sked"
        },
        {
            'question': "'Swedish' in Swedish?",
            'answer': "svenska"
        },
        {
            'question': "Okay. Suppose you fell in love with a Swedish guy or a girl. How will you tell them if you love them?",
            'answer': "jag \xc3\xa4lskar dig"
        },
        {
            'question': "How is 'coffee' known as in Swedish?",
            'answer': "kaffe"
        },
        {
            'question': "What is an 'engineer' known as in Swedish?",
            'answer': "ingenj\xc3\xb6r"
        },
        {
            'question': "What is 'beautiful' called in Swedish?",
            'answer': "sk\xc3\xb6n"
        },

    ]
    return random.choice(list)