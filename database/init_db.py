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
            type VARCHAR(10) NOT NULL,
            voucher_number VARCHAR(50) NOT NULL,
            description TEXT,
            cheque VARCHAR(50)
        )
        """
    )
    conn = None
    try:
        conn = psycopg2.connect(database="accdata", user="postgres", password="postgres")
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def insert_data():
    data = [
        ("0e446910-8198-42c5-863f-f228b613f3c7", "101:Cash", "Assets", None),
        ("53c2c2ac-3c3f-48de-860c-b676869db2cf", "CASH-HO:CASH", "Assets", "0e446910-8198-42c5-863f-f228b613f3c7"),
        ("da5fd8b9-0741-44cb-905f-a28bd812f1bd", "102:Fixed Assets", "Assets", None),
        ("657cb85e-5032-4a69-b018-b37979873c16", "103:Cash at Bank", "Assets", None),
        ("e5e7d08f-3eed-40f3-8e5f-428aee938632", "104:Deffered Tax Assets", "Assets", None),
        ("01bcbce1-2b44-4007-9742-e5e7fd0ee4f5", "105:Account Receivable", "Assets", None),
        ("cbe123fb-113f-48b5-9401-ad9c7c0720df", "106:Advance Deposits and Prepayments", "Assets", None),
        ("9b92c032-ed18-4fe2-9603-8153145b06c1", "107:Advance Income Tax", "Assets", None),
        ("597b1e73-7d38-4add-a2cd-6f594ded2b65", "Motor Vehicle Cost", "Assets", "da5fd8b9-0741-44cb-905f-a28bd812f1bd"),
        ("cf9ddc2a-e034-48e7-a49b-57a336f6e04c", "Computer Hardware Cost", "Assets", "da5fd8b9-0741-44cb-905f-a28bd812f1bd"),
        ("98b65cd5-666e-41ee-91a8-56899c223fc6", "Office Furniture Cost", "Assets", "da5fd8b9-0741-44cb-905f-a28bd812f1bd"),
        ("b5b3464b-bcad-4f11-b260-995c9d5feb29", "201. Liability", "Liabilities and Owners Equity", None),
        ("08b4cacd-a397-405d-86ad-d6a3f81e4e34", "202. Equity", "Liabilities and Owners Equity", None),
        ("37450ad5-d02c-4c11-891a-4995080e90bd", "203. Non Current Liabilities", "Liabilities and Owners Equity", None),
        ("06a86e82-d63d-46b8-815c-111a2b2c5931", "204. Payables", "Liabilities and Owners Equity", None),
        ("eca7a7f0-fddd-49f7-9fbe-819a88bfe8a2", "O-2010. Remittance (Head Office)", "Liabilities and Owners Equity", "b5b3464b-bcad-4f11-b260-995c9d5feb29"),
        ("7d5f9d09-8131-4456-9956-b9abc136a1d8", "C-0001. Creditors", "Liabilities and Owners Equity", "b5b3464b-bcad-4f11-b260-995c9d5feb29"),
        ("ad206314-590d-4c4e-8667-bc2211fea745", "B-2801. AIT (Office Rent)", "Liabilities and Owners Equity", "b5b3464b-bcad-4f11-b260-995c9d5feb29"),
        ("02f4be5b-5bd3-4327-93c3-4f3604019e5f", "B-1016. AIT (Office Staff Salary)", "Liabilities and Owners Equity", "b5b3464b-bcad-4f11-b260-995c9d5feb29"),
        ("7bf0d58d-ff2c-4055-961c-f8960214964a", "P-8000. Company Tax", "Liabilities and Owners Equity", "b5b3464b-bcad-4f11-b260-995c9d5feb29"),
        ("ac8aa5fa-982e-4f94-9adf-cb54949fdf8a", "E-1998. Share Capital", "Liabilities and Owners Equity", "08b4cacd-a397-405d-86ad-d6a3f81e4e34"),
        ("9f65a0ef-180a-42f8-856a-061f0a285cad", "TL-20301. Current Portion (1 Year Payment Timeline)", "Liabilities and Owners Equity", "37450ad5-d02c-4c11-891a-4995080e90bd"),
        ("867e3288-6fe0-4a67-b4ac-df59c1d233ab", "TL-20302. Net Portion (Longer Payment Timeline)", "Liabilities and Owners Equity", "37450ad5-d02c-4c11-891a-4995080e90bd"),
        ("22708da2-7bec-42ed-89a9-a77ce8e78e4a", "TL-20401. Motor Vehicle Fuel Cost Payables", "Liabilities and Owners Equity", "06a86e82-d63d-46b8-815c-111a2b2c5931"),
        ("8645acec-a836-4cb6-8598-6699eebef066", "301. Regular Income", "Income", None),
        ("1c2aac04-8b46-479d-a5f5-8c3f4b73046c", "A-1040. Inspection Fees (Income)", "Income", "8645acec-a836-4cb6-8598-6699eebef066"),
        ("b5ea0ae4-e471-4236-8f42-373dd5e41f60", "302. Irregular/Alternative Income", "Income", None),
        ("51799b32-81ae-420b-80dd-eaa17d2e0188", "A-1050. Income (Insurance Claim)", "Income", "b5ea0ae4-e471-4236-8f42-373dd5e41f60"),
        ("4b291cdb-79ad-4118-a14c-f757bdb32cbf", "A-1060. Income (Asset Sale)", "Income", "b5ea0ae4-e471-4236-8f42-373dd5e41f60"),
        ("16c90d71-e2b3-42ec-a170-bde0a4258052", "402. Vehicle Expenses", "Expenditure", None),
        ("5c92ef49-d7bc-4e68-9944-bbdbc7ec28c4", "401. Staff Expenses", "Expenditure", None),
        ("4e626227-342d-4d9d-a213-c826ddf65582", "404. Foreign Travels", "Expenditure", None),
        ("1f7544a7-982b-4463-b092-9d9bd0f99e8f", "405. Communication Expenses", "Expenditure", None),
        ("7a5593a2-b426-41c9-b893-dc7041835957", "406. Mobile Expenses", "Expenditure", None),
        ("bd62d8dd-bb43-49b7-afdd-e33289c26ec3", "B-1140. Motor Vehicle Maintenance", "Expenditure", "16c90d71-e2b3-42ec-a170-bde0a4258052"),
        ("cd0b3779-defc-4072-8e20-ef74eb75d96b", "B-1150. Motor Vehicle Fuel Cost (+ Security Deposit)", "Expenditure" "16c90d71-e2b3-42ec-a170-bde0a4258052"),
        ("7655b99b-d22c-452a-bd32-cdbf5ce0d701", "B-1151. Lease & Lease Repayments", "Expenditure", "16c90d71-e2b3-42ec-a170-bde0a4258052"),
        ("688c08de-1b4b-4cd3-8c9e-6cd215abf8f6", "X-0982. Motor Vehicle Fuel Cost (CEO Vehicle)", "Expenditure", "16c90d71-e2b3-42ec-a170-bde0a4258052"),
        ("8c02cc2b-0f10-40e6-aeae-494e882a2e19", "A-1100. Inspection & Survey Expenses", "Expenditure", "5c92ef49-d7bc-4e68-9944-bbdbc7ec28c4"),
        ("5669879b-a929-47d1-865d-82101fa6266f", "B-1015. Staff Salaries & Allowances", "Expenditure", "5c92ef49-d7bc-4e68-9944-bbdbc7ec28c4"),
        ("94d3316c-85d1-4255-80a3-369bc0df8501", "B-1240. Guard & Security Services", "Expenditure", "5c92ef49-d7bc-4e68-9944-bbdbc7ec28c4"),
        ("c58efe00-a8ab-45de-b7ec-54a295a38985", "B-1610. Entertainment Expenses (Tyser Staff BD & UK)", "Expenditure", "5c92ef49-d7bc-4e68-9944-bbdbc7ec28c4"),
        ("75536538-8a8a-4ac0-bd6b-67f4b9ef0b41", "B-1720. Travelling & Conveyance Expenses", "Expenditure", "5c92ef49-d7bc-4e68-9944-bbdbc7ec28c4"),
        ("8fa79513-5229-4b8c-aac1-c0e69fab6508", "B-1750. Client Entertainment Expenses", "Expenditure", "5c92ef49-d7bc-4e68-9944-bbdbc7ec28c4"),
        ("fac20541-2a36-4ff3-9d1c-1fd05bb3b139", "B-1020. Staff Bonus", "Expenditure", "5c92ef49-d7bc-4e68-9944-bbdbc7ec28c4"),
        ("4597ea77-7707-45bc-bc45-d142f28094b8", "B-1220. Health Insurance", "Expenditure", "5c92ef49-d7bc-4e68-9944-bbdbc7ec28c4"),
        ("87930e3b-ee4d-4b4e-a445-3052b64e0859", "B-1060. Staff Gratuity", "Expenditure", "5c92ef49-d7bc-4e68-9944-bbdbc7ec28c4"),
        ("3f3606dd-0fa1-4395-9943-46347e0ef0df", "B-1660. Foreign Air Fares", "Expenditure", "4e626227-342d-4d9d-a213-c826ddf65582"),
        ("6da84476-a39d-454e-a235-b7cf1bfb9aca", "B-2000. Land Telephone Installation & Bills", "Expenditure", "1f7544a7-982b-4463-b092-9d9bd0f99e8f"),
        ("23ee2830-b69a-4736-9575-9603a0abe749", "B-2070. Postage Charge", "Expenditure", "1f7544a7-982b-4463-b092-9d9bd0f99e8f"),
        ("3b32e6e2-3398-4976-ac0d-8b5d924bec83", "B-2050. Mobile Phone Cost & Bills", "Expenditure", "7a5593a2-b426-41c9-b893-dc7041835957"),
        ("30a26baf-42bb-48c5-af4c-7c4a8c4fe7e4", "407. Hardware Expenses", "Expenditure", None),
        ("8b923f31-fae1-49bf-bad4-143fb57a15d0", "B-2390. Other Computer Cost", "Expenditure", "30a26baf-42bb-48c5-af4c-7c4a8c4fe7e4"),
        ("afe633ac-8c99-48e6-9584-a62032cda31d", "B-2520. Printing Supplies", "Expenditure", "30a26baf-42bb-48c5-af4c-7c4a8c4fe7e4"),
        ("578d3cab-236e-4cb9-9ae3-a2b921b0521a", "408. Software Expenses", "Expenditure", None),
        ("da94895d-663d-4dba-86bf-8e70ca0a17b7", "409. Others", "Expenditure", None),
        ("ebc51a7a-b05c-4507-84f4-4aa82b92f306", "410. Liability Expenses", "Expenditure", None),
        ("da6ae215-5742-44fd-a3de-1d78e1bf96bb", "411. Advertisement", "Expenditure", None),
        ("2cba3586-32c2-42f4-a76b-40a3a1784c5e", "412. Legal Fees", "Expenditure", None),
        ("66ca4f3d-08ed-4980-8a9c-45ccef58cacb", "B-2260. Software Purchase", "Expenditure", "578d3cab-236e-4cb9-9ae3-a2b921b0521a"),
        ("d1a4cce6-65a3-4c8b-975f-b2e75da7ccee", "B-2380. Website Costs", "Expenditure", "578d3cab-236e-4cb9-9ae3-a2b921b0521a"),
        ("5af6e45a-a50d-4bdc-a45d-5fe010b76141", "B-2090. Other Communication Cost", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("87663e90-f2ff-4bb5-a210-ebc7f830bf84", "B-2130. Internet Usage", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("777d63a3-9346-497d-a2b8-bb09c31a81f4", "B-2530. Stationery Supplies", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("1c722274-6caf-4ab8-a02c-9539f2d8143a", "B-2720. Marketing & Business Development Costs", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("2c55fd81-1535-45bb-9309-b1c4f5f9bb85", "B-2800. Rent Payable", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("cf9ca03c-6cb5-4c67-b7d2-5d6ae59cdf98", "B-2870. Generator Fuel & Maintenance, Electricity, Gas Bill", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("de9a7fd1-8db5-49b3-ac15-e99f173ff0b8", "B-2871. Lease & Lease Repayments (Generator)", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("d3e1867b-5e15-4c43-93b8-43d31b37c9e4", "B-2872. Lease & Lease Repayments (Furniture)", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("dd3a8e2d-247c-4cf2-b4b9-bae2c3783dd4", "B-2880. Water Bill", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("5f98524d-cdcd-4b5e-84a5-5e19d3641908", "B-2890. Cleaning Maintenance Expenses", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("c101d283-5596-4e2d-8308-cc62313a4d69", "B-4010. Trade Subscription", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("c47907d2-92b0-43f9-9edd-22dd3209168d", "B-4130. Bank Charges", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("dce3f68f-9d68-40cb-b33f-4f4e354f73cd", "B-4150. Sundry Expenses", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("58b1b22b-ea53-415e-89bb-0e37bb81700a", "B-2080. Courier Costs", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("6c5f53d5-ae27-4fc1-b843-32a976ac35d6", "B-2500. Photocopier Supplies", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("8b6c5cd4-63ba-45da-acf2-c5c5fe23df95", "B-1890. Other Professional Fees", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("6bb4cb1a-5545-434c-9d4a-00f7201d003a", "B-4040. VAT Expenses", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("dd626442-e2b1-4c2a-bc8c-222ea413edac", "B-2930. Other Premises Cost", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("28022a65-ff56-465f-ba12-06d6ab580803", "B-1230. Life Cover", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("a9d6e2db-e11f-4482-9139-6d02423afb8d", "B-4170. Conference & Seminars", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("661ac251-8569-425f-86b5-000addb96287", "B-2840. Maintenance Cost", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("2b191597-0e4a-4ca8-9268-c8895ab57152", "B-3040. General Insurance", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("84bcf0d3-06f7-42fe-b391-993cac39e299", "B-2100. Communication Maintenance", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("8910fb7b-93ea-4a9a-98fe-1f3f4cd18ced", "B-4030. Corporate Gift", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("28f0e631-daf3-442d-8339-69080e10a633", "B-1830. Audit Fees", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("2c0bfbd3-b740-4744-a6f1-f0f4567f8893", "B-1310. Training - External Courses", "Expenditure" "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("975817c8-a863-459a-b32e-86ce643cd370", "B-2910. Moving Cost", "Expenditure", "da94895d-663d-4dba-86bf-8e70ca0a17b7"),
        ("fb5d1a06-1f8d-412d-a571-7ad7ff7e1083", "B-101601. Expense AIT (Office Staff Salary)", "Expenditure", "ebc51a7a-b05c-4507-84f4-4aa82b92f306"),
        ("fe9fcdf9-1a9c-41d9-80e6-21f0e2fb9ef5", "B-280101. Expense AIT (Office Rent)", "Expenditure", "ebc51a7a-b05c-4507-84f4-4aa82b92f306"),
        ("4c256750-d0c8-4d24-bf46-d2629fc1984c", "B-184001. Expense AIT (Professional Service)", "Expenditure", "ebc51a7a-b05c-4507-84f4-4aa82b92f306"),
        ("2587e532-09b1-4d12-9e7d-f0817b2870d7", "B-1840. Tax Fees (Legal & Professional Fees)", "Expenditure", "ebc51a7a-b05c-4507-84f4-4aa82b92f306"),
        ("cc7e013c-cd47-4294-8098-78e0cb3696d1", "B-2700. Advertising Expenses", "Expenditure", "ebc51a7a-b05c-4507-84f4-4aa82b92f306"),
        ("4cc1a5a5-363b-4823-bdc4-554478248634", "B-2700. Advertising Expenses", "Expenditure", "da6ae215-5742-44fd-a3de-1d78e1bf96bb"),
        ("0c230505-3f2d-4521-912e-3f3e29654424", "B-1800. Legal Fees (Tax Deductible)", "Expenditure", "2cba3586-32c2-42f4-a76b-40a3a1784c5e"),
        ("b9528cc2-045a-41da-8748-296a8fbc999b", "B-1810. Legal Fees (Non-Tax Deductible)", "Expenditure", "2cba3586-32c2-42f4-a76b-40a3a1784c5e"),
        ("3f2dd10a-51a8-4115-9750-e6d731733597", "B-1820. Accountant Fees", "Expenditure", "2cba3586-32c2-42f4-a76b-40a3a1784c5e"),
        ("ad044e4b-0e6c-4f6b-bae2-e0f315b65313", "HSBC. HSBC A/C (001-072370-011)", "Assets", "657cb85e-5032-4a69-b018-b37979873c16"),
        ("c450d37b-c1c9-4fcd-be96-24a11ad7a0d6", "MTBL. MTBL A/C (0046-0210002250)", "Assets", "657cb85e-5032-4a69-b018-b37979873c16"),
        ("be2c3b00-b5f0-4b32-a3b0-b6a9a0e610d9", "MTBL. MTBL A/C (0022-0210008770)", "Assets", "657cb85e-5032-4a69-b018-b37979873c16"),
        ("cf084b01-0e1f-4d08-9aac-7a24edce0378", "TA-10401. Deffered Tax Assets", "Assets", "e5e7d08f-3eed-40f3-8e5f-428aee938632"),
        ("ae30d895-fddb-440a-970f-58a7b1c82ec0", "TA-10501. Accounts Receivables", "Assets", "01bcbce1-2b44-4007-9742-e5e7fd0ee4f5"),
        ("07bc8bb2-dce6-46e1-9702-0e72e08ebd62", "O-4000. Debtors", "Assets", "01bcbce1-2b44-4007-9742-e5e7fd0ee4f5"),
        ("94320e13-7df6-478e-95e6-5c38d1417c3a", "TA-10601. Prepayments", "Assets", "cbe123fb-113f-48b5-9401-ad9c7c0720df"),
        ("99209e91-b92c-44e7-a4bc-4dc097f30e68", "B-2802. Office Rent Advance", "Assets", "cbe123fb-113f-48b5-9401-ad9c7c0720df"),
        ("ee110d05-69e2-45f3-bd76-c244becc0997", "TA-10701. AIT (Client Side)", "Assets", "9b92c032-ed18-4fe2-9603-8153145b06c1"),
    ] 
    
    conn = None
    try:
        conn = psycopg2.connect(database="accdata", user="postgres", password="postgres")
        cur = conn.cursor()
        insert_query = """
        INSERT INTO accounts (account_id, account_name, account_type, parent_account_id) 
        VALUES (%s, %s, %s, %s)
        """
        cur.executemany(insert_query, data)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_tables()
    insert_data()
