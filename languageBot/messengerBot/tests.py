from django.test import TestCase
from views import translate_text, generate_question

# Create your tests here.

class testLanguageChange(TestCase):
    def testTranslateText(self):
        self.assertEqual(translate_text('fr', 'Hello'), 'Bonjour', msg="Wrong translation!")
        self.assertEqual(translate_text('de', 'Hello'), 'Hallo', msg="Wrong translation!")
        self.assertEqual(translate_text('es', 'Hello'), 'Hola', msg="Wrong translation!")

class testQuiz(TestCase):
    def testCorrectAnswer(self):
        question = generate_question()


