### Steps to run

Ensure that python and pip are installed then to install the required packages run 
`pip install -r requirements.txt`.

Create a `.env` file for storing required credentials. If the RabbitMQ broker is on the same machine then let it be as follows:
```
username = guest
password = guest
ip_address = localhost
```


Otherwise, create user and set password on the machine running RabbitMQ broker using `rabbitmqctl add_user <username> <password>`. Grant the user permissions by running 
`rabbitmqctl set_permissions -p / <username> ".*" ".*" ".*"`  
Update the `.env` file accordingly.

Then the scripts for the youtubeserver, youtuber, user can be run as follows:
1. Start the 'youtubeserver' `python youtubeserver.py`
2. A Youtuber can upload a video using `python youtuber.py <youtuberName> <videoTitle>` (the video title can have spaces but not the Youtuber's username)
3. Users can (un)subsrcribe to Youtubers by `python user.py <username> u/s <youtuberName>` or simply login by `python user.py <username>`.