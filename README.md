# Youtube Data Harvesting and Warehousing
**Introduction**

The YouTube Data Harvesting and Warehousing project is dedicated to creating an intuitive Streamlit application that harnesses the capabilities of the Google API to gather significant insights from YouTube channels. This extracted information is efficiently stored in a MongoDB database, later transitioned to a SQL data warehouse, and finally presented for comprehensive analysis and exploration within the Streamlit app.

**Key Technologies and Skills Used**

1. Python Scripting
2. Data Collection
3. API integration
4. Streamlit
5. Data Mangement using MongoDB and MySql
   
**Installation**

1. pip install google-api-python-client
2. pip install pymongo
3. pip install pandas
4. pip install mysql-connector-python
5. pip install streamlit
6. pip install isodate

**Usage** 
To use this project, follow these steps:

1. Clone the repository: git clone [https://github.com/SREERAJTS07/Youtube-project/blob/main/mongo.py]
2. Install the required packages : pip install -r requirements.txt
3. Run the Streamlit app: streamlit run mongo.py
4. Access the app in your browser at [http://localhost:8501]

**Features**
- Retrieve data from the YouTube API, including channel information, playlists, videos, and comments.
- Store the retrieved data in a MongoDB database.
- Migrate the data to a SQL data warehouse.
- Analyze and visualize data using Streamlit.
- Perform queries on the SQL data warehouse.
- Gain insights into channel performance and more.

**Retrieving data from the YouTube API**
The project utilizes the Google API to retrieve comprehensive data from YouTube channels. The data includes information on channels, playlists, videos, and comments. By interacting with the Google API.

**Storing data in MongoDB**
The retrieved data is stored in a MongoDB database based on user authorization. If the data already exists in the database, it can be overwritten with user consent. This storage process ensures efficient data management and preservation, allowing for seamless handling of the collected data.

**Migrating data to a SQL data warehouse**
The application allows users to migrate data from MongoDB to a SQL data warehouse. Users can choose which channel's data to migrate. To ensure compatibility with a structured format, the data is cleansed using the powerful pandas library. Following data cleaning, the information is segregated into separate tables, including channels, playlists, videos, and comments, utilizing SQL queries.

**Data Analysis**
Channel Analysis: Channel analysis includes insights on playlists, videos, subscribers, views, likes, comments, and durations. Gain a deep understanding of the channel's performance and audience engagement through summaries.

Video Analysis: Video analysis focuses on views, likes, comments, and durations, enabling both an overall channel and specific channel perspectives. Leverage visual representations and metrics to extract valuable insights from individual videos.
The Streamlit app provides an intuitive interface to interact with the charts and explore the data visually. Users can customize filter data, and zoom in or out to focus on specific aspects of the analysis.

**Contributing**
Contributions to this project are welcome! If you encounter any issues or have suggestions for improvements, please feel free to submit a pull request.

**License**
This project is licensed under the MIT License. Please review the LICENSE file for more details.

**Contact**
📧 Email: sreeraj18surendran41@gmail.com

🌐 LinkedIn: [https://www.linkedin.com/in/sreeraj-surendran-30b903221/]

For any further questions or inquiries, feel free to reach out. We are happy to assist you with any queries.
