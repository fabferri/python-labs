<properties
pageTitle= 'Starting with Azure SDK for Python'
description= "Starting with Azure SDK for Python"
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
   ms.date="01/12/2023"
   ms.author="fabferri" />

# First Python project with Azure SDK for Python
[Azure for Python](https://learn.microsoft.com/en-us/azure/developer/python/) documentation contains all the details required to use the Azure Python SDK. <br>
The purpose of this article is not to replace the official documentation, but a step-by-step for boost the starting. <br>


## <a name="Start with installation"></a>1. Install Visual Studio Code and Python in Windows

List of steps to get the Python environment ready on Windows. <br>
1. download and install [Visual Studio Code](https://code.visualstudio.com/)
2. download and install [Python](https://www.python.org/downloads/)  
3. install in VS Code the extensions **ms-python.python**. The  MS Python extension installs automatically Pylance extension **ms-python.vscode-pylance**:

[![1]][1]

[![2]][2]

You can get the list of installed VS extensions by command:
```powershell
code --list-extensions 
```

> NOTE
> In Windows the default installation paths for Python 3.12 are: 
> 
> **%LocalAppData%\Programs\Python\Python312**
> **%LocalAppData%\Programs\Python\Python312\Scripts** 
>
> Those paths need to be added to the PATH variable. <br>
> Type **sysdm.cpl** to open the **System Properties** <br>
> Go to the **Advanced** tab and then click-on the **Environment Variables…**  -> **System Variables** -> **PATH**


[![3]][3]

You should be able to install Python packages easily, by opening the Windows Command Prompt and then typing:
```
pip install package_name
```
and upgrade pip:
```
python -m pip install --upgrade pip
```

In Windows to check the Python version, open the command line and run:
```Console
py -3 --version 
```

## <a name="how to run Python code"></a>2. Create virtual environment and run Python code 
Create a folder and then open VS code:
```Console
mkdir test1
cd test1
code .
```

In VS Code, to create a virtual environment: 
- open the palette (CTRL+SHIT +P) and 
- in the search write **python**  
- select **"Python: Create environment"**
- select **venv**
- select the python version (3.12.0 in our case)

[![4]][4]

[![5]][5]

[![6]][6]

VS code starts the generation of virtual environment:

[![7]][7]

At the end of the process a folder **.vnev** is create in the project, as shown below:

[![8]][8]

> [!NOTE] 
> **Visual Studio Code does the activation of virtual environment automatically.** 
>

In windows, the virtual environment can be created by command:
```Console
py -3 -m venv .venv
```
or
```Console
python -m venv .venv
```

After the virtual environment is generated, use the following command to activate the virtual environment:
```Console
.venv\Scripts\activate
```
In the project folder write a simple Python code, sometime like:
```Python
msg="test"
for i in range (1, 10, 2): 
   print(msg, '-', i)
```
To run Python in VS you have couple of options:

[![9]][9]

[![10]][10]



## <a name="application service principal"></a>3. Create an application service principal
To interact by code with Azure resources, you need to establish and authenticate an identity using credentials. Azure SDK for Python provides different authentication methods. <br>
One of authentication method during development in local computer is to create dedicated <ins>application service principal objects</ins> . 
The identity of the service principal is then stored as environment variables to be accessed by the app when it's run in local development.
Application service principal objects are created with an app registration in Azure. 
In the Azure portal select all service and Identity:

[![11]][11]

Select **App registrations** and click-on **New registration**:

[![12]][12]

On the Register an application page, fill out the form as follows.
- **Name** → Enter a name for the app registration in Azure. 
- **Supported account types** → Accounts in this organizational directory only.

[![13]][13]


On the App registration page :
- **Application (client) ID** → This is the app id the app will use to access Azure during local development. Copy this value to a temporary location in a text editor as you will need it in a future step.
- **Directory (tenant) id** → This value will also be needed by your app when it authenticates to Azure. Copy this value to a temporary location in a text editor it will also be needed it in next steps.
- **Client credentials** → You must set the client credentials for the app before your app can authenticate to Azure and use Azure services. Select **Add a certificate or secret** to add credentials for your app.

[![14]][14]


On the Certificates & secrets page, select **+ New client secret**.

[![15]][15]

The Add a client secret dialog will pop out from the right-hand side of the page. In this dialog: <br>
- Description → Enter a value of Current. <br>
- Expires → Select a value of 24 months. <br>
Select Add to add the secret:

[![16]][16]


On the **Certificates & secrets** page, you will be shown the value of the client secret. <br>
Copy this value to a temporary location in a text editor as you will need it in  future steps. <br>
**IMPORTANT: This is the only time you will see this value. Once you leave or refresh this page, you will not be able to see this value again.** 

[![17]][17]

At this stage you have the following Azure elements can be used for authentication to the Azure resources:
- **Tenant ID**
- **Azure Subscription ID**
- **Application (client) ID**
- **Application (client) password**

## <a name="Assign a role to the application service principal"></a>3. Assign roles to the application service principal
You need to a roles (permissions) your application service principal. <br>
Roles can be assigned at a resource, resource group, or subscription scope. <br> This example shows how to assign roles at the Subscription scope.
Select the Azure subscription and then **Access control (IAM)**:

[![18]][18]

Click-on **Add** and then **Role assign**:

[![19]][19]

Select **Privileged administrator roles** and search for contributor; select contributor and click-on **Next** button:

[![20]][20]

In Assign access to, select **User, group or service principle** <br>
Click-on **+Select member** to add the application service principle defined before:

[![21]][21]

Select the application service principle:

[![22]][22]

The application service priciple has the role of Contributor and it can create any resource in the Azure subscription.

## <a name="environment variables"></a>4. Set local development environment variables
A way to scope the environment variables used to authenticate the application to Azure such it can only be used by this application, it can be done with python package **python-dotenv** <br>
The package **python-dotenv** allows to access to the environment from a **.env** file stored in the application's directory during development.
In the Python project create the **.env** file and store your environment variables in it:
```console
# Setting the environment variables
AZURE_SUBSCRIPTION_ID = '[YOUR SUBSCRIPTION ID]'
AZURE_TENANT_ID = '[YOUR TENANT ID]'
AZURE_CLIENT_ID = '[YOUR SERVICE PRINCIPAL APPLICATION (CLIENT) ID]'
AZURE_CLIENT_SECRET = '[YOUR SERVICE PRINCIPAL SECRET VALUE]'
```

[![23]][23]

> [!NOTE] 
> In the **.env** file replace the strings: <br>
> [YOUR SUBSCRIPTION ID] <br> 
> [YOUR TENANT ID] <br>
> [YOUR SERVICE PRINCIPAL APPLICATION (CLIENT) ID] <br> 
> [YOUR SERVICE PRINCIPAL SECRET VALUE]  <br>
> with values collected at time you created the application service principal.

<br>

In the virtual environment **python-dotenv** is installed by:
```console
pip3 install python-dotenv
```

Create a Python file **provision_rg.py** and paste the following code:
```python
import os
from dotenv import load_dotenv, find_dotenv

# load the environment variables from the file .env.
load_dotenv(find_dotenv())

# Retrieve  environment variables.
subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
client_id = os.getenv('AZURE_CLIENT_ID')
client_secret = os.getenv('AZURE_CLIENT_SECRET')
tenant_id = os.getenv('AZURE_TENANT_ID')

print("subscription ID: ", subscription_id)
print("tenant ID......: ", tenant_id)
print("client ID......: ", client_id)
print("client secret..: ", client_secret)
```
Running the Python will print the values of variables in **.env** file.  


## <a name="Install the Azure library packages"></a>4. Install the Azure library packages 
In the Python project create a new file named **requirements.txt** and paste the following content:
```console
azure-mgmt-resource>=18.0.0
azure-identity>=1.5.0
```
In a terminal prompt with <ins>the virtual environment activated</ins>, install the requirements:
```console
pip install -r requirements.txt
```

The virtual environment is now ready to create the Azure Resources.

## <a name="Create Azure ResourceGroup in Python"></a>5. Create an Azure Resource Group in Python

Replace the content of **provision_rg.py** with the following code:
```python
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
```
Run **provision_rg.py**


`Tags: Python, Visual Studio Code` <br>
`date: 20-11-23` <br>

<!--Image References-->

[1]: ./media/vs-python-extension.png "Visual Studio Python extension"
[2]: ./media/vs-pylance-extension.png "Visual Studio Pylance extension"
[3]: ./media/add-to-path.png "add the path to the Python binary files and lib"
[4]: ./media/virtual-env1.png "Create virtual enviroment"
[5]: ./media/virtual-env2.png "Create virtual enviroment"
[6]: ./media/virtual-env3.png "Create virtual enviroment"
[7]: ./media/virtual-env4.png "Create virtual enviroment"
[8]: ./media/virtual-env5.png "Create virtual enviroment"
[9]: ./media/run-python-in-vs-1.png "run Python code in VS code"
[10]: ./media/run-python-in-vs-2.png "run Python code in VS code"
[11]: ./media/service-principle01.png "create an application service principal"
[12]: ./media/service-principle02.png "create an application service principal"
[13]: ./media/service-principle03.png "create an application service principal"
[14]: ./media/service-principle04.png "create an application service principal"
[15]: ./media/service-principle05.png "create an application service principal"
[16]: ./media/service-principle06.png "create an application service principal"
[17]: ./media/service-principle07.png "create an application service principal"
[18]: ./media/assign-role01.png "Assing a role to the application service principal"
[19]: ./media/assign-role02.png "Assing a role to the application service principal"
[20]: ./media/assign-role03.png "Assing a role to the application service principal"
[21]: ./media/assign-role04.png "Assing a role to the application service principal"
[22]: ./media/assign-role05.png "Assing a role to the application service principal"
[23]: ./media/environment-variables.png "Environment variables in the file .env"

<!--Link References-->
