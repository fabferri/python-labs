<properties
pageTitle= 'Azure Ubuntu VM dev tools, Python and packages'
description= "Azure Ubuntu VM dev tools, Python and packages"
services="Azure"
documentationCenter="https://github.com/fabferri/"
authors="fabferri"
editor=""/>

<tags
   ms.service="configuration-Example-Azure"
   ms.devlang="bash"
   ms.topic="article"
   ms.tgt_pltfrm="Azure"
   ms.workload="Azure"
   ms.date="06/12/2023"
   ms.author="fabferri" />

# Azure Ubuntu VM dev tools, Python and packages
The full deployment of the Azure Ubuntu VM can be done in steps:
1. Copy the bash scripts **create-vm.sh**, **dev.sh** to the Azure Cloud Shell storagedriver
2. Inside the Cloud Shell run the script **create-vm.sh**; this spins up the Ubuntu VM
3. Inside the CloudShell run the command **az vm run-command invoke** referencing the script **dev.sh**. The bash script **dev.sh** install: 
   - xrdp service to connect to the VM in RDP 
   - Ubuntu desktop 
   - Visual Studio Code
   - Chrome web browser
   - Python 
   - Visual Studio Code Python extension
   - Visual Studio Code Jupyter notebook extension
   - Python virtual environment package
   - Miniconda
   At the end, you will be able to connect to the Ubuntu in RDP.
4. Follow the discussion in this article to install Python packages by Miniconda in virtual environment.

## <a name="Spinning up the Azure Ubuntu VM"></a>1. Spinning up the Azure Ubuntu VM 
In the Azure management portal open the Azure Cloud Shell:

[![1]][1]

Using the button on the Cloud Shell menu, copy local files **create-vm.sh**, **dev.sh** to a Cloud Shell storagedriver: 

[![2]][2]


Moving bash script created in Windows to linux can cause an issue. Running the script, it might appear the messages: <br> 
**-bash: '\r': command not found** <br> 

**CR** = Carriage Return (**\r**) and **LF** = Line Feed (**\n**) are control characters, respectively coded 0x0D (13 decimal) and 0x0A (10 decimal). They are used to mark a line break in a text file. Windows uses two characters the **CR LF** sequence; Linux only uses **LF**. <br>
The error appearing in the Cloud Shell is caused by shell not able to recognise Windows-like **CRLF** line endings (0x0D 0x0A, \r\n) as it expects only **LF** (0x0A).<br>
It is possible in this case remove trailing CR (**\r**) character that causes this error:

```bash
sed -i 's/\r$//' create-vm.sh
sed -i 's/\r$//' dev.sh
```

Set the execution mode on the file:
```bash
chmod +x create-vm.sh
chmod +x dev.sh
```

Now we are ready to deploy the Azure VM. <br>
- **1<sup>st</sup> step:** in the Cloud Shell run **./create-vm.sh** 
- **2<sup>nd</sup> step:** in the Cloud Shell run **dev.sh** by Azure **Run Command**:
```bash
# Resource Group Name where is deployed the Azure VM
rgName='rg-2'

# Name of the Ubuntu VM
vmName='vm1'

# Run the scripts dev.sh in Ubuntu VM by using action Run Commands
az vm run-command invoke --name $vmName --resource-group $rgName --command-id RunShellScript --scripts @dev.sh --parameters ADMINISTRATOR_USERNAME
```
The **Run Command** feature uses the Azure VM agent to run shell scripts within an Azure Linux VM. <br>
The **dev.sh** installs Python and Miniconda. After installing, the script initialize the newly-installed Miniconda:
```
/home/USER_FOLDER/miniconda/bin/conda init bash
```

The bash script set up automatically the installation path: 
```
export PATH = $PATH:/home/ADMINISTRATOR_FOLDER/miniconda/bin
```


To verify the correct execution of **Run Command**, login in the VM and access to the folder **/var/lib/waagent/run-command/download/0/**: <br>
Check if there is any error in the files:
```bash
/var/lib/waagent/run-command/download/0/script.sh
/var/lib/waagent/run-command/download/0/stdout
/var/lib/waagent/run-command/download/0/stderr
```

## <a name="PyCharm Community Edition"></a>2. Install PyCharm Community Edition

PyCharm Community Edition is a free version of PyCharm <br>
Requirements: 
- RAM: 8GB
- Multi-core CPU
- at least 5 GB of free space

PyCharm requires Java Development Kit (JDK). <br> 
PyCharm supports virtual environments.  <br>
The list of download: https://www.jetbrains.com/pycharm/download/other.html  <br>

```bash
wget -P /tmp/ https://download.jetbrains.com/python/pycharm-community-2023.3.tar.gz
sudo mkdir /opt/pycharm-community/
sudo chmod 777 /opt/pycharm-community/
tar -zxvf /tmp/pycharm-community-*.tar.gz -C /tmp/
mv /tmp/pycharm-community-*/* /opt/pycharm-community/
rm -rf /tmp/pycharm-*

