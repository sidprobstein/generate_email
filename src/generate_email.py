#!/usr/local/bin/python2.7
# encoding: utf-8
'''
@author:     Sid Probstein
@copyright:  RightWhen, Inc. All Rights Reserved.
@license:    MIT License (https://opensource.org/licenses/MIT)
@contact:    sid@rightwhen.com
'''

import sys
import os
import argparse
import glob
import json
import datetime
import random

# to do: move to a separate module and/or package (low priority)

# the following is from http://stackoverflow.com/questions/31392361/how-to-read-eml-file-in-python
# author http://stackoverflow.com/users/2247264/dalen

from email import message_from_file

# Path to directory where attachments will be stored:
path = "./msgfiles"

# To have attachments extracted into memory, change behaviour of 2 following functions:

def file_exists (f):
    """Checks whether extracted file was extracted before."""
    return os.path.exists(os.path.join(path, f))

def save_file (fn, cont):
    """Saves cont to a file fn"""
    file = open(os.path.join(path, fn), "wb")
    file.write(cont)
    file.close()

def construct_name (id, fn):
    """Constructs a file name out of messages ID and packed file name"""
    id = id.split(".")
    id = id[0]+id[1]
    return id+"."+fn

def disqo (s):
    """Removes double or single quotations."""
    s = s.strip()
    if s.startswith("'") and s.endswith("'"): return s[1:-1]
    if s.startswith('"') and s.endswith('"'): return s[1:-1]
    return s

def disgra (s):
    """Removes < and > from HTML-like tag or e-mail address or e-mail ID."""
    s = s.strip()
    if s.startswith("<") and s.endswith(">"): return s[1:-1]
    return s

def pullout (m, key):
    """Extracts content from an e-mail message.
    This works for multipart and nested multipart messages too.
    m   -- email.Message() or mailbox.Message()
    key -- Initial message ID (some string)
    Returns tuple(Text, Html, Files, Parts)
    Text  -- All text from all parts.
    Html  -- All HTMLs from all parts
    Files -- Dictionary mapping extracted file to message ID it belongs to.
    Parts -- Number of parts in original message.
    """
    Html = ""
    Text = ""
    Files = {}
    Parts = 0
    if not m.is_multipart():
        if m.get_filename(): # It's an attachment
            fn = m.get_filename()
            cfn = construct_name(key, fn)
            Files[fn] = (cfn, None)
            if file_exists(cfn): return Text, Html, Files, 1
            save_file(cfn, m.get_payload(decode=True))
            return Text, Html, Files, 1
        # Not an attachment!
        # See where this belongs. Text, Html or some other data:
        cp = m.get_content_type()
        if cp=="text/plain": Text += m.get_payload(decode=True)
        elif cp=="text/html": Html += m.get_payload(decode=True)
        else:
            # Something else!
            # Extract a message ID and a file name if there is one:
            # This is some packed file and name is contained in content-type header
            # instead of content-disposition header explicitly
            cp = m.get("content-type")
            try: id = disgra(m.get("content-id"))
            except: id = None
            # Find file name:
            o = cp.find("name=")
            if o==-1: return Text, Html, Files, 1
            ox = cp.find(";", o)
            if ox==-1: ox = None
            o += 5; fn = cp[o:ox]
            fn = disqo(fn)
            cfn = construct_name(key, fn)
            Files[fn] = (cfn, id)
            if file_exists(cfn): return Text, Html, Files, 1
            save_file(cfn, m.get_payload(decode=True))
        return Text, Html, Files, 1
    # This IS a multipart message.
    # So, we iterate over it and call pullout() recursively for each part.
    y = 0
    while 1:
        # If we cannot get the payload, it means we hit the end:
        try:
            pl = m.get_payload(y)
        except: break
        # pl is a new Message object which goes back to pullout
        t, h, f, p = pullout(pl, key)
        Text += t; Html += h; Files.update(f); Parts += p
        y += 1
    return Text, Html, Files, Parts

def extract (msgfile, key):
    """Extracts all data from e-mail, including From, To, etc., and returns it as a dictionary.
    msgfile -- A file-like readable object
    key     -- Some ID string for that particular Message. Can be a file name or anything.
    Returns dict()
    Keys: from, to, subject, date, text, html, parts[, files]
    Key files will be present only when message contained binary files.
    For more see __doc__ for pullout() and caption() functions.
    """
    m = message_from_file(msgfile)
    From, To, Subject, Date = caption(m)
    Text, Html, Files, Parts = pullout(m, key)
    Text = Text.strip(); Html = Html.strip()
    msg = {"subject": Subject, "from": From, "to": To, "date": Date,
        "text": Text, "html": Html, "parts": Parts}
    if Files: msg["files"] = Files
    return msg

def caption (origin):
    """Extracts: To, From, Subject and Date from email.Message() or mailbox.Message()
    origin -- Message() object
    Returns tuple(From, To, Subject, Date)
    If message doesn't contain one/more of them, the empty strings will be returned.
    """
    Date = ""
    if origin.has_key("date"): Date = origin["date"].strip()
    From = ""
    if origin.has_key("from"): From = origin["from"].strip()
    To = ""
    if origin.has_key("to"): To = origin["to"].strip()
    Subject = ""
    if origin.has_key("subject"): Subject = origin["subject"].strip()
    return From, To, Subject, Date

