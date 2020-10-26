# CS316_F20_Team8
# Data Procurement
Our project is an online scheduler for task coordination, and our database includes user info, task, announcement, et cetera. This information is highly random, and we plan to generate the data on our own.

Here are a few sources we can generate data from:  
https://www.generatedata.com/  
https://www.mockaroo.com/  

More specifically, we will first generate at least 200 tuples of user information using the aforementioned websites and store them as managers. And then we will generate at least 800 tuples of user information and store them as users. Then we will generate at least 5000 task tuples involving random manager and user pairs, at least 5000 announcement tuples and at least 5000 polls involving random (manager, user, user, user) tuples with randomly generated text description.  The matching will be done using python. With this framework, we can make sure that all the data fit our schema and constraints.

# Data Cleanup
Since we are generating data on our own, we will make sure that our data fits our schema and constraints. Therefore, we believe that data cleanup will not be much needed.
