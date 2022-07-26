import psycopg2


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(40),
            last_name VARCHAR(40),
            email VARCHAR(40)
        );        
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            id SERIAL PRIMARY KEY,
            number  varchar(10),
            id_client INTEGER NOT NULL REFERENCES clients(id)            
        );
        """)
    conn.commit()


def add_client(conn, name1, name2, e_mail, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO clients(first_name, last_name, email)
            VALUES(%s, %s, %s)
        """, (name1, name2, e_mail,))
        if phone:
            client_id = get_id_client_by_name(conn, name1, name2)
            cur.execute("""
            INSERT INTO phones(number, id_client)
                VALUES(%s, %s)
            """, (phone, client_id,))
    conn.commit()


def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO phones(number, id_client)
                        VALUES(%s, %s)
                    """, (phone, client_id,))
    conn.commit()

def change_client(conn, client_id, name1=None, name2=None, e_mail=None, phone=None):
    with conn.cursor() as cur:
        if name1:
            cur.execute("""
                        UPDATE clients SET first_name=%s WHERE id=%s
                        """, (name1, client_id,))
        if name2:
            cur.execute("""
                        UPDATE clients SET last_name=%s WHERE id=%s
                        """, (name2, client_id,))
        if e_mail:
            cur.execute("""
                        UPDATE clients SET email=%s WHERE id=%s
                        """, (e_mail, client_id,))
        if phone:
            add_phone(conn, client_id, phone)

    conn.commit()


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                    DELETE FROM phones WHERE id_client=%s AND number=%s
                    """, (client_id, phone,))
    conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
                        SELECT id FROM phones WHERE id_client=%s
                    """, (client_id,))
        client_phones_ids = cur.fetchall()
        if client_phones_ids != None:
            for cur_phone_client_id in client_phones_ids:
                cur.execute("""
                                DELETE FROM phones WHERE id=%s
                            """, (cur_phone_client_id,))
            conn.commit()
        cur.execute("""
                    DELETE FROM clients WHERE id=%s
                    """, (client_id,))
    conn.commit()


def print_client_row(client):
    print('First name: {0}\nLast name: {1}\nEmail: {2}\nPhone = {3}'.format(client[0], client[1],
                                                                     client[2], client[3],))


def find_client(conn, name1=None, name2=None, e_mail=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
                        select clients.first_name, clients.last_name, clients.email, phones."number"
                        from clients full outer join phones on clients.id = phones.id_client        
                        WHERE first_name=%s OR last_name=%s OR email=%s OR number=%s       
                    """, (name1, name2, e_mail, phone,))
        client = cur.fetchall()
        print_client_row(client[0])
        if len(client) > 1:
            i = 2
            for row in client[1:]:
                print('Phone{0}: {1}'.format(i, row[3]))
                i += 1


def get_id_client_by_name(conn, name1, name2):
    with conn.cursor() as cur:
        cur.execute("""
                        SELECT id FROM clients WHERE first_name = %s and last_name = %s
                    """, (name1, name2,))
        client_id = cur.fetchone()[0]
    return client_id


with psycopg2.connect(database="clients_info", user="user2", password="pass2") as conn:
    print('success connection')
    create_db(conn)
    add_client(conn, 'John', 'Malcovich', 'malc@mail.ru', '123456')
    add_client(conn, 'Bruce', 'Willis', 'bruce@mail.ru', '98745')
    add_client(conn, 'Arny', 'Swarz', 'swar@mail.ru')
    last_client_id = get_id_client_by_name(conn, 'Arny', 'Swarz')
    add_phone(conn, last_client_id, '55555')
    bruce_id = get_id_client_by_name(conn, 'Bruce', 'Willis')
    add_phone(conn, bruce_id, '000000000')
    change_client(conn, last_client_id, None, None, 'newmail@mail.com', '44444444')
    delete_phone(conn, last_client_id, '44444444')
    delete_client(conn, last_client_id)
    find_client(conn, 'Bruce', 'Willis')
conn.close()
