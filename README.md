# discordToken-googleSheets
(script gets discord token and save information about user of its token to Google Sheet)
--------------------------------------------------------------------------------------------
(for using it, you need to change values 'sheet_servers_id' and 'sheet_accounts_id' to yours) 
(and also change s.json to your json-key from google cloud api)


--------------------------------------------------------------------------------------------------------------
    
First part of this script, using id of your google sheet, gets tokens from first column. Then information
about servers, that this user is subscribed to, such as: id, name, date of subscribing of this user to server
and information abut which roles does this user has on ever server; and saving
it to google sheet with 'sheet_servers_id'. 


Next, the second part of the programm again gets all tokens from the first table and, for each, gets 
information about the user. Then saves it to another google sheet with id = 'sheet_accounts_id'.
