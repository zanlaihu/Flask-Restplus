# Flask-Restplus
develop a Flask-Restplus data service that allows a client to read and store some publicly available economic indicator data for countries around the world, and allow the consumers to access the data through a REST API<br><br>
Access the given Web content programmatically<br><br>
The source URL: http://api.worldbank.org/v2/<br>
Documentations on API Call Structure: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structure<br><br>
As the documentation shows , you can construct URLs specifying different parameters to acquire necessary data. Use a custom URL to get information about a specific indicator. <br><br>
 MongoDB as a service ( https://mlab.com/ ) for this data storage.<br><br>
 
 这是一个基于python语言，结合Flask-Restplus框架搭建的后端系统。<br>
 功能主要为：<br>
 1.从指定网站爬虫获得经济信息，并按经济信息内容存储到特定的mongoDB中。<br>
 2.返回给用户当前网络数据库存储的数据集的内容。<br>
 3.返回给用户特定数据库的特定内容。<br>
 4.删除已存储的数据集。<br><br>
 
 特定：<br>
 1.可根据网站的不同经济数据，自动生成相应集合名并存储到云端数据库。可以防止不同数据之前同存一起的混乱。<br>
 2.数据存储云端，不在本地保留数据。安全方便、不用担心本地数据毁坏，可随时取用。<br><br>
 
 使用技术<br>
 1.python逻辑操作、爬虫，jsons包操作<br>
 2.Flask框架搭建<br>
 3.后端系统与云端数据库mongoDB链接<br>
