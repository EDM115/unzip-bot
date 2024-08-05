# How to create a MongoDB URL in 10min ?
  
1. Go to [MongoDB website](https://mongodb.com/cloud/atlas/register)  
  *(skip steps 2 and 3 if you already have an account, just create a new cluster)*
1. On the account setup page, choose wisely your Organization name and Project name (you can't change that). Select Python as preferred language
2. Choose `Create a cluster` on the `Shared Clusters` category (the free one)
3. Choose `Azure` as provider and `Netherlands` as region, then click on `Create Cluster` (it takes 1-5 minutes, but don't close the window !)
4. When it's done, click on `Network Access` on left panel
    1. `Add IP Address`
    2. `Allow access from anywhere` (because Heroku IP addresses changes everytime)
    3. `Confirm` (it can take up to 2 minutes)
5. Click on `Clusters` on left panel
    1. `Connect`
    2. Create a Database User (remember the credentials you choose !)
    3. `Choose a connection method`
    4. `Connect with your application`
    5. Choose `Python` as Driver
    6. Choose `3.6 or later` as Version
    7. Copy the URL
6. Replace `<password>` with the one you chosen at step 5.ii

## You're done :partying_face:
### Now use that as `MONGODB_URL`
> [!NOTE]  
> It should look like : `mongodb+srv://username:password@cluster-name.abcde.mongodb.net/?retryWrites=true&w=majority`  
> You can strip the DB name here, it's set on the `MONGODB_DBNAME` env var
