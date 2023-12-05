import isodate
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pymongo
import mysql.connector
import streamlit as st
from bson import ObjectId
from datetime import datetime
def convert_iso8601_to_hhmmss(duration):
    # the built-in Python libraries
    duration_obj = isodate.parse_duration(duration)

    # Extract H, M, and S
    hours = duration_obj.days * 24 + duration_obj.seconds // 3600
    minutes = (duration_obj.seconds % 3600) // 60
    seconds = duration_obj.seconds % 60

    # Format the duration in HH:MM:SS
    formatted_duration = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    return formatted_duration

def list_to_string(data):
    if isinstance(data, list):
        return ','.join(map(str, data))
    return data

def display_channel_details(channel_id):
    channel_data = channel(channel_id)
    st.write("Channel Details:")
    st.write(channel_data)


def extract_and_transform(channel_id):
    data = main(channel_id)
    st.write("Extracted Data:")
    st.write(data)

def channel(channel_id):
    api_key = 'AIzaSyAKfGIwV1enQ037ym23bWBmJiP0yR3ceyk'
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    try:
        response = request.execute()

        if 'items' in response and response['items']:
            channel_data = {
                'channel_id': channel_id,
                'Channel_Name': response['items'][0]['snippet']['title'],
                'Subscription_Count': int(response['items'][0]['statistics']['subscriberCount']),
                'Channel_Views': int(response['items'][0]['statistics']['viewCount']),
                'Channel_Description': response['items'][0]['snippet']['description'],
                'channel_playlist': response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            }
            return channel_data
        else:
            print("No 'items' found in the response or response is empty.")
            return None  # handling the error

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return None  # handling the HTTP error


def get_video_ids(channel_id):
    api_key = 'AIzaSyAKfGIwV1enQ037ym23bWBmJiP0yR3ceyk'
    youtube = build('youtube', 'v3', developerKey=api_key)

    video_IDs = []
    video_request = youtube.channels().list(id=channel_id, part='contentDetails').execute()

    if 'items' in video_request and video_request['items']:  # Checking if 'items' key exists and is not empty
        playlist_id = video_request['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        next_page_token = None

        while True:
            video_response = youtube.playlistItems().list(playlistId=playlist_id,
                                                          part='snippet',
                                                          maxResults=500,
                                                          pageToken=next_page_token).execute()
            for item in video_response.get('items', []):
                video_IDs.append(item['snippet']['resourceId']['videoId'])

            next_page_token = video_response.get('nextPageToken')
            if not next_page_token:
                break
    else:
        print("No 'items' found in the video request or response is empty.")

    return video_IDs


def video(video_id):
    api_key = "AIzaSyAKfGIwV1enQ037ym23bWBmJiP0yR3ceyk"
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()

    # Extract the published datetime string from the response
    published_at_str = response['items'][0]['snippet']['publishedAt']

    # Convert the string to a Python datetime object
    published_at = datetime.strptime(published_at_str, '%Y-%m-%dT%H:%M:%SZ')

    # Format the datetime to fit MySQL datetime format
    formatted_published_at = published_at.strftime('%Y-%m-%d %H:%M:%S')

    video_data = {
        'Channel_id': response['items'][0]['snippet']['channelId'],
        'Video_Id': response['items'][0]['id'],
        'Video_Name': response['items'][0]['snippet']['title'],
        'Video_Description': response['items'][0]['snippet']['description'],
        'PublishedAt': formatted_published_at,  # Use the formatted datetime string
        'View_Count': int(response['items'][0]['statistics']['viewCount']),
        'Like_count': int(response['items'][0]['statistics']['likeCount']),
        'Favorite_count': int(response['items'][0]['statistics']['likeCount']),
        'Comment_Count': int(response['items'][0]['statistics']['commentCount']),
        'Duration': convert_iso8601_to_hhmmss(response['items'][0]['contentDetails']['duration']),
        'Thumbnail': response['items'][0]['snippet']['thumbnails']['default']['url']
    }

    return video_data


def get_comment_ids(video_id):
    api_key = "AIzaSyAKfGIwV1enQ037ym23bWBmJiP0yR3ceyk"
    youtube = build('youtube', 'v3', developerKey=api_key)

    comment_ids = []
    next_page_token = None
    total_comments = 0

    while True:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,  # Fetching up to 100 comments per page
            pageToken=next_page_token if next_page_token else ''
        )

        response = request.execute()

        print(f"Video ID: {video_id}, Response: {response}")  # Add this line to track the response received

        for item in response['items']:
            comment_ids.append(item['id'])
            total_comments += 1

            if total_comments >= 10:
                return comment_ids[:10]  # Return up to 10 comment IDs per video

        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    return comment_ids[:10]  # If fewer than 10 comments are available return all available comments