# link the executable to /usr/bin directory so that you can start PyCharm using the pycharm-community command from the terminal.
sudo ln -sf /opt/pycharm-community/bin/pycharm.sh /usr/bin/pycharm-community

#create a desktop entry to start PyCharm from the Activities menu
cat <<EOF > /usr/share/applications/pycharm-ce.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=PyCharm Community Edition
Icon=/opt/pycharm-community/bin/pycharm.svg
Exec="/opt/pycharm-community/bin/pycharm.sh" %f
Comment=Python IDE for Professional Developers
Categories=Development;IDE;
Terminal=false
StartupWMClass=jetbrains-pycharm-ce
StartupNotify=true
EOF
```

## <a name="virtual environment"></a>3. Virtual environments for Python with conda
virtual environment is a named, isolated, working copy of Python that that maintains its own files, directories, and paths so that you can work with specific versions of libraries or Python itself without affecting other Python projects. Virtual environments make it easy to cleanly separate different projects and avoid problems with different dependencies and version requirements across components. The conda command is the preferred interface for managing installations and virtual environments with the Anaconda Python distribution. <br>

| Description                  | conda command                                                                           |
| ---------------------------- | --------------------------------------------------------------------------------------- |
| Check conda version          | **conda -V**                   |
| Check Miniconda              | **conda info**                 |
| Update Miniconda             | **conda update --all**         |
| Create a virtual environment for your project|  **conda create --name myenv** <br> (replace myenv with the environment name) |
| Create an environment with a specific version of Python| **conda create --name myenv python=3.9**                            |
| Create an environment with a specific package| **conda create -n myenv scipy**                                               |
| Create an enviroment with a specific version of Python and add a specific package| **conda create -n myenv python** <br> **conda install -n myenv scipy** |
| Create an environment with a specific version of Python and multiple packages    | **conda create -n myenv python=3.9 scipy=0.17.3 astroid babel** |
| Make a silent installation      | **conda create -n myenv python=3.9 -y**        |
| Activate the virtual environment| **conda activate myenv** <br> After activation the prompt change into: <br> **(myenv) username@vm1:~$**|
| Deactivate an active environment| **conda deactivate myenv**        |
| Remove a deactivated environment| **conda env remove --name myenv** |
| exit/deactivate the virtual environment| **conda deactivate**       |
| List all the Conda environments| **conda env list** |
| List linked packages in a conda environment| **conda list** |
| If the environment is not activated, to see a list of all packages installed in a specific environment| **conda list -n myenv** |

> [!NOTE] 
> The **conda env remove** command deletes the environment's directory and all its contents. <br>
> In some cases, you may encounter a corrupted Conda environment that cannot be removed using the standard conda env remove command. In such cases, you can manually delete the environment by removing its directory from the envs folder in your Conda installation. <br>
>


- As best practice, in an <ins>activated environment</ins>, regularly update your packages using: **conda update --all** <br>
- Use conda environments for isolation; create a conda environment to isolate any changes pip makes.
   For this reason it is recommended use **pip** only after **conda**; install as many requirements as possible with conda then use **pip**. <br>
- Once **pip** has been used, conda will be unaware of the changes. To install additional conda packages, it is best to recreate the environment.
  Inside the virtual environment upgrade **pip**:
```bash
  pip install --upgrade pip
```

## <a name="Install Tensorflow"></a>4. Install Tensorflow in the virtual environment
Create a virtual environment and install tensorflow:
```bash
conda create -n myenv tensorflow
```
<br>
OR inside the virtual environment:
```
conda install tensorflow
```
<br>

Inside the virtual environment, verify the installation:
```bash
python -c "import tensorflow as tf; print(tf.reduce_sum(tf.random.normal([1000, 1000])))"
```


## <a name="Install PyTorch"></a>5. Install PyTorch in the virtual environment
Inside the virtual environment install from PyTorch channel:
```bash
conda update --all
conda install pytorch torchvision torchaudio -c pytorch
```
<br>

This will install the latest version of PyTorch, the torchvision and torchaudio packages. <br>
Verify the installation by running the following Python code:

```python
import torch
print(torch.__version__)
```
<br>

## <a name="Pandas"></a>6. Install Pandas in the virtual environment
```bash
conda install pandas
```
OR to make silent installations:
```bash
conda install -y pandas
```

## <a name="Matplotlib"></a>7. Install Matplotlib in the virtual environment
Inside the virtual enviroment, install Matplotlib. Matplotlib is available both via the anaconda main channel:
```bash
conda install matplotlib
```
or via the conda-forge community channel:
```bash
conda install -c conda-forge matplotlib
```

## <a name="Python version"></a>8. Python version installed out of virtual environment
The bash script **dev.sh** installed in the Ubuntu 22.04 the following release:
```bash
python --version
Python 3.11.5
```

`Tags: Python in Azure VM` <br>
`date: 06-12-23` <br>

<!--Image References-->
[1]: ./media/cloud-shell.png "start Cloud Shell"
[2]: ./media/copying-files.png "copying local files to the Cloud Shell storage account"

<!--Link References-->