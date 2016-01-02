==============
generate_email
==============

Python script to generate email in specific date ranges, using input .eml files


Usage
-----
python generate_email.py
	

Arguments
---------
This 0.1 version is hardcoded. Future version(s) may support CLI. Briefly: 

* Under main() there is a section marked "# initialize". Here you can
set the start and end day, number of read or sent emails per day, etc. The 
actual date is constructed later in the script, look for "sDate = "2016-01-"..."

* The script assumes 5 days of regular volume, defined by nReadPerDay and 
nSentPerDay, and then 2 days of 10% of that volume. (That's the weekend.)
You'd have to modify for loop ranges and the nWeekDay variable to change this.

* The script reads input eml files from two directories, one for read (received) 
messages, one for sent messages.For now you specify the source by setting the variables 
sReadDir and sSentDir. 

* Finished emails are written out to the argument specified via -o which defaults
to 'messages2/'


Operation
---------
The script reads eml files from two directories as noted above. The date is modified
to fit the messages into the desired ranges, and some remapping of the fields is
done. Then finished message is then written out to the output directory.


Notes
-----
* The script doesn't currently worry about running out of input files :-) 

* Many thanks to Dalen (http://stackoverflow.com/users/2247264/dalen) for contributing
 incredible code to extract and manipulate eml files here: 
 http://stackoverflow.com/questions/31392361/how-to-read-eml-file-in-python