def comment(comment_id):
    api_key = "AIzaSyAKfGIwV1enQ037ym23bWBmJiP0yR3ceyk"
    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        request = youtube.comments().list(
            part="snippet",
            parentId=comment_id
        )
        response = request.execute()


        if 'items' in response and len(response['items']) > 0:
            comment_published_at_str = response['items'][0]['snippet']['updatedAt']

            # Format the Comment_PublishedAt to match MySQL datetime format
            formatted_comment_published_at = datetime.strptime(comment_published_at_str, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')

            comment_data = {
                'Channel_id': response['items'][0]['snippet']['channelId'],
                'comment_id': response['items'][0]['id'],
                'Comment_Author': response['items'][0]['snippet']['authorChannelId'],
                'Comment_PublishedAt': formatted_comment_published_at,
                'Comment_Text': response['items'][0]['snippet']['textOriginal']
            }
        else:
            # handling the case where no comment data is found
            comment_data = {}

    except IndexError:
        # handling the IndexError
        comment_data = {}

    return comment_data


def extract_and_transform(channel_id):
    channel_data = channel(channel_id)
    if not channel_data:
        print("No channel data retrieved for the given channel ID.")
        return None

    video_ids = get_video_ids(channel_id)  # the first 10 video IDs
    if not video_ids:
        print("No video IDs retrieved for the channel.")
        return None

    video_details = []
    comment_data_all = []  # Collect all comment data from all videos

    for vid_id in video_ids:
        print(f"Processing video ID: {vid_id}")


        vid_data = video(vid_id)
        if vid_data:
            # Getting comment data for each video
            comment_ids = get_comment_ids(vid_id)
            comments_data = []
            if comment_ids:
                for comment_id in comment_ids:
                    comment_data = comment(comment_id)
                    if comment_data:
                        comments_data.append(comment_data)
                        comment_data_all.append(comment_data)

            vid_data['Comments'] = comments_data
            video_details.append(vid_data)
    data = {
        'channel_data': channel_data,
        'video_data': video_details,
        'comment_data': comment_data_all
    }

    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["YOUTUBE"]
    collection = db["y_data"]

    # Insert the data into the MongoDB collection
    try:
        collection.insert_one(data)
        print("Data inserted into MongoDB successfully.")

    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

    return data



def create_mysql_tables(mysql_cursor):
    # Creating tables
    mysql_cursor.execute("""
        CREATE TABLE IF NOT EXISTS channel_data (
            channel_id VARCHAR(50) PRIMARY KEY,
            Channel_Name VARCHAR(255),
            Subscription_Count INT,
            Channel_Views INT,
            Channel_Description TEXT,
            channel_playlist VARCHAR(50)
        )
    """)

    mysql_cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_data (
            _id VARCHAR(50) PRIMARY KEY,
            Channel_id VARCHAR(50),
            Video_Id VARCHAR(50),
            Video_Name VARCHAR(255),
            Video_Description TEXT,
            PublishedAt DATETIME,
            View_Count INT,
            Like_count INT,
            Favorite_count INT,
            Comment_Count INT,
            Duration VARCHAR(20),
            Thumbnail VARCHAR(255)
        )
    """)

    mysql_cursor.execute("""
        CREATE TABLE IF NOT EXISTS comment_data (
            _id VARCHAR(50) PRIMARY KEY,
            Channel_id VARCHAR(50),
            comment_id VARCHAR(100),
            Comment_Author VARCHAR(50),
            Comment_PublishedAt DATETIME,
            Comment_Text TEXT
        )
    """)

def insert_data_to_mysql(data, mysql_cursor):
    channel_data = data['channel_data']
    mysql_cursor.execute("""
        INSERT INTO channel_data 
        (channel_id, Channel_Name, Subscription_Count, Channel_Views, Channel_Description, channel_playlist)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        channel_data['channel_id'],
        channel_data['Channel_Name'],
        channel_data['Subscription_Count'],
        channel_data['Channel_Views'],
        channel_data['Channel_Description'],
        channel_data['channel_playlist']
    ))

    # Insert video data
    video_data = data['video_data']
    for video in video_data:
        mysql_cursor.execute("""
            INSERT INTO video_data 
            (_id, Channel_id, Video_Id, Video_Name, Video_Description, PublishedAt, View_Count, Like_count, Favorite_count, Comment_Count, Duration, Thumbnail)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(ObjectId()),  # Generate an ID for MySQL
            video['Channel_id'],
            video['Video_Id'],
            video['Video_Name'],
            video['Video_Description'],
            video['PublishedAt'],
            video['View_Count'],
            video['Like_count'],
            video['Favorite_count'],
            video['Comment_Count'],
            video['Duration'],
            video['Thumbnail']
        ))

        # Insert comments for each video
    comments = data['comment_data']
    for comment in comments:
        mysql_cursor.execute("""
            INSERT INTO comment_data 
            (_id, Channel_id, comment_id, Comment_Author, Comment_PublishedAt, Comment_Text)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            str(ObjectId()),  # Generate an ID for MySQL
            comment['Channel_id'],
            comment['comment_id'],
            comment['Comment_Author']['value'],
            comment['Comment_PublishedAt'],
            comment['Comment_Text']
            ))

