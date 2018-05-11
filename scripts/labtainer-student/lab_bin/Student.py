#!/usr/bin/env python
'''
This software was created by United States Government employees at 
The Center for the Information Systems Studies and Research (CISR) 
at the Naval Postgraduate School NPS.  Please note that within the 
United States, copyright protection is not available for any works 
created  by United States Government employees, pursuant to Title 17 
United States Code Section 105.   This software is in the public 
domain and is not subject to copyright. 
'''

# Student.py
# Description: Create a zip file containing the student's lab work
# Also kill any lingering monitored processes

import glob
import os
import subprocess
import sys
import zipfile
import datetime


def killMonitoredProcess(homeLocal):
    cmd = "ps x -o \"%r %c\" | grep [c]apinout | awk '{print $1}' | uniq"
    child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    done = False
    #print("cmd was %s" % cmd)
    while not done:
        line = child.stdout.readline().strip()
        #print('got line %s' % line)
        if len(line)>0:
            cmd = 'kill -TERM -%s' % line
            print('cmd is %s' % cmd)
            os.system(cmd)
        else:
            done = True
    kill_proc = os.path.join(homeLocal, 'bin', 'killproc')
    if os.path.isfile(kill_proc):
        with open(kill_proc) as fh:
            for line in fh:
                cmd = 'pkill %s' % line
                os.system(cmd)

def main():
    #print "Running Student.py"
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: Student.py <username> <image_name>\n")
        return 1


    user_name = sys.argv[1]
    container_image = sys.argv[2].split('.')[1]
    studentHomeDir = os.path.join('/home',user_name)
    homeLocal= os.path.join(studentHomeDir, '.local')
    killMonitoredProcess(homeLocal)
    os.chdir(studentHomeDir)
    student_email_file=os.path.join(homeLocal, '.email')
    lab_name_file=os.path.join(homeLocal, '.labname')
    if not os.path.isfile(student_email_file):
        print('No email file at %s, exit.' % student_email_file)
        return 1
    fh = open(student_email_file)
    student_email = fh.read().strip()
    fh.close()
    fh = open(lab_name_file)
    lab_name = fh.read().strip()
    fh.close()
    # NOTE: Always store as e-mail+lab_name.zip
    #       e-mail+lab_name.zip will be renamed by stop.py (add containername)
    zipFileName = '%s.%s.zip' % (student_email.replace("@","_at_"), lab_name)

    #print 'The lab name is (%s)' % LabName
    #print 'Output zipFileName is (%s)' % zipFileName
    homeLocal = os.path.join(homeLocal, 'zip')
    if not os.path.isdir(homeLocal):
        os.makedirs(homeLocal)
    OutputName=os.path.join(homeLocal, zipFileName)
    TempOutputName=os.path.join("/tmp/", zipFileName)
    # Remove temp zip file and any zip file in homeLocal
    if os.path.exists(TempOutputName):
        os.remove(TempOutputName)
    if os.path.exists(OutputName):
        os.remove(OutputName)
    zip_filenames = glob.glob('%s*.zip' % homeLocal)
    for zip_file in zip_filenames:
        #print "Removing %s" % zip_file
        os.remove(zip_file)
    
    # Note: Use /tmp to temporary store the zip file first
    # Create temp zip file and zip everything under studentHomeDir
    zipoutput = zipfile.ZipFile(TempOutputName, "w")
    udir = "/home/"+user_name
    skip_list = []
    manifest = '%s-home_tar.list' % container_image

    no_skip = os.path.join(udir,'.local','bin', 'noskip')
    no_skip_list = []
    if os.path.isfile(no_skip):
        with open(no_skip) as fh:
            for line in fh:
                no_skip_list.append(line.strip())

    skip_file = os.path.join(udir,'.local','config', manifest)
    if os.path.isfile(skip_file):
        fh = open(skip_file) 
        for line in fh:
            if os.path.basename(line.strip()) not in no_skip_list:
                skip_list.append(line.strip())
        fh.close()
    dt_skip_list = {}
    dt_skip_file = os.path.join(udir,'.local','config', 'mytar_list.txt')
    if os.path.isfile(dt_skip_file):
        fh = open(dt_skip_file) 
        for line in fh:
            parts = line.split()
            if len(parts) < 6:
                print('Bad mytar_list entry %s' % line)
                continue
            fname = parts[5]
            if os.path.basename(fname).strip() not in no_skip_list:
                dt_string = parts[3]+' '+parts[4]
                dt = datetime.datetime.strptime(dt_string, "%Y-%m-%d %H:%M")
                dt_skip_list[fname] = dt
    for rootdir, subdirs, files in os.walk(studentHomeDir):
        newdir = rootdir.replace(udir, ".")
        for fname in files:
            savefname = os.path.join(newdir, fname)
            #print "savefname is %s" % savefname
            try:
                local_time = datetime.datetime.fromtimestamp(os.path.getmtime(savefname))
            except OSError:
                ''' ephemeral '''
                continue 
            local_time = local_time.replace(minute=0)
            ckname = savefname[2:]
            if ckname not in skip_list:
                if ckname not in dt_skip_list or dt_skip_list[ckname] < local_time: 
                    try:
                        zipoutput.write(savefname, compress_type=zipfile.ZIP_DEFLATED)
                    except:
                        # do not die if ephemeral files go away
                        pass
    zipoutput.close()
   
    os.chmod(TempOutputName, 0666)

    # Rename from temp zip file to its proper location
    os.rename(TempOutputName, OutputName)
    '''
    # Store 'OutputName' into 'zip.flist' 
    zip_fname = os.path.join(homeLocal, 'zip.flist')
    zip_flist = open(zip_fname, "w")
    zip_flist.write('%s ' % OutputName)
    zip_flist.close()
    os.chmod(zip_fname, 0666)
    '''
    return 0

if __name__ == '__main__':
    sys.exit(main())

