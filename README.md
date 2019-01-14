# SPR_Create_Dotmatics_ADLP_File
Project for processing SPR Data for upload to Dotmatics via ADLP

**Overview**

Takes SPR binding data and reformats the data into an Excel file for upload to Dotmatics through Broad's ADLP data upload portal.

## Environment Setup ([Skip](https://github.com/bfulroth/SPR_Create_Dotmatics_ADLP_File/blob/master/README.md#create-spr-setup-file-for-dose-response-experiment) this section if done before)
__Follow the steps below for initial setup. If initial setup was conducted previously, skip to next section of this document by clicking link above.__

_Take Note: The following procedure has been tested for Mac OS. Different commands are needed for Windows._

### Setup Python on your computer and download script files

1. Create a github.com account by clicking the following link. This is free. (https://github.com)
    - This is necessary in order to copy all of the files needed to run the SPR to ADLP scripts.
    - Another advantage is that any bugs fixed or changes made can be easily synced to your local hard drive.
2. Download and Install Anaconda with Python version 3.7 for Mac by clicking link. (https://www.anaconda.com/download/#macos)
    - Anaconda is a distribution of software packages that are very useful for data science.
    - With the Anaconda download, python version 3 or greater will be automatically installed. Mac OS comes with version 2.7 but this is an older version that may cause issues.
3. Create a new file folder on your hard drive titled "PythonProjects" using the terminal.
    1. Open Terminal.
        - Hold command + space to bring up spotlight search. Type 'terminal' and press 'return'.
    2. In terminal, create a new folder on your hard drive titled "PythonProjects". 
        - Type or copy/paste command: __mkdir PythonProjects__
        - Press 'return'
    3. In terminal navigate into "PythonProjects" by typing or copy/paste the command: __cd PythonProjects__
        - Press 'enter'
4. Fork this repo by clicking 'Fork' in the upper right corner of this webpage.
    - Forking means that all of the files necessary to run the SPR to ADLP scripts will be copied to your personal github account.
    - Later we will sync these files to your local hard drive in the PythonProjects folder you created above.
5. Once this repo is forked to your github account, navigate to the top project folder on github and click the green button 'Clone or download'. Next, click the button that looks like a clipboard to copy the link to your clipboard.
5. Navigate back to terminal.
6. Type command: __git clone 'paste contents of clipboard'__
7. Press 'return'
    - All the files needed should be copied to your local hard drive in the PythonProjects folder.
8. Navigate *into* the folder containing all of projects files. 
    - Type or copy/paste command: __cd SPR_Create_Dotmatics_ADLP_File__

### Create new Conda environment and install SPR to ADLP script dependencies.

 1. Navigate to terminal.
 2. Make sure you are in the SPR_Create_Dotmatics_ADLP_File file folder.
    - If your are not sure type command: cd ~
    - Press 'enter'
    - Type or copy/paste command: __cd PythonProjects__
    - Type or copy/paste command: __cd SPR_Create_Dotmatics_ADLP_File__
 3. Create and activate Conda Environment
    - Type or copy/paste command: 
    - conda create __--name SPR_ADLP_env --file /Users/*bfulroth*/PythonProjects/SPR_Create_Dotmatics_ADLP_File/SPR_ADLP_env.txt__
        - *Important: make sure to replace the user name italics with your own.*
    - Type or copy/paste command: __source activate SPR_ADLP_env__
    
## Create SPR setup file for dose response experiment

__Important__: For the data processing script to work, you must use the __Create_SPR_setup_file.py__ script described in this section.

__Important__: For the data processing script to work, you must save the Biacore run as: __yymmdd_PROJECTCODE_affinity__. No slashes for the date.

1. Navigate to the following folder using *Finder*: 
    - /Users/your_user_name/PythonProjects/SPR_Create_Dotmatics_ADLP_File/Example Files
    - Copy the file __181113_Cmpd_Setup_Example_Tbl.xlsx__ to another location on your hard drive. You can rename this file to anything you want.
    - Update the file with the information from your experiment.
    - Note:
        - The Files headers must not be changed.
        - The headers in __RED__ are used by the scripts and must be filled out. All others fields can be left blank (Although this is not a best practice).
2. Save the file above as a __.csv__ file.
3. In terminal, navigate to the __SPR_Create_Dotmatics_ADLP_File__ folder
    - Type command: cd ~
        - Press 'enter'
        - Type or copy/paste command: __cd PythonProjects__
        - Press 'enter'
        - Type or copy/paste command: __cd SPR_Create_Dotmatics_ADLP_File__
        - Press 'enter'
4. Make sure the the correct environment is activated.
    - Type or copy/paste command: __source activate SPR_ADLP_env__
    - Press 'enter'
5. Copy the complete file path for the setup table (remember it's a .csv file) you created in 1. above.
    - __Trick:__ 
        - To copy file or folder paths, right click on the file or folder and __hold__ the 'option' key. 
        - Next, select Copy "File Name" as Pathname.
6. Run the script
    - Type the command: __python Create_SPR_setup_file.py "Paste the contents of your clipboard"__ 
        - note: no quotes in command above just a space after py and then paste.
    - This should create the setup file on your desktop.
    
            
## Create ADLP upload file from Biacore dose response affinity experiment

__Important__ If your remove points during data analysis you must correct the setup table csv file to reflect the new top concentration.  This is necessary to correctly calculate the percent binding at the top concentration.

1. Create both affinity as well as kinetic analysis of the data in the SPR evaluation software.
2. Export both affinity as well as kinetic analysis.
    - Click on *affinity analysis* under 'Screening'
        - Right click on the sensorgram thumbnails and select 'Export All Graphs and Table'.
            - Save on Biacore hard drive.
      Click on *kinetic analysis* under 'Screening'.
        - Right click on the sensorgram thumbnails and select 'Export All Graphs and Table'
            - Save on Biacore hard drive.
3. Transfer both folders from 2. above to SPR image export folder on flynn. 
    - tdts_users/Informatics and computational research/SPR_Image_import/year_month
4. Navigate back to the Biacore evaluation software.
5. Export the 'Report Point Table'
    - Click on 'Report Point Table' under the Report Point Section.
    - Click File --> Export --> Results To Excel
    - Save this file either on flynn or on your hard drive. The name does not matter as long as it's an .xlsx file.
6. Navigate to the following folder using *Finder*: 
    - /Users/your_user_name/PythonProjects/SPR_Create_Dotmatics_ADLP_File/Example Files
    - Copy the Config.txt file to *__another location__* on your hard drive.
7. Update Config.txt for your experiment.
    - Open the Config.txt and replace all the paths as well as variables with those for your experiment.
    - __Trick:__ 
        - To copy file or folder paths, right click on the file or folder and __hold__ the 'option' key. 
        - Next, select Copy "File Name" as Pathname.
8. Run SPR_to_ADLP script
    - Navigate to the terminal
    - Make sure the the correct environment is activated.
        - Type or copy/paste command: __source activate SPR_ADLP_env__
        - Press 'enter'
    - Make sure you are in the folder containing the script.
        - If your are not sure type command: cd ~
        - Press 'enter'
        - Type or copy/paste command: __cd PythonProjects__
        - Type or copy/paste command: __cd SPR_Create_Dotmatics_ADLP_File__
     - Run the script
        - Copy the config file path name to the clipboard. See trick in __bold__ above.
        - Type command: __python SPR_to_ADLP.py__ 
        - Press 'enter'
        - Paste in the Config.txt path from the clipboard.
        - Press 'enter'
        - In the next prompt, name the results file. The name doesn't matter as long as it is *somthing.xlsx*
        - Press 'enter'
        - The upload file should be created on your desktop.
     - Manual Curation
        - The CURVE_VALID field needs to be fill in with 1 or 0.
            - 1: The data is *valid* and will be uploaded to Dotmatics.
            - 0: The data is *invalid* and will be excluded when uploading the file to Dotmatics through ADLP.
        - Comments
            - Under each cell there is a pull down menu with a list of comments to select from.
        - Other
            - It may be necessary to manually adjust the KD in the KD_SS field 
            __or__ if there is no binding remove the value in the KD_SS field.
            - It may be necessary to remove the stats
            - As a best practice, compounds that are *not saturating* should be reported as >top concentration - 1 dilution. e.g. >25
            - As a best practice, compounds that are *not saturating* should have all stats removed.
9. Upload file to ADLP
     
    
 
   
