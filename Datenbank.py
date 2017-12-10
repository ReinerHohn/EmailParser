#!/usr/bin/python
import sqlite3

class BelegDb:
    def __init__(self):
        self.connection = sqlite3.connect("dbname")
        self.cursor = self.connection.cursor()


        sql_command = """
        CREATE TABLE IF NOT EXISTS kassenbeleg ( 
        staff_number INTEGER PRIMARY KEY,
        terminal_id VARCHAR(8), 
        ta_nr VARCHAR(6), 
        genem_nr VARCHAR(6), 
        verwend_zw VARCHAR(128), 
        betrag FLOAT,
        bel_datum DATE);"""
        self.cursor.execute(sql_command)

    def insertBeleg(self, _terminal_id, _ta_nr, _genem_nr, _verwend_zw, _betrag, _datum):
        format_str = """INSERT INTO kassenbeleg (staff_number, terminal_id, ta_nr, genem_nr, verwend_zw, betrag, bel_datum) VALUES (NULL, "{terminal_id}", "{ta_nr}", "{genem_nr}", "{verwend_zw}", "{betrag}", "{bel_datum}");"""

        sql_command = format_str.format( terminal_id=_terminal_id, ta_nr=_ta_nr, genem_nr=_genem_nr, verwend_zw=_verwend_zw, betrag=_betrag, bel_datum=_datum)
        self.cursor.execute(sql_command)

    def getBelegItem(self, item, col):
        self.cursor.execute("SELECT {col} FROM kassenbeleg WHERE {col} = {item}")
        print("fetchall:")
        result = cursor.fetchall()
        for r in result:
            print(r)
        cursor.execute("SELECT * FROM kassenbeleg")
        print("\nfetch one:")
        res = cursor.fetchone()

    def __exit__(self):
        # never forget this, if you want the changes to be saved:
        connection.commit()
        connection.close()