def handle_question(selected_question, mysql_cursor, px=None):
    if selected_question == '1. What are the names of all the videos and their corresponding channels?':
        mysql_cursor.execute("""
            SELECT v.Video_Name ,c.Channel_Name  FROM video_data as v 
            inner join channel_data as c on v.Channel_id=c.channel_id
        """)
        return pd.DataFrame(mysql_cursor.fetchall(), columns=mysql_cursor.column_names)

    elif selected_question == '2. Which channels have the most number of videos, and how many videos do they have?':
        mysql_cursor.execute("""select c.Channel_Name,count(v.Video_Id) as Video_count from video_data as v 
                                inner join channel_data as c on v.Channel_id=c.channel_id
                                group by v.Channel_id""")
        df = pd.DataFrame(mysql_cursor.fetchall(), columns=mysql_cursor.column_names)

        return df

    elif selected_question == '3. What are the top 10 most viewed videos and their respective channels?':
        mysql_cursor.execute("""SELECT v.Video_Name, c.Channel_Name, View_Count AS Views 
                                    FROM video_data as v inner join channel_data as c on v.Channel_id=c.channel_id
                                    ORDER BY View_Count DESC
                                    LIMIT 10""")

        return pd.DataFrame(mysql_cursor.fetchall(), columns=mysql_cursor.column_names)

    elif selected_question == '4. How many comments were made on each video, and what are their corresponding video names?':
        mysql_cursor.execute("""SELECT Video_Name AS Video, Comment_Count AS Total_comment
                                    FROM Video_data
                                    ORDER BY Video_Name DESC""")

        return pd.DataFrame(mysql_cursor.fetchall(), columns=mysql_cursor.column_names)

    elif selected_question == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        mysql_cursor.execute("""SELECT v.Video_Name, c.Channel_Name, Like_count AS Likes_Count 
                                    FROM video_data as v inner join channel_data as c on v.Channel_id=c.channel_id
                                    ORDER BY Like_count DESC
                                    LIMIT 10""")

        return pd.DataFrame(mysql_cursor.fetchall(), columns=mysql_cursor.column_names)

    elif selected_question == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        mysql_cursor.execute("""SELECT Video_Name, Like_count AS Likes_Count
                                    FROM video_data
                                    ORDER BY Like_count DESC""")

        return pd.DataFrame(mysql_cursor.fetchall(), columns=mysql_cursor.column_names)

    elif selected_question == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        mysql_cursor.execute("""SELECT Channel_Name, Channel_Views AS Total_Views
                                    FROM channel_data 
                                    ORDER BY Total_Views DESC""")
        df = pd.DataFrame(mysql_cursor.fetchall(), columns=mysql_cursor.column_names)

        return df

    elif selected_question == '8. What are the names of all the channels that have published videos in the year 2022?':
        mysql_cursor.execute("""SELECT DISTINCT c.Channel_Name
                                FROM video_data as v inner join channel_data as c on v.Channel_id=c.channel_id
                                WHERE YEAR(PublishedAt) = 2022
                                ORDER BY Channel_Name""")
        df = pd.DataFrame(mysql_cursor.fetchall(), columns=mysql_cursor.column_names)

        return df

    elif selected_question == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        mysql_cursor.execute("""SELECT c.Channel_Name AS Channel_Name, convert(SEC_TO_TIME(AVG(TIME_TO_SEC(Duration))),char) AS Average_Duration
                                FROM video_data as v inner join channel_data as c on v.Channel_id=c.channel_id
                                GROUP BY Channel_Name""")

        df = pd.DataFrame(mysql_cursor.fetchall(), columns=[1,2])



        st.dataframe(df)

    elif selected_question == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        mysql_cursor.execute("""SELECT v.Video_Name, c.Channel_Name, Comment_Count AS Comments_Count
                                    FROM video_data as v inner join channel_data as c on v.Channel_id=c.channel_id
                                    ORDER BY Comment_Count DESC
                                    LIMIT 10""")

        df = pd.DataFrame(mysql_cursor.fetchall(), columns=mysql_cursor.column_names)
        return df

    else:
        st.write("No query selected.")
        return None
    
