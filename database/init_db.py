import psycopg2
from psycopg2 import sql

def create_tables():
    commands = (
        """
        CREATE TABLE accounts (
            account_id VARCHAR PRIMARY KEY,
            account_name VARCHAR(255) NOT NULL,
            account_type VARCHAR(255) NOT NULL,
            parent_account_id VARCHAR REFERENCES accounts(account_id)
        )
        """,
        """
        CREATE TABLE transactions (
            transaction_id SERIAL PRIMARY KEY,
            transaction_date DATE NOT NULL,
            account_id VARCHAR NOT NULL REFERENCES accounts(account_id),
            amount NUMERIC(10, 2) NOT NULL,
            type VARCHAR(10) NOT NULL
);
        """
    )
    conn = None
    try:
        #conn = psycopg2.connect(database="accdata", user="postgres", password="postgres")
        conn = psycopg2.connect(user="postgres.pgcsropeslgzznelfnpy", password="duafe#AyUk9@HFQ", host="aws-0-ap-southeast-1.pooler.supabase.com", port="6543", database="postgres")
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_tables()
