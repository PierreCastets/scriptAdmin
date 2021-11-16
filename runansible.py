import os

def run_ansible(x):
    bashCommand = "ssh-keyscan -H %s >> ~/.ssh/known_hosts" % x
    os.system(bashCommand)
    bashCommand = "ansible-playbook -i inventory.txt ./playbook.yml"
    os.system(bashCommand)