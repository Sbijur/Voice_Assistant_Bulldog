from __future__ import print_function
import datetime
from datetime import timedelta
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import os
import speech_recognition as sr
from gtts import gTTS
import pyttsx3
import subprocess
import pytz
import sys
import webbrowser
SCOPES = ['https://www.googleapis.com/auth/calendar']
DAYS=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
MONTHS=["january","february","march","april","may","june","july","august","september","october","november","december"]
DAY_EX=["th","rd","st","nd"]
NOTE_STRS=["note","open notes","write this down"]
CAL=["what do i have","do i have any plans","am i busy","schedule"]
OPBR=["search","google"]
SETEVENT=["set event for"]
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.setProperty("rate",128)
    engine.runAndWait()
    
def get_audio():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
        said=""
        try:
            said=r.recognize_google(audio)
            print("USER:"+said)
        except Exception as e:
            print('Please repeat')
            
    return said
#text=get_audio()
#if "hello" in text:
#    speak("Hello There")
    

def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_events(day,service):
    date=datetime.datetime.combine(day,datetime.datetime.min.time())
    end_date=datetime.datetime.combine(day,datetime.datetime.max.time())
    utc=pytz.UTC
    date=date.astimezone(utc)
    end_date=end_date.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),timeMax=end_date.isoformat(),
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        speak(start+"EVENT:")
        speak(event['summary'])
        print(start, event['summary'])

def get_date(text):
    text=text.lower()
    today=datetime.date.today()
    if(text.count("today")>0):
        return today
    day=-1
    day_of_week=-1
    month=-1
    year=today.year
    
    for word in text.split():
        if word in MONTHS:
            month=MONTHS.index(word)+1
        elif word in DAYS:
            day_of_week=DAYS.index(word)
        elif word.isdigit():
            day=int(word)
        else:
            for ex in DAY_EX:
                found=word.find(ex)
                if found>0:
                    try:
                        day=int(word[:found])
                    except:
                        pass
    if month<today.month and month!=-1:
        year=year+1
    if day<today.day and month==-1 and day!=-1:
        month=month+1
    if month==-1 and day==-1 and day_of_week!=-1:
        current_day_of_week=today.weekday()
        dif=day_of_week-current_day_of_week
        if dif<0:
            dif=dif+7
            if text.count("next")>=1:
                dif=dif+7
        return today+datetime.timedelta(dif)
    return datetime.date(year,month,day)
def note(text):
    date=datetime.datetime.now()
    file_name=str(date).replace(":","-")+"-note.txt"
    with open(file_name,"w") as f:
        f.write(text)
    subprocess.Popen(["notepad.exe",file_name])
        
def set_time(time):
    if time.count(" p.m.")>0:
        time=time.replace(" p.m.", ":00")
        T=datetime.datetime.strptime(time,"%H:%M:%S")
        T=T+timedelta(hours=12)
    else:
        time=time.replace(" a.m.", ":00")
        T=datetime.datetime.strptime(time,"%H:%M:%S")
    T=datetime.datetime.time(T)
    print("Time",T)
    return(T)

def set_event(text,service):
    #format = '%Y-%m-%d-T%I:%M%p+05:30' # The format

    speak("Enter title of event")
    s=get_audio()
    speak("Enter description of event")
    e=get_audio()
    speak("Enter location of event")
    l=get_audio()
    speak("Enter starting time")
    time=get_audio()
    stime=set_time(time)
    speak("Enter ending time")
    time=get_audio()
    etime=set_time(time)
    c1=datetime.datetime.combine(text,stime)
    c2=datetime.datetime.combine(text,etime)
    event = {
  'summary':s,
  'location':l,
  'description':e,
  'start': {
    'dateTime':c1.strftime("%Y-%m-%dT%H:%M:%S"),
    'timeZone': 'Asia/Kolkata',
  },
  'end': {
    'dateTime':c2.strftime("%Y-%m-%dT%H:%M:%S"),
    'timeZone': 'Asia/Kolkata',
  },
  'recurrence': [

  ],
  'attendees': [

  ],
  'reminders': {
    'useDefault': False,
  },
}
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(event.get('htmlLink'))


    
speak("Hello there")
Wake="hey bulldog"
service=authenticate_google()
while True:
    text=get_audio()
    if text.lower().count(Wake)>0:
        speak("Hello I am bulldog What can i do for you")
        while True:
            text=get_audio()          
            for phrase in CAL:
                if phrase in text.lower():
                    date=get_date(text)
                    if date:
                        get_events(date,service)
                    else:
                        speak("Please Try again")
            for phrase in SETEVENT:
                if phrase in text.lower():
                    date=get_date(text)
                    if date:
                        set_event(date,service)
                    else:
                        print("Try again")

            for phrase in NOTE_STRS:
                if phrase in text:
                    speak("Note Maker Opened")
                    entry=get_audio()
                    if entry!="":
                        note(entry)
                        speak("Entry has been made!")
        
            for phrase in OPBR:
                if phrase in text.lower():
                    for word in text.lower().split():
                        if(word not in OPBR):
                            webbrowser.open("https://www.google.com/search?q="+word+"&sxsrf=AOaemvJLVOb8NLE4zLzuaytqwGTfUvWzKg%3A1636198233043&source=hp&ei=WWeGYaEM59bk5Q-hy4ewCQ&iflsig=ALs-wAMAAAAAYYZ1adk-BYle5EF3Ju1r_aRLAROur9io&oq=youtube&gs_lcp=Cgdnd3Mtd2l6EAMyDQguEMcBEKMCECcQkwIyBAgjECcyBAgjECcyBAgAEEMyBQgAEJECMgUIABCRAjIFCAAQkQIyBwgAELEDEEMyBAgAEEMyBAgAEEM6BwgjEOoCECc6BQguEIAEOggILhCABBCxAzoOCC4QgAQQsQMQxwEQ0QM6CAgAEIAEELEDOgsIABCABBCxAxCDAToHCC4QsQMQQzoKCAAQgAQQhwIQFFCdCVjPFmDCGGgBcAB4AIABtgGIAfMHkgEDMC43mAEAoAEBsAEK&sclient=gws-wiz&ved=0ahUKEwjhnNez0YP0AhVnK7kGHaHlAZYQ4dUDCAc&uact=5")
            
            if(text.lower()=="stop") or (text.lower()=="exit")or(text.lower()=="close"):
                speak("Bulldog Closing thank you for using Bulldog on Python")
                sys.exit()