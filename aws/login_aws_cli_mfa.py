import argparse
import subprocess
import json
import configparser

parser = argparse.ArgumentParser(prog='login_aws_cli_mfa')

parser.add_argument('otpcode')

args = parser.parse_args()

awscliObject = subprocess.run('aws sts get-session-token --serial-number arn:aws:iam::794382686957:mfa/BitWarden --token-code ' + args.otpcode, capture_output=True)
if(awscliObject.returncode != 0):
    print("Could not login via MFA (token-code invalid, arn invalid)")
    exit(-1)

credentialsObject = json.loads(awscliObject.stdout)['Credentials']

config = configparser.ConfigParser()
credentialsFilePath = 'c:/Users/Schlechtwegt/.aws/credentials'
config.read(credentialsFilePath)

config['mfa']['aws_access_key_id'] = credentialsObject['AccessKeyId']
config['mfa']['aws_secret_access_key'] = credentialsObject['SecretAccessKey']
config['mfa']['aws_session_token'] = credentialsObject['SessionToken']

with open(credentialsFilePath, 'w') as credentialsFile:
    config.write(credentialsFile)
    
print("Login successful.")