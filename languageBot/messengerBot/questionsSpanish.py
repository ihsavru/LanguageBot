import random

def generate_question_spanish():
    list = [
        {
            'question' : "What comes after sunday?",
            'answer': "lunes"
        },
        {
            'question' : "What is 5+4?",
            'answer' : "nueve"
        },
        {
            'question': "How would you say 'red' in Spanish?",
            'answer': "rojo"
        },
        {
            'question': "What is father called in Spanish?",
            'answer': "padre"
        },
        {
            'question': "Christmas comes in?",
            'answer': "diciembre"
        },
        {
            'question': "How will you ask someone if they speak English?",
            'answer': "hablas ingl\xc3\xa9s?"
        },
        {
            'question': "'Where' in Spanish?",
            'answer': "donde"
        },
        {
            'question': "How do you say thank you in Spanish?",
            'answer': "gracias"
        },
        {
            'question': "How will you say 'please' in Spanish?",
            'answer': "por favor"
        },
        {
            'question': "'No' in Spanish is?",
            'answer': "no"
        },
        {
            'question': "'North' is called?",
            'answer': "norte"
        },
        {
            'question' : "How will you say 'south' in Spanish?",
            'answer' : "sur"
        },
        {
            'question': "'East' is called?",
            'answer': "este"
        },
        {
            'question': "'West' is called?",
            'answer': "oeste"
        },
        {
            'question': "What will you call a 'spoon'?",
            'answer': "cuchara"
        },
        {
            'question': "'Spanish' in Spanish?",
            'answer': "espa\xc3\xb1ol"
        },
        {
            'question': "Okay. Suppose you fell in love with a Spanish guy or a girl. How will you tell them if you love them?",
            'answer': "te amo"
        },
        {
            'question': "How is 'coffee' known as in Spanish?",
            'answer': "caf\xc3\xa9"
        },
        {
            'question': "What is a 'teacher' known as in Spanish?",
            'answer': "profesor"
        },
        {
            'question': "What is an 'engineer' known as in Spanish?",
            'answer': "ingeniero"
        },
        {
            'question': "What is 'beautiful' called in Spanish?",
            'answer': "hermosa"
        },

    ]
    return random.choice(list)