import random

def generate_question():
    list = [
        {
            'question' : "What comes after sunday?",
            'answer': "Montag"
        },
        {
            'question' : "What is 5+4?",
            'answer' : "Neun"
        },
        {
            'question': "How would you say 'red' in German?",
            'answer': "Rot"
        },
        {
            'question': "What is father called in German?",
            'answer': "Vater"
        },
        {
            'question': "Christmas comes in?",
            'answer': "Dezember"
        },
        {
            'question': "What is 'I speak' in German?",
            'answer': "ich spreche Deutsch"
        },

    ]
    return random.choice(list)