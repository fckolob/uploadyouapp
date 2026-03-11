# Overview

This web app allows users to create an account and upload their files.
Each user can manage his files, can upload, download, and delete each file.
 The app implements many safety measures, like limit the file size to 10mb, limit the uploads per hour, implement upload quota limits to prevent server abuse.
The app also implements CSFR attack protection using the CSFR tokens of Django.
Another security measures are virus scanning the uploads, checking the actual MIME type of the uploads to prevent malicious file to be uploaded with a fake name and also implements protection against double extension in files upload.
To prevent hacking by guessing URLs, the app creates unique random identifiers to name the files uploaded.
The app also protects against hacking by require to be logged to access the protected pages and restricting the HTTP methods that can be used in each case.
The user’s information and the information about files are stored in a SQLite database and sensitive information like passwords is hashed before being stored.

The purpose of the app is to explore the implementation of a safe storage that allows users to make a backup of their files following the best practices to avoid danger to the users and admins of the files being corrupted or stolen. Also explore the workflow of this kind of functionality using the Python web framework Django and some useful libraries. 
 
[Software Demo Video](http://youtube.link.goes.here)

# Web Pages

The web pages of the app are: the dashboard, the register page, the login page, the upload page.
If a logged users access the dashboard, he can see all his already uploaded files, the app implements pagination to improve performance and accessibility download them, or delete them. If the user is not logged or registered, he will be redirected to the login page to log or register.
In the dashboard, a logged user can click the upload button to navigate to the upload page to upload new files.


# Development Environment

The was created using Visual Studio Code. 

The app is build using the Django framework of Python. HTML is used for the templates and CSS is used to style the pages.
Libraries used:
Django==6.0.3
asgiref==3.11.1
sqlparse==0.5.5
tzdata==2025.3
python-magic==0.4.27
pyclamd==0.4.0

The asgiref and sqlparse libraries are additional libraries required by Django itself. 
The library python-magic is used to check the actual MIME types of the files to upload and pyclamd is used to handle virus scanning of the files to upload. 



# Useful Websites

https://docs.djangoproject.com/
https://docs.djangoproject.com/en/6.0/ref/files/uploads/

https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Django/Models




# Future Work


* Implement cloud storage using AWS S3 storage.
* Implement user levels, premium and free.
* File encryption. 

