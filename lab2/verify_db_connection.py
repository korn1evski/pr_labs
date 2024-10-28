import psycopg2

def connect_to_database():
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="drago2002",
            host="127.0.0.1",
            port="5432",
            database="postgres"  # Change database name here to 'postgres'
        )
        cursor = connection.cursor()
        # Execute a sample query to verify the connection
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

        # Close the cursor and connection after use
        cursor.close()
        connection.close()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

if __name__ == "__main__":
    connect_to_database()
