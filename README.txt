===========
generate_email
===========

Python script to repurpose eml files into specific date ranges for indexing

Usage
-----

python generate_email.py
	

Arguments
---------

This 0.1 version is entirely hardcoded. Please review the script for details.

Briefly: 

* Under main() there is a section marked "# initialize". Here you can
set the start and end day, number of read or sent emails per day, etc. The 
actual date is constructed later in the script, look for "sDate = "2016-01-"..."

* The script assumes 5 days of regular volume, defined by nReadPerDay and 
nSentPerDay, and then 2 days of 10% of that volume. 

* The script sources from two directories, one for read (received) messages, one
for sent messages.For now you specify the source by setting the variables 
sReadDir and sSentDir. The script doesn't currently worry about running out of 
inputs. :-) 

* Finished emails are written out to the arg specified via -o which defaults

* Many thanks to Dalen (http://stackoverflow.com/users/2247264/dalen) for contributing
 incredible code to extract and manipulate eml files here: 
 http://stackoverflow.com/questions/31392361/how-to-read-eml-file-in-python