# end contribution 
# author http://stackoverflow.com/users/2247264/dalen

#############################################    

def main(argv):
       
    parser = argparse.ArgumentParser(description='Generate email in specific date ranges, using input .eml files')
    parser.add_argument('-o', '--outputdir', default="messages2/", help="subdirectory into which to place enriched files")
    parser.add_argument('-d', '--debug', action="store_true", help="dump diagnostic information for debugging purposes")
    args = parser.parse_args()
                   
    # initialize
    nDays = 20
    nStartDay = 10      # 10th through 30th
    nReadPerDay = 60
    nSentPerDay = 20
    fWeekend = .1
    nWeekDay = 0
    nReadToday = 0
    nSentToday = 0
    nGenerated = 0
    nRead = 0
    nSent = 0
    sReadDir = 'enron/inbox/'
    sSentDir = 'enron/sent/'

    # to do: scan sReadDir and sSentDir and build a list of files
    
    lstReadFiles = []
    lstSentFiles = []
    
    lstReadFiles = glob.glob(sReadDir + '*')
    lstSentFiles = glob.glob(sSentDir + '*')
    
    for nDay in range(0, nDays):
        # day
        nReadToday = nReadPerDay
        nSentToday = nSentPerDay
        nWeekDay = nWeekDay + 1
        if nWeekDay > 5:
            # weekend
            nReadToday = int(nReadToday * fWeekend)
            nSentToday = int(nSentToday * fWeekend)
        if nWeekDay == 7:
            nWeekDay = 0
                
        for nMessages in range(1, nReadToday + nSentToday + 1):
            # emails for that day
            
            #####
            # read emails
            
            # open the next file in ReadDir
            nRead = nRead + 1
            if nRead > nReadToday:
                nSent = nSent + 1
                sFile = lstSentFiles[nSent-1]
            else:
                sFile = lstReadFiles[nRead-1]
            
            # debug                    
            # print "generate_email.py: reading:", sFile
            
            try:
                f = open(sFile, 'rb')
            except Exception, e:
                sys.exit(e)
            # extract the file using the new defs above
            # print json.dumps(extract(f, f.name), sort_keys=True, indent=4, separators=(',', ': '))
            jEml = extract(f, f.name)
            f.close()
            
            # debug
            # print json.dumps(jEml, sort_keys=True, indent=4, separators=(',', ': '))    
                  
            # write the new file out
            jNew = {}
            jNew['user'] = "sid"
            jNew['subject'] = jEml['subject']
            jNew['subject'] = jNew['subject'].replace('\n', ' ')
            jNew['subject'] = jNew['subject'].replace('\r', ' ')
            jNew['subject'] = jNew['subject'].replace('\t', ' ')
            if nRead > nReadToday:
                # sent
                jNew['from'] = 'sid@rightwhen.com'
                jNew['body'] = 'To: ' + jEml['to'] + ' ' + jEml['text']
            else:
                # read
                jNew['from'] = jEml['from']
                # cleanse from
                jNew['from'] = jNew['from'].replace('\n', ' ')
                jNew['from'] = jNew['from'].replace('\r', ' ')
                jNew['from'] = jNew['from'].replace('\t', ' ')
                jNew['body'] = jEml['text']
            # cleanse body
            jNew['body'] = jNew['body'].replace('\n', ' ')
            jNew['body'] = jNew['body'].replace('\r', ' ')
            jNew['body'] = jNew['body'].replace('\t', ' ')
            
            # remove extra spaces
            jNew['body'] =  " ".join(jNew['body'].split())
            jNew['subject'] =  " ".join(jNew['subject'].split())
            jNew['from'] =  " ".join(jNew['from'].split())
                        
            # construct date/time
            # e.g. 2016-01-25T09:03:00
            nHour = random.randint(8, 20) 
            nMin = random.randint(0, 59)
            sDate = "2016-01-" + str(nStartDay + nDay) + "T" + "%02d" % nHour + ":" + "%02d" % nMin + ":00"
            
            jNew['date'] = sDate
            
            # debug
            # print json.dumps(jNew, sort_keys=True, indent=4, separators=(',', ': '))
            
            sOutputFile = args.outputdir + str(nRead) + '.json'
            
            # debug
            # print "generate_email.py: writing:", sOutputFile
            
            try:
                fo = open(sOutputFile, 'w')
            except Exception, e:                # to do: clean up
                f.close()
                sys.exit(e)
            # write the file
            try:
                json.dump(jNew,fo, sort_keys=True, indent=4, separators=(',', ': '))
            except Exception, e:
                sys.exit(e)
            fo.close()
            
            nGenerated = nGenerated + 1
            
            # to do: run these through BT ee???
            
        # end for
        print "generate_email.py: generated", nMessages, "messages for day", nDay
            
    # end for
        
    print "generate_email.py: generated", nGenerated, "messages for", nDays, "days"

# end main

#############################################    
    
if __name__ == "__main__":
    main(sys.argv)

# end