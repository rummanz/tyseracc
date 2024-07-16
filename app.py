from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
import csv
import uuid
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'siakdhlkasjdlksajfdl'

def get_db_connection():
    conn = psycopg2.connect(database="accdata", user="postgres", password="postgres")
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT account_id, account_name FROM accounts')
    accounts = cur.fetchall()
    cur.close()
    conn.close()

    num_rows = 1  # Set this to the desired number of rows

    return render_template('index.html', accounts=accounts, num_rows=num_rows)

@app.route('/add_account', methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        account_name = request.form['account_name']
        account_type = request.form['account_type']
        is_parent_account = request.form.get('is_parent_account')
        parent_account_id = request.form.get('parent_account_id') if not is_parent_account else None

        conn = get_db_connection()
        cur = conn.cursor()

        # Generate UUID for account ID
        account_id = str(uuid.uuid4())  # Convert UUID to string

        cur.execute('INSERT INTO accounts (account_id, account_name, account_type, parent_account_id) VALUES (%s, %s, %s, %s)',
                    (account_id, account_name, account_type, parent_account_id))
        conn.commit()
        cur.close()
        conn.close()
        flash('Account added successfully!')
        return redirect(url_for('add_account'))

    # Fetch existing parent accounts
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_id, account_name FROM accounts WHERE parent_account_id IS NULL")
    parent_accounts = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('add_account.html', parent_accounts=parent_accounts)

@app.route('/add_journal', methods=['GET', 'POST'])
def add_journal():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT account_id, account_name FROM accounts')
    accounts = cur.fetchall()
    cur.close()
    conn.close()

    if request.method == 'POST':
        transaction_date = request.form.get('transaction_date')
        voucher_number = request.form.get('voucher_number')

        transactions = []
        row_index = 0
        while True:
            cheque = request.form.get(f'cheque_{row_index}')
            account_id = request.form.get(f'account_id_{row_index}')
            description = request.form.get(f'description_{row_index}')
            debit = request.form.get(f'debit_{row_index}')
            credit = request.form.get(f'credit_{row_index}')
            
            if not account_id:
                break

            amount = debit if debit else credit
            trans_type = 'debit' if debit else 'credit'

            if transaction_date and account_id and amount:
                transactions.append((transaction_date, account_id, amount, trans_type, voucher_number, description, cheque))

            row_index += 1
        
        conn = get_db_connection()
        cur = conn.cursor()
        for transaction in transactions:
            cur.execute('''
                INSERT INTO transactions (transaction_date, account_id, amount, type, voucher_number, description, cheque) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', transaction)
        conn.commit()
        cur.close()
        conn.close()

        flash('Transactions added successfully!')
        return redirect(url_for('index'))

    return render_template('index.html', accounts=accounts, num_rows=2)



@app.route('/view_reports', methods=['GET', 'POST'])
def view_reports():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        report_type = request.form['report_type']

        conn = get_db_connection()
        cur = conn.cursor()
        
        
        if report_type == 'Summary Statement':
                # Define cash and bank account names
                cash_account = 'CASH-HO:CASH'
                bank_accounts = [
                    'HSBC. HSBC A/C (001-072370-011)',
                    'MTBL. MTBL A/C (0046-0210002250)',
                    'MTBL. MTBL A/C (0022-0210008770)'
                ]
                
                # Updated SQL Query
                query = """
                WITH voucher_transactions AS (
                    SELECT 
                        t.voucher_number,
                        t.transaction_date,
                        t.account_id,
                        a.account_name,
                        t.type,
                        t.amount,
                        a.parent_account_id
                    FROM transactions t
                    JOIN accounts a ON t.account_id = a.account_id
                    WHERE t.voucher_number IS NOT NULL
                ),
                cash_bank_transactions AS (
                    SELECT 
                        vt.voucher_number,
                        vt.transaction_date,
                        vt.account_name,
                        SUM(CASE WHEN vt.account_name = %s AND vt.type = 'debit' THEN vt.amount ELSE 0 END) AS cash_in,
                        SUM(CASE WHEN vt.account_name = %s AND vt.type = 'credit' THEN vt.amount ELSE 0 END) AS cash_out,
                        SUM(CASE WHEN vt.account_name IN %s AND vt.type = 'debit' THEN vt.amount ELSE 0 END) AS bank_in,
                        SUM(CASE WHEN vt.account_name IN %s AND vt.type = 'credit' THEN vt.amount ELSE 0 END) AS bank_out
                    FROM voucher_transactions vt
                    WHERE vt.account_name IN (%s, %s, %s, %s)
                    GROUP BY vt.voucher_number, vt.transaction_date, vt.account_name
                )
                SELECT 
                    vt.account_name,
                    SUM(cbt.cash_in) AS cash_in,
                    SUM(cbt.cash_out) AS cash_out,
                    SUM(cbt.bank_in) AS bank_in,
                    SUM(cbt.bank_out) AS bank_out,
                    SUM(cbt.cash_in + cbt.bank_in) AS total_in,
                    SUM(cbt.cash_out + cbt.bank_out) AS total_out
                FROM voucher_transactions vt
                JOIN cash_bank_transactions cbt ON vt.voucher_number = cbt.voucher_number AND vt.transaction_date = cbt.transaction_date
                WHERE vt.account_name NOT IN (%s, %s, %s, %s)
                GROUP BY vt.account_name;
                """

                # Execute the query
                cur.execute(query, (
                    cash_account,
                    cash_account,
                    tuple(bank_accounts),
                    tuple(bank_accounts),
                    cash_account,
                    bank_accounts[0],
                    bank_accounts[1],
                    bank_accounts[2],
                    cash_account,
                    bank_accounts[0],
                    bank_accounts[1],
                    bank_accounts[2]
                ))

                # Fetch results
                summary_data = cur.fetchall()

                # Process fetched data and prepare report
                report_data = []
                for row in summary_data:
                    account_name, cash_in, cash_out, bank_in, bank_out, total_in, total_out = row
                    report_data.append({
                        'account_name': account_name,
                        'cash_in': cash_in,
                        'cash_out': cash_out,
                        'bank_in': bank_in,
                        'bank_out': bank_out,
                        'total_in': total_in,
                        'total_out': total_out
                    })

                # Calculate totals
                totals = {
                    'cash_in': sum(data['cash_in'] for data in report_data),
                    'cash_out': sum(data['cash_out'] for data in report_data),
                    'bank_in': sum(data['bank_in'] for data in report_data),
                    'bank_out': sum(data['bank_out'] for data in report_data)
                }

                return render_template('summary_statement.html', report_data=report_data, totals=totals, start_date=start_date, end_date=end_date)

        
        elif report_type == 'Ledger':
            # Fetch balance b/f for each child account
            cur.execute("""
                SELECT a.account_name, a.account_id, 
                       COALESCE(SUM(CASE WHEN t.type = 'debit' THEN t.amount ELSE 0 END), 0) - 
                       COALESCE(SUM(CASE WHEN t.type = 'credit' THEN t.amount ELSE 0 END), 0) AS balance_bf
                FROM accounts a
                LEFT JOIN transactions t ON a.account_id = t.account_id
                WHERE t.transaction_date < %s
                AND a.parent_account_id IS NOT NULL
                GROUP BY a.account_name, a.account_id
                ORDER BY a.account_name
            """, (start_date,))
            balances_bf = cur.fetchall()

            # Fetch transactions within the date range for child accounts
            cur.execute("""
                SELECT a.account_name, t.transaction_date, t.voucher_number, t.description, 
                       CASE WHEN t.type = 'debit' THEN t.amount ELSE 0 END AS debit,
                       CASE WHEN t.type = 'credit' THEN t.amount ELSE 0 END AS credit
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE a.parent_account_id IS NOT NULL
                AND t.transaction_date BETWEEN %s AND %s
                ORDER BY a.account_name, t.transaction_date, t.voucher_number
            """, (start_date, end_date))

            transactions = cur.fetchall()
            cur.close()
            conn.close()

            ledger_report = {}

            # Initialize ledger report with Balance B/F
            for account_name, account_id, balance_bf in balances_bf:
                ledger_report[account_name] = {
                    'initial_balance': Decimal(balance_bf),
                    'transactions': []
                }

            # Populate transactions and compute running balances
            for account_name, transaction_date, voucher_number, description, debit, credit in transactions:
                if account_name not in ledger_report:
                    ledger_report[account_name] = {
                        'initial_balance': Decimal('0.00'),
                        'transactions': []
                    }
                ledger_report[account_name]['transactions'].append({
                    'date': transaction_date,
                    'voucher_number': voucher_number,
                    'description': description,
                    'debit': Decimal(debit),
                    'credit': Decimal(credit)
                })

            # Calculate running balances and totals
            for account_name, data in ledger_report.items():
                initial_balance = data['initial_balance']
                running_balance = initial_balance
                total_debit = Decimal('0.00')
                total_credit = Decimal('0.00')

                for transaction in data['transactions']:
                    running_balance += transaction['debit'] - transaction['credit']
                    total_debit += transaction['debit']
                    total_credit += transaction['credit']
                    transaction['balance'] = running_balance

                data['total_debit'] = total_debit
                data['total_credit'] = total_credit
                data['closing_balance'] = running_balance

            return render_template('ledger_report.html', ledger=ledger_report, start_date=start_date, end_date=end_date)
        
        
        
        elif report_type == 'Cash/Bank Book':
            def get_account_id(account_name):
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('SELECT account_id FROM accounts WHERE account_name = %s', (account_name,))
                account_id = cur.fetchone()
                cur.close()
                conn.close()
                return account_id[0] if account_id else None

            def get_bank_account_ids():
                return [
                    get_account_id('HSBC. HSBC A/C (001-072370-011)'),
                    get_account_id('MTBL. MTBL A/C (0046-0210002250)'),
                    get_account_id('MTBL. MTBL A/C (0022-0210008770)')
                ]

            def get_account_name(account_id):
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('SELECT account_name FROM accounts WHERE account_id = %s', (account_id,))
                account_name = cur.fetchone()
                cur.close()
                conn.close()
                return account_name[0] if account_name else 'Unknown'
            
            cur.execute("""
            SELECT 
                account_id, 
                SUM(CASE WHEN type = 'debit' THEN amount ELSE 0 END) - 
                SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END) AS balance
            FROM transactions 
            WHERE transaction_date < %s AND account_id IN (
                SELECT account_id FROM accounts WHERE account_name IN (
                    'CASH-HO:CASH',
                    'HSBC. HSBC A/C (001-072370-011)',
                    'MTBL. MTBL A/C (0046-0210002250)',
                    'MTBL. MTBL A/C (0022-0210008770)'
                )
            )
            GROUP BY account_id
            """, (start_date,))
            initial_balances = cur.fetchall()

            # Fetch transactions within the date range for relevant accounts
            cur.execute("""
                SELECT 
                    transaction_date, 
                    voucher_number, 
                    cheque, 
                    account_id, 
                    description, 
                    amount, 
                    type 
                FROM transactions 
                WHERE transaction_date BETWEEN %s AND %s 
                AND account_id IN (
                    SELECT account_id FROM accounts WHERE account_name IN (
                        'CASH-HO:CASH',
                        'HSBC. HSBC A/C (001-072370-011)',
                        'MTBL. MTBL A/C (0046-0210002250)',
                        'MTBL. MTBL A/C (0022-0210008770)'
                    )
                )
                ORDER BY transaction_date
            """, (start_date, end_date))
            transactions = cur.fetchall()

            cur.close()
            conn.close()

            # Calculate balances and format data
            cash_balance = next((bal for acc_id, bal in initial_balances if acc_id == get_account_id('CASH-HO:CASH')), 0)
            bank_balance = sum(bal for acc_id, bal in initial_balances if acc_id in get_bank_account_ids())

            report_data = [{
                'date': start_date,
                'voucher_no': '',
                'cheque': '',
                'account': '',
                'remarks': 'Balance B/F',
                'cash_paid_in': '',
                'cash_paid_out': '',
                'cash_balance': cash_balance,
                'bank_paid_in': '',
                'bank_paid_out': '',
                'bank_balance': bank_balance
            }]

            for trans in transactions:
                trans_date, voucher_no, cheque, acc_id, description, amount, trans_type = trans
                
                # Initialize variables to default values at the start of each iteration
                cash_paid_in = cash_paid_out = bank_paid_in = bank_paid_out = None
                
                if acc_id == get_account_id('CASH-HO:CASH'):
                    if trans_type == 'debit':
                        cash_balance += amount
                        cash_paid_in = amount
                        cash_paid_out = ''
                    else:
                        cash_balance -= amount
                        cash_paid_in = ''
                        cash_paid_out = amount
                else:
                    if trans_type == 'debit':
                        bank_balance += amount
                        bank_paid_in = amount
                        bank_paid_out = ''
                    else:
                        bank_balance -= amount
                        bank_paid_in = ''
                        bank_paid_out = amount

                report_data.append({
                    'date': trans_date,
                    'voucher_no': voucher_no,
                    'cheque': cheque,
                    'account': get_account_name(acc_id),  # Ensure get_account_name is defined
                    'remarks': description,
                    'cash_paid_in': cash_paid_in if cash_paid_in is not None else '',
                    'cash_paid_out': cash_paid_out if cash_paid_out is not None else '',
                    'cash_balance': cash_balance,
                    'bank_paid_in': bank_paid_in if bank_paid_in is not None else '',
                    'bank_paid_out': bank_paid_out if bank_paid_out is not None else '',
                    'bank_balance': bank_balance
                })


            return render_template('cash_bank_book.html', data=report_data, start_date=start_date, end_date=end_date)

        elif report_type == 'Balance Sheet':
            # Debug: Print statement to verify data retrieval
            print("Fetching assets for balance sheet")

            # Fetching assets with parent account consideration
            cur.execute("""
            SELECT a.account_name, 
                SUM(CASE WHEN t.type = 'debit' THEN t.amount ELSE 0 END) - 
                SUM(CASE WHEN t.type = 'credit' THEN t.amount ELSE 0 END) AS balance,
                CASE
                    WHEN SUBSTR(pa.account_name, 1, 3) IN ('101', '103', '105', '106', '107') THEN 'Current Assets'
                    WHEN SUBSTR(pa.account_name, 1, 3) = '102' THEN 'Fixed Assets'
                    WHEN SUBSTR(pa.account_name, 1, 3) = '104' THEN 'Other Assets'
                    ELSE 'Uncategorized'
                END AS subcategory
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            LEFT JOIN accounts pa ON a.parent_account_id = pa.account_id
            WHERE a.account_type = 'Assets'
                AND t.transaction_date BETWEEN %s AND %s  -- Add date filter
            GROUP BY a.account_name, pa.account_name
            """, (start_date, end_date))
            assets = cur.fetchall()

            # Debug: Print the fetched assets
            print("Assets:", assets)

            # Fetching liabilities and owners' equity with parent account consideration
            cur.execute("""
            SELECT a.account_name, 
                   SUM(CASE WHEN t.type = 'debit' THEN t.amount ELSE 0 END) - 
                   SUM(CASE WHEN t.type = 'credit' THEN t.amount ELSE 0 END) AS balance,
                   CASE
                       WHEN SUBSTR(pa.account_name, 1, 3) = '201' THEN 'Liability'
                       WHEN SUBSTR(pa.account_name, 1, 3) = '202' THEN 'Owners Equity'
                       WHEN SUBSTR(pa.account_name, 1, 3) = '203' THEN 'Liability'
                       WHEN SUBSTR(pa.account_name, 1, 3) = '204' THEN 'Liability'
                       ELSE 'Uncategorized'
                   END AS subcategory
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            LEFT JOIN accounts pa ON a.parent_account_id = pa.account_id
            WHERE a.account_type = 'Liabilities and Owners Equity'
                  AND t.transaction_date BETWEEN %s AND %s  -- Add date filter
            GROUP BY a.account_name, pa.account_name
            """, (start_date, end_date))
            liabilities_equities = cur.fetchall()

            # Debug: Print the fetched liabilities and equities
            print("Liabilities and Equities:", liabilities_equities)

            cur.close()
            conn.close()

            # Separate liabilities and owners' equity based on the subcategory
            liabilities = [(acc_name, balance) for acc_name, balance, subcat in liabilities_equities if subcat == 'Liability']
            equities = [(acc_name, balance) for acc_name, balance, subcat in liabilities_equities if subcat == 'Owners Equity']

            # Calculate totals
            total_assets = sum([balance for _, balance, _ in assets])
            total_liabilities = sum([balance for _, balance in liabilities])
            total_equities = sum([balance for _, balance in equities])

            # Debug: Print totals
            print("Total Assets:", total_assets)
            print("Total Liabilities:", total_liabilities)
            print("Total Equities:", total_equities)

            balance_sheet_data = {
                'assets': assets,
                'liabilities': liabilities,
                'equities': equities,
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'total_equities': total_equities
            }

            return render_template('balance_sheet.html', data=balance_sheet_data, start_date=start_date, end_date=end_date)

        elif report_type == 'Income Statement':
            # Income Statement: Revenues and Expenses for the period
            cur.execute("""
                SELECT a.account_name, a.account_type, SUM(t.amount) as balance
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.transaction_date BETWEEN %s AND %s AND a.account_type IN ('Income', 'Expenditure')
                GROUP BY a.account_name, a.account_type
                ORDER BY a.account_type, a.account_name
            """, (start_date, end_date))
            income_statement_data = cur.fetchall()
            cur.close()
            conn.close()
            return render_template('income_statement.html', data=income_statement_data, start_date=start_date, end_date=end_date)

        elif report_type == 'Cash Flow Statement':
            # Cash Flow Statement: Cash inflows and outflows for the period
            cur.execute("""
                SELECT a.account_name, t.transaction_date, t.amount, t.type
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE t.transaction_date BETWEEN %s AND %s AND a.account_type = 'Assets' AND a.account_name = 'Cash'
                ORDER BY t.transaction_date
            """, (start_date, end_date))
            cash_flow_data = cur.fetchall()
            cur.close()
            conn.close()
            return render_template('cash_flow_statement.html', data=cash_flow_data, start_date=start_date, end_date=end_date)

        elif report_type == 'Trial Balance':
            # Query to calculate total debits and credits for each account within the period
            cur.execute("""
            SELECT a.account_name,
                   SUM(CASE WHEN t.type = 'debit' THEN t.amount ELSE 0 END) AS total_debit,
                   SUM(CASE WHEN t.type = 'credit' THEN t.amount ELSE 0 END) AS total_credit
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE t.transaction_date BETWEEN %s AND %s
            GROUP BY a.account_name
            ORDER BY a.account_name
        """, (start_date, end_date))

        trial_balance_data = cur.fetchall()

        # Calculate total debit and credit amounts
        total_debit = sum(row[1] for row in trial_balance_data)
        total_credit = sum(row[2] for row in trial_balance_data)

        cur.close()
        conn.close()

        return render_template('trial_balance.html', 
                               data=trial_balance_data, 
                               start_date=start_date, 
                               end_date=end_date, 
                               total_debit=total_debit, 
                               total_credit=total_credit)

    return render_template('reports.html', transactions=[], start_date=None, end_date=None)


@app.route('/import_csv', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            csv_data = csv.reader(file)
            conn = get_db_connection()
            cur = conn.cursor()
            for row in csv_data:
                account_name, account_type, parent_account_id = row
                cur.execute('INSERT INTO accounts (account_name, account_type, parent_account_id) VALUES (%s, %s, %s)',
                            (account_name, account_type, parent_account_id))
            conn.commit()
            cur.close()
            conn.close()
            flash('Data imported successfully!')
            return redirect(url_for('index'))
    return render_template('upload.html')


@app.route('/get_accounts')
def get_accounts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_id, account_name, account_type, parent_account_id FROM accounts")
    accounts = cur.fetchall()
    cur.close()
    conn.close()

    accounts_list = []
    for account in accounts:
        accounts_list.append({
            'account_id': account[0],
            'account_name': account[1],
            'account_type': account[2],
            'parent_account_id': account[3]
        })

    return jsonify(accounts_list)
# Route to view all transactions

@app.route('/view_transactions')
def view_transactions():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT transaction_id, transaction_date, accounts.account_name, amount, type
        FROM transactions
        JOIN accounts ON transactions.account_id = accounts.account_id
    """)
    transactions = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('view_transactions.html', transactions=transactions)

# Route to delete a transaction
@app.route('/delete_transaction/<transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM transactions WHERE transaction_id = %s', (transaction_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Transaction deleted successfully!')
    return redirect(url_for('view_transactions'))

# Route to edit a transaction
@app.route('/edit_transaction/<transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        transaction_date = request.form['transaction_date']
        account_id = request.form['account_id']
        debit = request.form['debit']
        credit = request.form['credit']
        amount = debit if debit else credit
        trans_type = 'debit' if debit else 'credit'

        cur.execute("""
            UPDATE transactions
            SET transaction_date = %s, account_id = %s, amount = %s, type = %s
            WHERE transaction_id = %s
        """, (transaction_date, account_id, amount, trans_type, transaction_id))
        conn.commit()
        cur.close()
        conn.close()
        flash('Transaction updated successfully!')
        return redirect(url_for('view_transactions'))

    cur.execute("""
        SELECT transaction_id, transaction_date, account_id, amount, type
        FROM transactions
        WHERE transaction_id = %s
    """, (transaction_id,))
    transaction = cur.fetchone()

    cur.execute('SELECT account_id, account_name FROM accounts')
    accounts = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('edit_transaction.html', transaction=transaction, accounts=accounts)

# Route to fetch accounts based on a search query
@app.route('/api/accounts')
def api_accounts():
    search_query = request.args.get('q', '')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT account_id, account_name
        FROM accounts
        WHERE account_name ILIKE %s
    """, (f'%{search_query}%',))
    accounts = cur.fetchall()
    cur.close()
    conn.close()

    accounts_list = [{'id': account[0], 'name': account[1]} for account in accounts]
    return jsonify(accounts_list)

@app.route('/trial_balance', methods=['GET', 'POST'])
def trial_balance():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        conn = get_db_connection()
        cur = conn.cursor()

        # Query to calculate total debits and credits for each account within the period
        cur.execute("""
            SELECT a.account_name,
                   SUM(CASE WHEN t.type = 'debit' THEN t.amount ELSE 0 END) AS total_debit,
                   SUM(CASE WHEN t.type = 'credit' THEN t.amount ELSE 0 END) AS total_credit
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE t.transaction_date BETWEEN %s AND %s
            GROUP BY a.account_name
            ORDER BY a.account_name
        """, (start_date, end_date))

        trial_balance_data = cur.fetchall()

        # Calculate total debit and credit amounts
        total_debit = sum(row[1] for row in trial_balance_data)
        total_credit = sum(row[2] for row in trial_balance_data)

        cur.close()
        conn.close()

        return render_template('trial_balance.html', 
                               data=trial_balance_data, 
                               start_date=start_date, 
                               end_date=end_date, 
                               total_debit=total_debit, 
                               total_credit=total_credit)

    return render_template('trial_balance.html', data=[], start_date=None, end_date=None)


if __name__ == '__main__':
    app.run(debug=True)
