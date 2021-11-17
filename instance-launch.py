import boto3
import os
import runansible
import time

def inputNumber(message):
  while True:
    try:
       userInput = int(input(message))       
    except ValueError:
       print("Not an integer! Try again.")
       continue
    else:
       return userInput 
       break 

def create_key_pair(x):
    ec2_client = boto3.client("ec2", region_name="eu-central-1")
    key_pair = ec2_client.create_key_pair(KeyName="%s" % x)

    private_key = key_pair["KeyMaterial"]

    # write private key to file with 400 permissions
    with os.fdopen(os.open("/tmp/%s.pem" % x, os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
        handle.write(private_key)

userId = str(input("Name of the user? "))
ec2_resource = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
info = {}

create_key_pair(userId)
ec2_instance = ec2_resource.create_instances(
    BlockDeviceMappings=[
        {
            'DeviceName': '/dev/xvda',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': 8,
                'VolumeType': 'gp2',
            },
        },
    ],
    ImageId='ami-0a49b025fffbbdac6',
    InstanceType='t2.micro',
    MaxCount=1,
    MinCount=1,
    SecurityGroupIds=[
        'sg-039f72687978812c8',
    ],
    Monitoring={'Enabled':False},
    KeyName="%s" % userId
)

ec2_instance_id = ec2_instance[0].id
print('Creating EC2 instance')
waiter = ec2_client.get_waiter('instance_running')
waiter.wait(InstanceIds=[ec2_instance_id])
print('EC2 Instance created successfully with ID: ' + ec2_instance_id)
ec2_instance[0].reload()
ec2_instance_ip = ec2_instance[0].public_ip_address
#ec2_instance_keyname = ec2_instance[0].keyname
info["id"] = str(ec2_instance_id)
info["ip"] = str(ec2_instance_ip)
info["key"] = str(userId)
print(info.values())

with open('inventory.txt', 'a') as f:
    f.write(info["id"] + " ansible_host=" + info["ip"] + " ansible_port=22 ansible_ssh_private_key_file=/tmp/" + info["key"] + ".pem \n")

with open('infos-connection.txt', 'a') as f:
    f.write(info["ip"] + " /tmp/" + info["key"] + ".pem \n")
time.sleep(20)
runansible.run_ansible(info["ip"])