def main():
    st.title('YouTube Data Extraction and Storage')
    # Initialize data variable
    data = None

    # Sidebar for user input
    channel_id = st.sidebar.text_input("Enter YouTube Channel ID")
    if st.sidebar.button('Extract and Display Channel Details'):
        display_channel_details(channel_id)

    if st.sidebar.button('Extract and Transform Data'):
        # Assign the returned data to the variable
        data = extract_and_transform(channel_id)

    # Proceed if data is not None
    if data:
        # Connect to MySQL
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="ilovesreeraj",
            database="newdata",
            auth_plugin='mysql_native_password',
            charset='utf8mb4'
        )

        mysql_cursor = mydb.cursor()

        create_mysql_tables(mysql_cursor)

        insert_data_to_mysql(data, mysql_cursor)

        # Commit changes and close connection
        mydb.commit()
        mysql_cursor.close()
        mydb.close()

        # Query section
    st.title("Query the Database")
    st.write("Select a question to get insights")

    questions = [
            ' Select a question:',
            '1. What are the names of all the videos and their corresponding channels?',
            '2. Which channels have the most number of videos, and how many videos do they have?',
            '3. What are the top 10 most viewed videos and their respective channels?',
            '4. How many comments were made on each video, and what are their corresponding video names?',
            '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
            '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
            '7. What is the total number of views for each channel, and what are their corresponding channel names?',
            '8. What are the names of all the channels that have published videos in the year 2022?',
            '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
            '10. Which videos have the highest number of comments, and what are their corresponding channel names?'
        ]

    selected_question = st.selectbox('Select a question:', questions)
    if selected_question:
        mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="ilovesreeraj",
                database="newdata",
                auth_plugin='mysql_native_password',
                charset='utf8mb4'
            )
        mysql_cursor = mydb.cursor()

        result = handle_question(selected_question, mysql_cursor)

        # Display the result
        st.write(result)

        mysql_cursor.close()
        mydb.close()




if __name__ == "__main__":
    main()
