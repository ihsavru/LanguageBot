import random

def generate_question_german():
    list = [
        {
            'question' : "What comes after sunday?",
            'answer': "montag"
        },
        {
            'question' : "What is 5+4?",
            'answer' : "neun"
        },
        {
            'question': "How would you say 'red' in German?",
            'answer': "rot"
        },
        {
            'question': "What is father called in German?",
            'answer': "vater"
        },
        {
            'question': "Christmas comes in?",
            'answer': "dezember"
        },
        {
            'question': "How will you ask someone if they speak English?",
            'answer': "sprechen sie englisch?"
        },
        {
            'question': "'Where' in German?",
            'answer': "wo"
        },
        {
            'question': "How do you say thank you in German?",
            'answer': "danke"
        },
        {
            'question': "How will you say 'please' in German?",
            'answer': "bitte"
        },
        {
            'question': "'No' in German is?",
            'answer': "nein"
        },
        {
            'question': "'North' is called?",
            'answer': "nord"
        },
        {
            'question' : "How will you say 'south' in German?",
            'answer' : "s\xc3\xbcd"
        },
        {
            'question': "'East' is called?",
            'answer': "ost"
        },
        {
            'question': "'West' is called? This is easy ;)",
            'answer': "west"
        },
        {
            'question': "What will you call a 'spoon'?",
            'answer': "l\xc3\xb6ffel"
        },
        {
            'question': "'German' in German?",
            'answer': "deutsche"
        },
        {
            'question': "Okay. Suppose you fell in love with a German guy or a girl. How will you tell them if you love them?",
            'answer': "ich liebe dich"
        },
        {
            'question': "How is 'coffee' known as in German?",
            'answer': "kaffee"
        },
        {
            'question': "What is a 'teacher' known as in German?",
            'answer': "lehrer"
        },
        {
            'question': "What is an 'engineer' known as in German?",
            'answer': "ingenieur"
        },
        {
            'question': "What is 'beautiful' called in German?",
            'answer': "sch\xc3\xb6n"
        },


    ]
    return random.choice(list)