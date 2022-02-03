# Instructions
#
# Open SQL Server Management Studio. Go to Tool > Options.
# Navigate to Query Results > SQL Server > Results to Grid,
# and check "Include column headers when copying or saving
# the results". Click OK then restart SSMS to apply changes.
#
# This script takes two inputs, the data file and the column
# file. The data file contains data you want your query to
# return. It can be generated in SSMS by saving results via
# "Save Results As...".
#
# The column file specifies the columns from the data file you
# want to select. Each line in this file should be formatted as
# "UserId|INT", "LastModified|DATETIME", or "FName|NVARCHAR(256)".
#
# Put both files in the same directory as this python script.
# Edit the filenames below. Then run the script to generate
# the SQL query.
#
# The input data file can also be from an Excel spreadsheet.
# The SNHU data is such an example, but beware of Excel-
# specific issues. For instance, don't include columns with
# '#######' values because they won't parse. Also, beware of
# subtle differences between DATETIME and TIME. In the SNHU
# dataset, DWCreated is of type TIME but DWEffectiveStart is
# of type DATETIME.
#
# by Tiffany Inglis
# Nov 18, 2021

import csv
import codecs

dataFile = 'test_input.csv' # the CSV file you want to parse
colFile = 'column-types.csv' # the columns (and their types) that you want to keep
outFile = 'output1.sql' # output file name
tempTable = '#temp' # name of temp table


datatypes = {}
datatypes['BIGINT'] = 'num'
datatypes['BIT'] = 'num'
datatypes['DECIMAL'] = 'num'
datatypes['INT'] = 'num'
datatypes['MONEY'] = 'num'
datatypes['NUMERIC'] = 'num'
datatypes['SMALLINT'] = 'num'
datatypes['SMALLMONEY'] = 'num'
datatypes['TINYINT'] = 'num'
datatypes['FLOAT'] = 'num'
datatypes['REAL'] = 'num'
datatypes['DATE'] = 'time'
datatypes['DATETIME'] = 'time'
datatypes['DATETIME2'] = 'time'
datatypes['DATETIMEOFFSET'] = 'time'
datatypes['SMALLDATETIME'] = 'time'
datatypes['TIME'] = 'time'
datatypes['TEXT'] = 'text'
datatypes['VARCHAR'] = 'text'
datatypes['NCHAR'] = 'text'
datatypes['NTEXT'] = 'text'
datatypes['NVARCHAR'] = 'text'
datatypes['BINARY'] = 'binary'
datatypes['IMAGE'] = 'binary'
datatypes['VARBINARY'] = 'binary'
datatypes['ROWVERSION'] = 'binary'
datatypes['UNIQUEIDENTIFIER'] = 'binary'
datatypes['XML'] = 'text'


class FormattingError(Exception):
    pass

class BadDataError(Exception):
    pass


def validateDataType(dataType):
    try:
        datatypes[dataType.split('(')[0]]
    except Exception:
        print(f'Error: {dataType} is not a valid SQL data type.')

def parseColumnTypeFile(filename):
    f = open(filename, encoding='utf-8-sig')
    cols = {}
    r = 0
    for row in csv.reader(f, delimiter='|'):
        r += 1
        if(len(row)==0):
            continue
        if(len(row)!=2):
            raise FormattingError(f'Line {r} in the column type file is improperly formatted. There should only be one pipe delimiter per line.')
        colName = row[0].strip()
        if(colName == ''):
            raise FormattingError(f'Line {r} in the column type file is improperly formatted. The column name should not be empty.')
        colType = row[1].strip().upper()
        validateDataType(colType)
        cols[colName] = colType
    return cols

def createTempTable(cols):
    rows = []
    for key in cols.keys():
        rows.append('[' + key + '] ' + cols[key])
    x = ',\n\t'.join(rows)
    s = f'CREATE TABLE {tempTable}\n(\n\t{x}\n)'
    return s

def needQuotations(colType, colData):
    if(colData == 'NULL'):
        return False
    try:
        category = datatypes[colType.split('(')[0]]
        return category in ('text','time')
    except Exception:
        print(f'Error: {colType} is not a valid SQL data type.')

def validateColumnNames(selectCols, allCols):
    for col in selectCols:
        if(col not in allCols):
            raise BadDataError(f'{col} is not one of the columns in the data.')

def removeBOM(filename):
    s = open(filename, mode='r', encoding='utf-8-sig').read()
    open(filename, mode='w', encoding='utf-8').write(s)

def parseDataFile(filename, cols):
    try:
        removeBOM(filename)
        print("BOM removed")
    except Exception:
        pass
    dataCsv = csv.DictReader(open(filename, encoding="ISO-8859-1"))
    allCols = dataCsv.fieldnames
    validateColumnNames(cols.keys(), allCols)
    
    dataCsv = csv.DictReader(open(filename, encoding="ISO-8859-1"))
    data = []
    
    for row in dataCsv:
        rowData = []
        for colName in cols.keys():
            colType = cols[colName]
            colData = row[colName]
            if(needQuotations(colType,colData)):
                x = colData.replace("'","''")
                colData = f"'{x}'"
            rowData.append(colData)
        data.append(rowData)
    return data

def insertIntoTempTable(cols,data):
    batches = []
    rows = []
    for row in data:
        x = ','.join(row)
        rows.append(f'({x})')
        if(len(rows) > 990):
            batches.append(rows)
            rows = []
    if(len(rows) > 0):
        batches.append(rows)
    ss = ''
    for batch in batches:
        y = ','.join(cols)
        z = ',\n\t'.join(batch)
        s = f'INSERT INTO {tempTable} ({y})\nVALUES\n\t{z}'
        ss += f'{s}\n\n'
    return ss

cols = parseColumnTypeFile(colFile)
data = parseDataFile(dataFile, cols)

sql1 = createTempTable(cols)
sql2 = insertIntoTempTable(cols,data)

f = open(outFile, 'w', encoding="ISO-8859-1")
f.write(f"IF OBJECT_ID('tempdb..{tempTable}') IS NOT NULL DROP TABLE {tempTable}\nGO\n\n")
f.write(f'{sql1}\n\n{sql2}')
f.write(f'SELECT * FROM {tempTable}')
f.close()