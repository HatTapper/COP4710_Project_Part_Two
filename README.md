Tested on Python v3.14.3

Requires installation of MySQL Connector and Flet packages

`pip install flet[all]`
`pip install mysql-connector-python`

The implementation expects you to have a running instance of a MySQL database. To configure connecting to your database, enter main.py and update the fields:

```
DB_HOST_NAME
DB_USER_NAME
DB_USER_PASS
DB_DATABASE_NAME
```

with your relevant values

The implementation will also verify the integrity of your database to ensure that it has all of the necessary tables and columns initialized. If these are not initialized, it will throw an error upon startup.
