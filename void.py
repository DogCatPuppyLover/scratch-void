import requests
import re
import time
from bs4 import BeautifulSoup
import json

# Get user info
print("Enter your username:")
username = input()

print("Enter your password:")
password = input()

with requests.Session() as s:

    # https://github.com/CubeyTheCube/scratchclient/tree/main/scratchclient
    headers = {
        "x-csrftoken": "a",
        "x-requested-with": "XMLHttpRequest",
        "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
        "referer": "https://scratch.mit.edu",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    }
    data = json.dumps({"username": username,"password": password,"useMessages": "true"})

    # Login with user info
    r = s.post("https://scratch.mit.edu/login/", data=data, headers=headers)
    print(r.status_code)
    session_id = re.search('"(.*)"', r.headers["Set-Cookie"]).group()
    token = r.json()[0]["token"]

    # Set headers
    headers = {
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchlanguage=en;permissions=%7B%7D;",
            "referer": "https://scratch.mit.edu"
    }

    # Get CSRF token
    r = s.get("https://scratch.mit.edu/csrf_token/", headers=headers)
    print(r.status_code)
    csrf_token = re.search(
            "scratchcsrftoken=(.*?);", r.headers["Set-Cookie"]
    ).group(1)

    # Update headers with the CSRF token, token, and cookies

    headers = {
        "x-csrftoken": csrf_token,
        "X-Token": token,
        "x-requested-with": "XMLHttpRequest",
        "Cookie": "scratchcsrftoken="
        + csrf_token
        + ";scratchlanguage=en;scratchsessionsid="
        + session_id
        + ";",
        "referer": "https://scratch.mit.edu",
    }

    print(csrf_token)

    # Get session data
    session = s.get("https://scratch.mit.edu/session/", headers=headers)
    print(session.status_code)
    print(session.text)
    
    wait = 120
    
    while True:
        html = s.get("https://scratch.mit.edu/site-api/comments/user/" + username + "/?page=1").text
        soup = BeautifulSoup(html, "html.parser")
        comments = soup.find_all("div", class_="comment")
        if (len(comments) == 0):
            wait = wait * 2
        for i in comments:
            data = json.dumps({"id":i["data-comment-id"]})
            s.post("https://scratch.mit.edu/site-api/comments/user/" + username + "/del/", data=data, headers=headers)
            print("#" + i["data-comment-id"])
            print("@" + i.find(class_="name").text.strip() + ":")
            print(" ".join(i.find(class_="content").text.split()))
            print("")
            wait = wait / 2
        
        wait = max(3.75, min(wait, 120))
        
        time.sleep(wait)