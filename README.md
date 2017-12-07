# LanguageBot
A conversational bot along with GUI interactions which enables the user to learn a specific language by interacting with the bot. The project is built using Django framework for messenger platform. Currently, the bot only supports teaching German and French.

## Requirements
* A Facebook app and it's page
* Django
* Ngrok

## Set up

### 1. Install Django
```$ pip install django==1.10```

### 2. Install Ngrok
```$ npm install ngrok```

### 3. Clone the project
```$ git clone https://github.com/ihsavru/LanguageBot.git```

### 4. Create a Facebook app and it's page
To do this, lets head to the [Facebook developer site](https://developers.facebook.com/), create a new app and fill out the relevant details to get our App ID. You can select "Apps for Messenger" as its category.  
Next, create a Facebook page for your app.
Replace **<page_access_token>** in _messengerBot/views.py_ with your Facebook page's access token (which will be given on your app's dashboard)

### 4. Set up Webhook
First, enter into the main project directory using:  
```$ cd LanguageBot```  
Now enter the _languageBot_ directory using:  
```$ cd languageBot```  
Run the development server:  
```$ python manage.py runserver```  
Run ngrok using:  
```$ ngrok http 8000```  
![](https://i.imgur.com/76qPYZn.png)  
 Now any outside computer can reach your localhost server at ```https://fac8049c.ngrok.io``` (this can change everytime you run ngrok) which means so can Facebook.

So lets set up the webhook for Facebook. Go to your app dashboard and click on Messenger. Click on "Setup Webhooks" right below "Token Generation" and fill the details:  
  
**Callback URL:** ```https://fac8049c.ngrok.io/messengerBot/21975e0a3c7ab17aa37124158bbda569af363d15eacb576e0```
  
**Verify Token** can be anything. Replace this Verify Token with **<verify_token>** in _messengerBot/views.py_
  
Select **messages, messaging_postbacks** in Subscription Fields. Now click on "Verify and Save" and your webhook is setup. You should see the green tick. Next, select the page you want your app to be subscribed to and click on Subscribe.

Now you're bot is ready to talk! Go ahead and send a message to your Facebook page.
