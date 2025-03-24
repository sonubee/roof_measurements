import os

class Random_Function

    def path_of_db:
        # Find the absolute path of quotes.db
    db_path = os.path.abspath("instance/quotes.db")
    print("Full path of your database:", db_path)