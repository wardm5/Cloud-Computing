import os
import boto3
from boto3.session import Session
from datetime import datetime
from dateutil import tz
import os.path, time
from dateutil.parser import parse

                #########################################################################################
                #                                                                                       #
                #                             --- AWS Backup App ---                                    #
                #       This program asks the user for a directory and then backs up that               #
                #       directory to the AWS cloud. Several checks are done to ensure the user          #
                #       provides correct input and ensure that new files have been modified before      #
                #       uploading them again.                                                           #
                #                                                                                       #
                #########################################################################################

def main():
    # session = Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    # path = "/Users/MishaWard/Desktop/myGitHub/Machine_Learning"
    bucket_name = "mishaward2462890"    # default bucket name
    bucket_name = intro(bucket_name)                  # intro
    # s3 = Session.resource("s3")
    s3 = boto3.resource("s3")           # sets up connection to s3
    d = s3_bucket_check(bucket_name, s3)      # checks if bucket exists, if it does returns map of files and uploaded date stamps
    path = user_file_input()  # user input for file directory
    total = total_files(path)                   # calculates the total files (less hidden) in the directory
    upload(path, total, bucket_name, s3, d)   # uploads the the files to AWS

def intro(bucket_name):
    print("\nHello, welcome to the AWS backup app! ")
    print("Currently, the default bucket name is: " + bucket_name + "\n")
    answer = ""
    while answer.lower() not in  ("yes", "no"):
        answer = input("Do you want to provide your own bucket name? Please write 'yes' or 'no'. ")
    if answer.lower() in "yes":
        return input("Provide unique bucket name here: ")
    else:
        return bucket_name

def user_file_input():
    check = False
    while not check:        # while not True
        path = input("What is the file path of the directory? ")  # ask for user input of directory
        check = os.path.exists(path) and os.path.isdir(path)  # check if path exists
        if check:                     # if the path exists
            return path               # return the path
        else:                         # else...
            print("Incorrect path entered. Please re-enter a correct path to folder. ")  # print error message

def s3_bucket_check(bucket_name, s3):
    print("Checking AWS to see if you have a bucket. ")
    for bucket in s3.buckets.all():            # for each bucket in all buckets
        if bucket.name == bucket_name:     # if bucket matches existing bucket name in AWS
            print("Bucket already exists. ")  # tell user bucket exists
            d = map_creation(bucket_name, s3)
            return d                 # return map

    try:
        s3.create_bucket(Bucket=bucket_name)              # have AWS create bucket with name
        print("\nCreating a new bucket: ", bucket_name)  # else print creating a new bucket
    except Exception as e:
        print("Bucket already exists, please retry.")
        main()
        exit()
    print("A bucket named " + bucket_name + " has been created in AWS. ")  # tell user the bucket was created
    return None  # return null

def total_files(path):
    total = 0
    for root, dirs, files in os.walk(path):  #for all directories, files, in the path
        sumFiles = [f for f in files if not f[0] == '.']  # for each of the files that dont start with . (hidden files)
        total = len(sumFiles) + total                     # calculate the total number of files
        dirs[:] = [d for d in dirs if not d[0] == '.']    # for each directory that doesnt start with . (hidden files)
    return total  # return number of files to be transferred

def upload(path, total, bucket_name, s3, d):
    count = 1  # set count of files to 0
    print("\nStarting the uploading process to AWS for " + str(total) + " files. \n")
    for root, dirs, files in os.walk(path):  # for all directories and files, walk through file structure
        files = [f for f in files if not f[0] == '.']  # compress files into list (filter hidden files out)
        dirs[:] = [d for d in dirs if not d[0] == '.']  # compress directories into list (filter hidden files out)
        for file in files:
            for root, dirs, files2 in os.walk(path):  # for each directory and file in file structure that is not hidden
                for name in files2:  # for each file in files
                    if name == file: # if the file name is equal to the file
                        full_path = os.path.abspath(os.path.join(root, name))  # get the full path to the file
                        if not bool(d):  # if dictionary is empty... (all files need to be uploaded)
                            print("Uploading file " + str(count) + " out of " + str(total) + ".      " + full_path)   # prints out file number out of total files and full path
                            count = count + 1
                            s3.Object(bucket_name, full_path).put(Body=open(full_path, "rb"))  # upload file to s3
                        elif full_path not in d:  # case when file has been added to folder after last modifcation
                            print("Uploading file " + str(count) + " out of " + str(total) + ".      " + full_path)   # prints out file number out of total files and full path
                            count = count + 1
                            s3.Object(bucket_name, full_path).put(Body=open(full_path, "rb"))  # upload file to s3
                        else:  # else (for cases where files were already uploaded and now need to check if they have been modified
                            file_time = datetime.fromtimestamp(os.path.getmtime(full_path))  # check the file datestamp
                            file_comptime = file_time.strftime("%Y-%m-%d %H:%M:%S")  # set file datestamp str format
                            aws_mod_time = d.get(full_path, None)    # get aws last modified time (str)
                            file_comptime = datetime.strptime(file_comptime, "%Y-%m-%d %H:%M:%S")  # convert to date object
                            aws_mod_time = datetime.strptime(aws_mod_time, "%Y-%m-%d %H:%M:%S")    # convert to date object
                            if file_comptime > aws_mod_time:  # check if file time is greater than AWS modified time
                                print("File has been modified after backup, replacing file in progress.")
                                count = count + 1
                            else:  # if AWS modifed time is the latest... alert user that nothing was backed up
                                print("File has not been modified since last backup and has not been uploaded to AWS, file " + str(count) + " out of " + str(total) + ". ")
                                count = count + 1
                                continue
                            print("Files " + str(count) + " out of " + str(total) + ".      " + full_path)  # prints out file number out of total files and full path
                            count = count + 1
                            s3.Object(bucket_name, full_path).put(Body=open(full_path, "rb"))
    if not bool(d):
        print("\nComplete: " + str(total) + " out of " + str(total) + " files uploaded successfully. Please check AWS to review files. ")
    else:
        print("\nComplete: " + str(total) + " out of " + str(total) + " files where checked for updates successfully. Please check AWS to review files. ")

def map_creation(bucket_name, s3):
    d = {}  # create dictionary
    bucket = s3.Bucket(bucket_name)  # get specific bucket
    for key in bucket.objects.all():  # for all keys in bucket
        from_zone = tz.gettz('UTC')  # set timezone of AWS modifed dates
        to_zone = tz.gettz('US/Pacific')  # set conversion timezone
        date = str(key.last_modified)[:-6]  # modify the date
        utc = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")  # create date object
        utc = utc.replace(tzinfo=from_zone)  # replace the timezone
        date = utc.astimezone(to_zone)  # set timezone
        d[key.key] = date.strftime("%Y-%m-%d %H:%M:%S")  # add date to the value of the dictionary
    return d  # return dictionary

main()
