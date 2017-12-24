import random

def generate_question(lang):
    list = [
        {
            'question' : "What comes after sunday?",
            'answer': "monday"
        },
        {
            'question': "How would you say 'red' in "+lang+"?",
            'answer': "red"
        },
        {
            'question': "What is father called in "+lang+"?",
            'answer': "father"
        },
        {
            'question': "Christmas comes in?",
            'answer': "december"
        },
        {
            'question': "How will you ask someone if they speak English?",
            'answer': "do you speak english"
        },
        {
            'question': "'Where' in "+lang+"?",
            'answer': "where"
        },
        {
            'question': "How do you say thank you in "+lang+"?",
            'answer': "thank you"
        },
        {
            'question': "How will you say 'please' in "+lang+"?",
            'answer': "please"
        },
        {
            'question': "'No' in "+lang+" is?",
            'answer': "no"
        },
        {
            'question': "'North' is called?",
            'answer': "north"
        },
        {
            'question' : "How will you say 'south' in "+lang+"?",
            'answer' : "south"
        },
        {
            'question': "'East' is called?",
            'answer': "east"
        },
        {
            'question': "'West' is called?",
            'answer': "west"
        },
        {
            'question': "What will you call a 'spoon'?",
            'answer': "spoon"
        },
        {
            'question': lang+ " in " + lang+ " is?",
            'answer': lang
        },
        {
            'question': "Okay. Suppose you fell in love with a "+lang+" guy or a girl. How will you tell them if you love them?",
            'answer': "i love you"
        },
        {
            'question': "How is 'coffee' known as in "+lang+"?",
            'answer': "coffee"
        },
        {
            'question': "What is a 'teacher' known as in "+lang+"?",
            'answer': "teacher"
        },
        {
            'question': "What is an 'engineer' known as in "+lang+"?",
            'answer': "engineer"
        },
        {
            'question': "What is 'beautiful' called in "+lang+"?",
            'answer': "beautiful"
        },
        {
            'question': "What is 'movie' called in "+lang+"?",
            'answer': "movie"
        },
        {
            'question': "How do you say 'happy' in "+lang+"?",
            'answer': "happy"
        },
        {
            'question': "How do you say 'cold' in "+lang+"?",
            'answer': "cold"
        },
        {
            'question': "How is 'pizza' known as in "+lang+"?",
            'answer': "pizza"
        },
        {
            'question': "How is 'burger' known as in "+lang+"?",
            'answer': "burger"
        },
        {
            'question': "What is 'mother' called in "+lang+"?",
            'answer': "mother"
        },
        {
            'question': "What is 'sister' called in "+lang+"?",
            'answer': "sister"
        },
        {
            'question': "What is 'brother' called in "+lang+"?",
            'answer': "brother"
        },
        {
            'question': "How is 'sorry' said in "+lang+"?",
            'answer': "sorry"
        },
        {
            'question': "What is 'water' called in "+lang+"?",
            'answer': "water"
        },
        {
            'question': "What is 'restaurant' called in "+lang+"?",
            'answer': "restaurant"
        },
        {
            'question': "What is 'hotel' called in "+lang+"?",
            'answer': "hotel"
        },
        {
            'question': "How do you say 'I am hungry' in "+lang+"?",
            'answer': "I am hungry"
        },
        {
            'question': "How do you say 'hot' in "+lang+"?",
            'answer': "hot"
        },
        {
            'question': "How do you say 'I am tired' in "+lang+"?",
            'answer': "I am tired"
        },
        {
            'question': "How do you say 'friend' in "+lang+"?",
            'answer': "friend"
        },
        {
            'question': "How do you say 'bye' in "+lang+"?",
            'answer': "bye"
        },
        {
            'question': "What is a 'hospital' called in "+lang+"?",
            'answer': "hospital"
        },
        {
            'question': "What is a 'doctor' called in "+lang+"?",
            'answer': "doctor"
        },
        {
            'question': "How do you say 'right' in "+lang+"?",
            'answer': "right"
        },
        {
            'question': "How do you say 'left' in "+lang+"?",
            'answer': "left"
        },
    ]
    return random.choice(list)
