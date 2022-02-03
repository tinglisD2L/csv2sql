# csv2sql
A parser for converting CSV files to a temp table in SQL Server

## Use Cases
Investigating defects in a CSV file is an onerous task when performed manually, especially when cross-referencing with the database is required. This parser will create the T-SQL code necessary to reproduce the data inside a temp table in SQL Server, retaining only the columns specified by the user.

Another use case is if you are investigating a defect that only occurs in prod, but reproducing this behaviour in the dev environment is impossible without the relevant data. In this scenario, the parser can be used to mock out the results of an intermediate query in the workflow.

## CSV Input
The input can be any CSV where the first row is the column names, and subsequent rows are the data. The datasets downloaded from Data Hub are suitable inputs.

If you wish to copy the results of a query to use as the CSV input, Open SQL Server Management Studio. Go to Tool > Options. Navigate to Query Results > SQL Server > Results to Grid, and check "Include column headers when copying or saving the results". Click OK then restart SSMS to apply changes.

## Column Type Input
In addition to the CSV data, the parser also takes a column type file as a second input.  The column file specifies the columns from the data file you want to select. Each line in this file should be formatted as "UserId|INT", "LastModified|DATETIME", or "FName|NVARCHAR(256)". If the data file contains any invalid or improperly formatted data, they can be excluded using the column file.

## Run the Script
Make sure Python 3 (I have 3.9) is installed and in the path. Put both input files (data file and column file) in the same directory as the parser. Edit the parameters in parser.py then run it to generate the SQL file.

## Create the Temp Table
Open SQL Server Management Studio and run the T-SQL code generated in the previous step to create the temp table. A common error encountered at this point is invalid typing, due to a specified column type in the column file not matching up with the actual data. It's easy to get DATE, TIME, DATETIME, and DATETIMEs mixed up. Read the error message from SQL Server to determine the source of the mismatch, then rerun the script and the newly generated SQL statements.
