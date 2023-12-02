# Import the needed credential and management objects from the libraries.
import os

from dotenv import load_dotenv, find_dotenv
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient

load_dotenv(find_dotenv())

# System call
os.system("")
# Class of different styles
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

# Retrieve subscription ID from environment variable.
subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
client_id = os.getenv('AZURE_CLIENT_ID')
client_secret = os.getenv('AZURE_CLIENT_SECRET')
tenant_id = os.getenv('AZURE_TENANT_ID')

print("subscription ID: "+ style.YELLOW, subscription_id, style.RESET)
print("tenant ID......: "+ style.YELLOW, tenant_id, style.RESET)
print("client ID......: "+ style.CYAN, client_id, style.RESET)
print("client secret..: "+ style.CYAN, client_secret, style.RESET)


# Acquire a credential object using CLI-based authentication.
#credential = AzureCliCredential()
credentials = ClientSecretCredential(client_id=client_id, client_secret=client_secret,tenant_id=tenant_id) 

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credentials, subscription_id)

# Provision the resource group.
rg_result = resource_client.resource_groups.create_or_update(
    "PythonAzureExample-rg", {"location": "centralus"}
)

# Within the ResourceManagementClient is an object named resource_groups,
# which is of class ResourceGroupsOperations, which contains methods like
# create_or_update.
#
# The second parameter to create_or_update here is technically a ResourceGroup
# object. You can create the object directly using ResourceGroup(location=
# LOCATION) or you can express the object as inline JSON as shown here. For
# details, see Inline JSON pattern for object arguments at
# https://learn.microsoft.com/azure/developer/python/sdk
# /azure-sdk-library-usage-patterns#inline-json-pattern-for-object-arguments

print(
    f"Provisioned resource group {rg_result.name} in \
        the {rg_result.location} region"
)

# The return value is another ResourceGroup object with all the details of the
# new group. In this case the call is synchronous: the resource group has been
# provisioned by the time the call returns.

# To update the resource group, repeat the call with different properties, such
# as tags:
rg_result = resource_client.resource_groups.create_or_update(
    "PythonAzureExample-rg",
    {
        "location": "centralus",
        "tags": {"environment": "test", "department": "tech"},
    },
)

print(f"Updated resource group {rg_result.name} with tags")

# Optional lines to delete the resource group. begin_delete is asynchronous.
# poller = resource_client.resource_groups.begin_delete(rg_result.name)
# result = poller.result()