import random

def generate_question_french():
    list = [
        {
            'question' : "What comes after sunday?",
            'answer': "lundi"
        },
        {
            'question' : "What is 5+4?",
            'answer' : "neuf"
        },
        {
            'question': "How would you say 'red' in French?",
            'answer': "rouge"
        },
        {
            'question': "What is father called in French?",
            'answer': "p\xc3\xa8re"
        },
        {
            'question': "Christmas comes in?",
            'answer': "d\xc3\xa9cembre"
        },
        {
            'question': "How will you ask someone if they speak English?",
            'answer': "parlez vous anglais?"
        },
        {
            'question': "'Where' in French?",
            'answer': "o\xc3\xb9"
        },
        {
            'question': "How do you say thank you in French?",
            'answer': "merci"
        },
        {
            'question': "How will you say 'please' in French? (formal)",
            'answer': "s'il vous plait"
        },
        {
            'question': "'No' in French is?",
            'answer': "non"
        },
        {
            'question': "'North' is called?",
            'answer': "nord"
        },
        {
            'question' : "How will you say 'south' in French?",
            'answer' : "sud"
        },
        {
            'question': "'East' is called?",
            'answer': "est"
        },
        {
            'question': "'West' is called? This is easy ;)",
            'answer': "ouest"
        },
        {
            'question': "What will you call a 'spoon'?",
            'answer': "cuill\xc3\xa8re"
        },
        {
            'question': "'French' in French?",
            'answer': "fran\xc3\xa7ais"
        },
        {
            'question': "Okay. Suppose you fell in love with a French guy or a girl. How will you tell them if you love them?",
            'answer': "je t'aime"
        },
        {
            'question': "How is 'coffee' known as in French?",
            'answer': "caf\xc3\xa9"
        },
        {
            'question': "What is a 'teacher' known as in French?",
            'answer': "prof"
        },
        {
            'question': "What is an 'engineer' known as in French?",
            'answer': "ing\xc3\xa9nieur"
        },


    ]
    return random.choice(list)