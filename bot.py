import speech_recognition as sr
import pyttsx3

import pywhatkit
from AppKit import *

from helper import configs
from helper import emails, utilities

import requests
import geocoder

import pyjokes
import datetime

import smtplib
from email.message import EmailMessage

### BOT CLASS MODULE ###
class Bot:
    def __init__(self):
        ### GET BOT NAME
        self.__bot_name = configs["BOT_NAME"]

        ### INITIALIZE THE BOT
        self.__ear = sr.Recognizer()
        self.__engine = pyttsx3.init()
        voice = self.__engine.getProperty('voice')
        self.__engine.setProperty('voice', voice.replace("Alex", "samantha"))

        # LOAD ALL DATA FROM FILES
        self.__utilities = utilities if len(utilities) > 0 else ""
        self.__emails = emails if len(emails) > 0 else {}

    # Brief description of bot
    def __str__(self):
        return f"Hello. This is {self.bot_name.upper()}, your virtual assistant."
    
    # Getter method for emails
    @property
    def emails(self):
        return self.__emails
    
    # Getter method for utilities
    @property
    def utilities(self):
        return self.__utilities
    
    # Getter method for bot name
    @property
    def bot_name(self):
        return self.__bot_name

    # Text-to-speech
    def say(self, text):
        self.__engine.say(text)
        self.__engine.runAndWait()
    
    # Get input
    def get_audio_input(self):
        try:
            with sr.Microphone() as stream:
                print('...On listening...')
                src = self.__ear.listen(stream)
                cmd = self.__ear.recognize_google(src)

                return cmd.lower() if cmd != '' and cmd != None else ''

        except:
            raise ValueError()
    
    # Get a list of available utilities
    def get_utilities(self):
        print("__GET UTILITIES__")
        self.say(f"Available utilities are {self.utilities}") if self.utilities != "" else self.say("Sorry, no utilities available")
    
    # Play music based on user's preferences
    def play_music(self):
            print("__STREAMING MUSIC__")
            print("> Please say the name of the song you want to play <")

            song = self.get_audio_input()
            song = song.upper()

            self.say(f"Playing {song} on Youtube")
            print(f"> Current song: {song}")
            pywhatkit.playonyt(song, use_api=True)
    
    # Get data for current weather in specific location
    def get_weather(self, cmd):
        print("__GET WEATHER__")
        # If location is specified, return data for that location
        if 'in' in cmd:
            loc = cmd.split(' ')[-1]
            url = f"https://api.openweathermap.org/data/2.5/weather?q={loc}&appid={configs['WEATHER_API_KEY']}&units=metric"
        # Otherwise, get the location based on location of machine running
        else:
            loc = geocoder.ip('me') 
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={loc.latlng[0]}&lon={loc.latlng[1]}&appid={configs['WEATHER_API_KEY']}&units=metric"

        response = requests.get(url)
        response = response.json()

        self.say(f'Currently, in {response["name"]}, it is {response["main"]["temp"]:.1f} degrees Celcius, with {response["weather"][0]["description"]}.')
    
    # Get jokes
    def get_joke(self):
        print("__GET JOKES__")
        self.say(pyjokes.get_joke())
    
    # Get current time
    def get_time(self):
        print("__GET CURRENT TIME__")
        time = datetime.datetime.now().strftime("%I:%M %p")
        self.say(f"Right now, it is {time}")
    
    # Get today's date
    def get_date(self):
        print("__GET CURRENT DATE__")
        date = datetime.datetime.now().strftime("%B %d, %Y")
        self.say(f"Today's date is {date}")
    
    # Send email
    def send_email(self):
        print("__SEND EMAIL__")

        print("...Getting email information...")
        self.say("Who is the recipient?")
        recipient = self.get_audio_input()

        if recipient not in self.emails:
            self.say("Recipient not found. Do you wish to add to contact list? (YES or NO)")
            option = self.get_audio_input()
            while option != "no":
                if option == "yes":
                    print('>> Redirecting to "add email contact" utility...')
                    self.add_email_contact()
                    self.say("Okay. Let's continue sending the email...")
                    break

                else:
                    self.say("Sorry. Please say YES or NO.")
                    option = self.get_audio_input()
            
            if option == "no":
                self.say(">> Operation cancelled: User chose to not add new contact, therefore cannot send the email")
                return
            
        self.say("What is the email subject?")
        subject = self.get_audio_input()
        self.say("What is the message?")
        message = self.get_audio_input()

        # Initialize an SMTP client
        server = smtplib.SMTP(configs["EMAIL_DOMAIN"], configs["EMAIL_PORT"])
        server.starttls()
        # Make sure to toggle ON 'Less Secure App Access' before login
        server.login(configs["EMAIL_USER"], configs["EMAIL_PWD"])

        # Initialize email object
        email = EmailMessage()
        email["From"] = configs["EMAIL_USER"]
        email["To"] = self.emails[recipient] 
        email["Subject"] = subject
        email.set_content(message)
        
        # Send email
        self.say("Do you want to send this email? (YES or NO)")
        option = self.get_audio_input()
        while option != "no":
            if option == "yes":
                server.send_message(email)
                print(f"Sending email to {self.emails[recipient]}...")
                self.say("Email sent!")
                break
            
        if option == "no":
            self.say(">> Operation cancelled: User chose to not send email")

    # Add email contact
    def add_email_contact(self):
        print("__ADD EMAIL CONTACT__")

        try:
            self.say("What's the name of the contact?")
            name = self.get_audio_input()

            while True:
                correct = input(f"Is the name correct? (y/n) -> {name}: ")
                if correct in ['y', 'Y']:
                    break

                if correct in ['n', 'N']:
                    name = input("Please type in the correct name: ")

                else:
                    print("Please enter y/n or Y/N: ")
            
            self.say("What's the contact's email address? Please spell it out!")
            email_parts = self.get_audio_input()
            email = email_parts.replace(" ", "")
            email = email.replace("at", "@")

            while True:
                correct = input(f"Is the email address correct? (y/n) -> {email}: ")

                if correct in ['y', 'Y']:
                    break

                if correct in ['n', 'N']:
                    email = input("Please type in the correct email address: ")

                else:
                    print("Please enter y/n or Y/N: ")

        except:
            raise ValueError()
        
        # Write new contact to file or edit existing contact
        while True:
            correct = input("Do you want to save this contact? (y/n): ")

            if correct == "n" or correct == "N":
                self.say("Adding contact cancelled.")
                print(">>> Operation cancelled: User chose not to save the contact")
                break

            elif correct == "y" or correct == "Y":
                if name not in self.emails:
                    self.emails[name] = email
                    print(f"Adding new contact...")
                    self.say("Contact added!")
                    break

                else:
                    if self.emails[name] != email:
                        while True:
                            correct = input("This contact name has already been registered. Do you want to overwrite this contact with the new email? (y/n): ")

                            if correct == "n" or correct == "N":
                                self.say("Overwritting contact cancelled.")
                                print(">>> Operation cancelled: User chose not to overwrite this contact")
                                break

                            elif correct == "y" or correct == "Y":
                                self.emails[name] = email
                                print(f"Overwriting existing contact...")
                                self.say("Contact overwritten!")
                                break

                            else:
                                print("Please enter y/n or Y/N: ")
                            
                        break

                    else:
                        self.say("Contact already exists with the provided email")
                        print(">>> Operation cancelled: Contact already exists with the provided email")
                        break

            else:
                print("Please enter y/n or Y/N: ")
    
    # Shutdown tasks to operate
    def shutdown_tasks(self):
        print(">> RUNNING BACKGROUND TASKS BEFORE SHUTDOWN <<")

        # overwrite all emails to email file
        try:
            with open(configs["FILE_EMAILS"], "w") as email_file:
                email_file.write("name,email\n")
                for name, email in self.emails.items():
                    email_file.write(f"{name},{email}\n")

        except:
            print("*** ERROR: Unable to write emails to file")
        
        print("Background tasks completed...")


if __name__ == '__main__':
    bot = Bot()
    print(bot.emails)
    print(bot.utilities)
    print(bot)