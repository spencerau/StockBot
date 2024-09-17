import sqlite3
import csv

# This is the Ticker. Has an alias, code (letters or number), country of origin.
# Should probably redo this one
makeIss = '''
CREATE TABLE IF NOT EXISTS Issuer (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL UNIQUE,
ticker TEXT,
country TEXT,
);
'''

# Trade Type can only be Buy, Sell, Exchange, Recieve
makeTT = '''
CREATE TABLE IF NOT EXISTS TradeType (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL UNIQUE
);
'''

# Trade Size is just another enum of ranges
makeTX = '''
CREATE TABLE IF NOT EXISTS TradeSize (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    size TEXT NOT NULL UNIQUE
);
'''


makeP = '''
CREATE TABLE IF NOT EXISTS Politician (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    party TEXT
);
'''

# Not sure what price means, if it is N/A then set 0
makeT = '''
CREATE TABLE IF NOT EXISTS Trade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    politicianID INTEGER NOT NULL,
    issuerID INTEGER NOT NULL,
    datePublished TEXT,
    transactionDate TEXT,
    reportingGap INTEGER,
    tradeTypeID INTEGER NOT NULL,
    tradeSizeID INTEGER NOT NULL,
    tradePrice REAL DEFAULT 0,
    FOREIGN KEY (politicianID) REFERENCES Politician(id),
    FOREIGN KEY (issuerID) REFERENCES Issuer(id),
    FOREIGN KEY (tradeTypeID) REFERENCES TradeType(id),
    FOREIGN KEY (tradeSizeID) REFERENCES TradeSize(id)
);'''

def insertFromCSV():
    conn = sqlite3.connect('MoneyLaundering.db')
    cursor = conn.cursor()
    with open('trades_data.csv', 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Insert Issuer, or get existing id
            namecodecountry = row['Issuer'].split(':')
            cursor.execute("SELECT id FROM Issuer WHERE name = ?", (row['Issuer'],))
            issuer_id = cursor.fetchone()
            if issuer_id is None:
                cursor.execute("INSERT INTO Issuer (name) VALUES (?)", (row['Issuer'],))
                issuer_id = cursor.lastrowid
            else:
                issuer_id = issuer_id[0]

            # Insert TradeType, or get existing id
            cursor.execute("SELECT id FROM TradeType WHERE type = ?", (row['Trade Type'],))
            trade_type_id = cursor.fetchone()
            if trade_type_id is None:
                cursor.execute("INSERT INTO TradeType (type) VALUES (?)", (row['Trade Type'],))
                trade_type_id = cursor.lastrowid
            else:
                trade_type_id = trade_type_id[0]

            # Insert TradeSize, or get existing id
            cursor.execute("SELECT id FROM TradeSize WHERE size = ?", (row['Trade Size'],))
            trade_size_id = cursor.fetchone()
            if trade_size_id is None:
                cursor.execute("INSERT INTO TradeSize (size) VALUES (?)", (row['Trade Size'],))
                trade_size_id = cursor.lastrowid
            else:
                trade_size_id = trade_size_id[0]

            # Insert Politician, or get existing id
            cursor.execute("SELECT id FROM Politician WHERE name = ?", (row['Politician'],))
            politician_id = cursor.fetchone()
            if politician_id is None:
                cursor.execute("INSERT INTO Politician (name, party) VALUES (?, ?)", (row['Politician'], "none"))
                politician_id = cursor.lastrowid
            else:
                politician_id = politician_id[0]

            trade_price = row['Trade Price']
            if trade_price == 'N/A' or trade_price == '':
                trade_price = 0
            else:
                trade_price = float(trade_price)
            # Insert into Trade table
            cursor.execute('''INSERT INTO Trade
                            (politicianID, issuerID, datePublished, transactionDate, reportingGap, tradeTypeID, tradeSizeID, tradePrice)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            (politician_id, issuer_id, row['Date Published'], row['Transaction Date'], row['Reporting Gap'],
                            trade_type_id, trade_size_id, trade_price))

        # Commit the transaction after processing all rows
        conn.commit()

    # Close the connection
    conn.close()
