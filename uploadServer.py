
import subprocess
subprocess.check_call(["python", '-m', 'pip', 'install', 'paramiko'])
import paramiko
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname='169.254.222.19', username='pi',password='raspberry')
ftp_client=ssh_client.open_sftp()
ftp_client.put('server.py','server.py')
ftp_client.close()
ssh_client.close()
