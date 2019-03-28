# triton_notify
A serverless centralized notification system

![alt text](https://travis-ci.com/ryux00/triton_notify.svg?branch=master "Travis Build Info")

---

### Background:
I have several python scripts that notify me over telegram, SMS,email about certain events, like the status of my portfolio, certain work-related notifications, etc.
And each of these tools had their own duplicated code for sending notifications. This was not ideal since:
* Code was duplicated
* Any changes in APIs would have to be coded in multiple locations
* No centralized logging

I made this tool to solve this problem by creating a centralized API that these scripts can use to send notifications.
This is based on flask and is designed to mainly run on AWS lambda but since this is a regular flask app this can be run anywhere).
[Zappa](https://github.com/Miserlou/Zappa) is used for deployments to lambda.


