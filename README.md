# Common Scents Server

This is the server for the Common Scents project, an indie perfume categorization tool. More coming soon!

## Tooling

Current dependencies include:

-   Flask
-   black (for formatting)
-   pylint (for code style)

## Getting Started

1. Create a virtual environment with `python -m venv venv` (in bash) or `py -3 -m venv venv` in the Windows command prompt.
2. Activate the virtual environment: `. venv/bin/activate` under Linux/OSX or `venv\Scripts\activate` under Windows.
3. Run `flask run` to start the server.
4. Navigate to `localhost:5000` in a browser to see the Hello World page.

## Environment Variables

To populate secrets and configuration variables, create a `.env` file at the root of the project. Create the following values:
|Key|Value|
|---|-----|
|DEBUG|`True` if running in development, `False` otherwise|
|FLASK_ENV| `development` if running in development, `production` otherwise|
|FLASK_APP| Set to `server`
|DATABASE_URL| The URL of your MySQL development database|
|DATABASE_USER| The user name of the account that will access the database for the server |
|DATABASE_PW| The password for the database user |
|DATABASE_NAME| The name of the database (in testing, this is CommonScents) |
|SQLALCHEMY_ECHO| `True` if running in dev and you want to see SQLAlchemy tracebacks, `False` otherwise.
SQLALCHEMY_ECHO=True

## Custom Management Commands

~~The server provides two custom commands for ease of development.~~

~~_**WARNING**_: **Both of these commands will destroy any current records in the database. Make sure you are not pointing at a database you care about before you run these!**~~

~~`initdb`: Drops all existing tables and recreates empty ones.~~

~~`bootstrap`: Drops all existing tables, recreates empty ones, and populates the tables with example data.~~

#

That's it! More soon.
