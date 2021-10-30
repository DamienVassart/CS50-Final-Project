# MASTERPASS
###### A Web-Based Password Vault using Flask

#### Video Demo: [View on Youtube](https://youtu.be/cys8sAto3NE)
#### Description:

This is my personnal project for [CS50](https://online-learning.harvard.edu/course/cs50-introduction-computer-science?delta=0)<br>
This web app allows you to manage your online accounts logins and passwords in a reasonably secure way. It comes with **AES encryption** to protect your sensitive data.


#### The Technology behind it

The Back-end side is written in **Python**, using the **Flask** framework.

All the data is stored in **SQLite** databases:

- A database storing all users, with their username, their master password hash and their account settings.
- For each user, a database is created to store his/her personnal data. All the sensitive information is encrypted on-the-fly with [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) prior to be inserted to the database.

The Front-end side uses some **JavaScript**:

- To randomly generate passwords according to the user's preferences (character classes, length).
- To show/hide credentials and to copy them to the clipboard.

The CSS makes the user interface **responsive** so that you can use it on any device.

#### Features

Herebelow are listed the main features:

- Password Generator: dont't blow your mind anymore by trying to find strong passwords; let the app generate them for you, following the rules you define (length, character range,...).
- Summary: on the home page, you will have a summary showing you if there are any weak or duplicate passwords in your database, so that you can change them whenever you want.
- Password Strength Calculator: for every password you store within the app, it will let you know how strong this password is by calculating its [entropy](https://en.wikipedia.org/wiki/Password_strength); all the weak and duplicates passwords will be brought to your attention so that you can change them when needed.
- Secure Notes: in addition to storing your login credentials, the app also allows you to add some personnal notes to each entry.

#### Requirements and Dependencies:

Works with `Python 3.6+`

The following libraries and frameworks are needed for the app to work properly:

- [pip](https://pip.pypa.io/en/stable/installation/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/installation/)
- [Flask-Session](https://flask-session.readthedocs.io/en/latest/)
- [CS50 Library for Python](https://cs50.readthedocs.io/libraries/cs50/python/)
- [Cryptography](https://cryptography.io/en/latest/)


You will also need to enable `Javascript` in your web browser.

#### Running

Once all of the above is installed, you can run the app locally by executing the following:

##### Bash:
```
$ export FLASK_APP=application
$ flask run
```

##### CMD:
```
> set FLASK_APP=application
> flask run
```

##### Powershell:
```
> $env:FLASK_APP = "application"
> flask run
```

If you are facing any issue or notice any bug, feel free to contact me or to send a Pull Request on GitHub.