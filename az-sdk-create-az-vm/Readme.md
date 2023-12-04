<properties
pageTitle= 'Create an Azure VM with SDK for Python'
description= "Create an Azure VM with SDK for Python"
services="Azure SDK, Python"
documentationCenter="https://github.com/fabferri/"
authors="fabferri"
editor=""/>

<tags
   ms.service="configuration-Example-Azure"
   ms.devlang="Azure libraries for Python"
   ms.topic="article"
   ms.tgt_pltfrm="Azure"
   ms.workload="Azure SDK for Python"
   ms.date="02/12/2023"
   ms.author="fabferri" />

# Create an Azure VM with SDK for Python

The Python project uses Azure SDK management libraries to create a resource group that contains a Ubuntu VM. <br>
To setup Python and the local development environment see the steps described in [First Python project with Azure SDK](https://github.com/fabferri/python-labs/tree/main/1st-python-lab-az-sdk).

In Python project create a file  **requirement.txt** containing the list of mnagement libraries:
```Console
azure-mgmt-resource
azure-mgmt-compute
azure-mgmt-network
azure-identity
```

Then, in your windows terminal with the virtual environment activated, install the management libraries listed in **requirements.txt** by command:
```Console
pip install -r requirements.txt
```

Create a Python file named **provision_vm.py** with the following code:
```Python
# Import the needed credential and management objects from the libraries.
import os

from dotenv import load_dotenv, find_dotenv
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from datetime import datetime

# variables:
#   RESOURCE_GROUP_NAME: the resource group name
#   LOCATION: the region in which we provision resources
#   USERNAME: VM Administrator username
#   PASSWORD: VM administrator password
#   VM_SIZE: VM SKU
#   VNET_NAME: name of the Azure Virtual Network
#   SUBNET_NAME: name of the Azure subnet
#   IP_NAME: name of the IP Public Address associated with the VM
#   IP_CONFIG_NAME: name of the IP configuration
#   NIC_NAME: name of the NIC of the VM
#   NETWORK_SECURITY_GROUP: name of the Network Security Group
RESOURCE_GROUP_NAME = "az-vm1"
LOCATION = "westus2"
VM_NAME = "vm1"
USERNAME = "azureuser"
PASSWORD =  "myAdministratorPassword"
VM_SIZE = "Standard_B1s"
VNET_NAME = "vnet1"
SUBNET_NAME = "subnet1"
IP_NAME = VM_NAME + "-pubIP"
IP_CONFIG_NAME = VM_NAME + "-ipCfg"
NIC_NAME =  VM_NAME + "-nic"
NETWORK_SECURITY_GROUP = "nsg1"

# load the environment variables from the file .env
load_dotenv(find_dotenv())

# Retrieve subscription ID from environment variable.
subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
client_id = os.getenv('AZURE_CLIENT_ID')
client_secret = os.getenv('AZURE_CLIENT_SECRET')
tenant_id = os.getenv('AZURE_TENANT_ID')

print("subscription ID: ", subscription_id)
print("tenant ID......: ", tenant_id)
print("client ID......: ", client_id)
print("client secret..: ", client_secret)


print(
    "Provisioning an Azure VM...some operations might take a \
minute or two."
)

# Acquire credential object using the application service principle
credential = ClientSecretCredential(client_id=client_id, client_secret=client_secret,tenant_id=tenant_id) 

# Obtain the management object for resources, using the credetial from application service principle
resource_client = ResourceManagementClient(credential, subscription_id)


# Step1: Provision the resource group.
rg_result = resource_client.resource_groups.create_or_update(
    RESOURCE_GROUP_NAME, {"location": LOCATION}
)

now=datetime.now().strftime("%H:%M:%S")
print(
    f"{now} - Provisioned resource group: {rg_result.name} in the \
{rg_result.location} region"
)


# Obtain the management object for networks
network_client = NetworkManagementClient(credential, subscription_id)

# Step 2: provision a virtual network and wait for completion
poller = network_client.virtual_networks.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {"address_prefixes": ["10.0.0.0/16"]},
    },
)

vnet_result = poller.result()

now = datetime.now().strftime("%H:%M:%S")
print(
    f"{now} - Provisioned virtual network: {vnet_result.name} with address \
prefixes: {vnet_result.address_space.address_prefixes}"
)

# Step 3: Provision the subnet and wait for completion
poller = network_client.subnets.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    SUBNET_NAME,
    {"address_prefix": "10.0.0.0/24"},
)
subnet_result = poller.result()

now = datetime.now().strftime("%H:%M:%S")
print(
    f"{now} - Provisioned virtual subnet: {subnet_result.name} with address \
prefix: {subnet_result.address_prefix}"
)

# Step 4: Provision a public IP address and wait for completion
poller = network_client.public_ip_addresses.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": {"name": "Standard"},
        "public_ip_allocation_method": "Static",
        "public_ip_address_version": "IPV4",
    },
)

ip_address_result = poller.result()

now = datetime.now().strftime("%H:%M:%S")
print(
    f"{now} - Provisioned public IP address: {ip_address_result.name} \
with address {ip_address_result.ip_address}"
)

# Step 5: Provision the network interface client
poller = network_client.network_interfaces.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    NIC_NAME,
    {
        "location": LOCATION,
        "ip_configurations": [
            {
                "name": IP_CONFIG_NAME,
                "subnet": {"id": subnet_result.id},
                "public_ip_address": {"id": ip_address_result.id},
            }
        ],
    },
)

nic_result = poller.result()

now = datetime.now().strftime("%H:%M:%S")
print(f"{now} - Provisioned network interface card {nic_result.name}")


# Obtain the management object for virtual machines
compute_client = ComputeManagementClient(credential, subscription_id)

now = datetime.now().strftime("%H:%M:%S")
print(
    f"{now} - Provisioning virtual machine: {VM_NAME}; this operation might \
take a few minutes."
)

# Step 6: Provision the virtual machine
poller = compute_client.virtual_machines.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VM_NAME,
    {
        "location": LOCATION,
        "storage_profile": {
            "image_reference": {
                "publisher": "canonical",
                "offer": "0001-com-ubuntu-server-jammy",
                "sku": "22_04-lts-gen2",
                "version": "latest",
            }
        },
        "hardware_profile": {"vm_size": VM_SIZE},
        "os_profile": {
            "computer_name": VM_NAME,
            "admin_username": USERNAME,
            "admin_password": PASSWORD,
        },
        "network_profile": {
            "network_interfaces": [
                {
                    "id": nic_result.id
                }
            ]
        }
    },
)

vm_result = poller.result()

now = datetime.now().strftime("%H:%M:%S")
print(f"{now} - Provisioned virtual machine: {vm_result.name}")


# Step 7: Provision the network security group
print( f"{now} - Provisioning network security group: {NETWORK_SECURITY_GROUP}" )

poller = network_client.network_security_groups.begin_create_or_update( 
    RESOURCE_GROUP_NAME,
    NETWORK_SECURITY_GROUP,
    {
        "location": LOCATION,
         "securityRules": [
          {
            "name": "SSH-rule",
            "properties": {
              "description": "allow SSH",
              "protocol": "Tcp",
              "sourcePortRange": "*",
              "destinationPortRange": "22",
              "sourceAddressPrefix": "*",
              "destinationAddressPrefix": "VirtualNetwork",
              "access": "Allow",
              "priority": 200,
              "direction": "Inbound"
            }
          },
          {
            "name": "RDP-rule",
            "properties": {
              "description": "allow RDP",
              "protocol": "Tcp",
              "sourcePortRange": "*",
              "destinationPortRange": "3389",
              "sourceAddressPrefix": "*",
              "destinationAddressPrefix": "VirtualNetwork",
              "access": "Allow",
              "priority": 300,
              "direction": "Inbound"
            }
          }
        ]
    }
)

nsg_result = poller.result()

now = datetime.now().strftime("%H:%M:%S")
print(f"{now} - Provisioned network security group: {nsg_result.name}")

poller = network_client.subnets.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    SUBNET_NAME,
    {
        "address_prefix": "10.0.0.0/24",
        "networkSecurityGroup": {
            "id": nsg_result.id
        }
    }
)
subnet_result = poller.result()

now = datetime.now().strftime("%H:%M:%S")
print(f"{now} - added nsg to the subnet: {subnet_result.name}")
```
<br>

> [!NOTE]
> Before running the **provision_vm.py** code:
> 1. set the right value of administrator password in the variable **PASSWORD**.
> 2. set the values of variables (application service principle, Tenant, Subscription) in the file **.env**


`Tags: Python, Visual Studio Code` <br>
`date: 02-12-23` <br>

<!--Image References-->

<!--Link References-->
