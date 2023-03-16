# Personal Project - JDR Tool Introduction
Content: JDR Tool Introduction (Job Dependency Runner)

**Preface**:
I recently started learning Python, so I tried to write this project as an exercise. The idea of the concept is derived from the solution to the difficulties encountered when helping the Ministry of Finance to develop the system. Share it here.

![](https://i.imgur.com/sg1lCzG.png)
<center>Figure 1. Appearance of JDR tool</center>

![](https://i.imgur.com/V1Qri4h.gif)
<center>Figure 2. Using JDR tools to execute and manage programs</center>

---
# 1. Motivation of the Project

JDR (Job Dependency Runner) is a set of small data governance tools developed by this project. In short, it is a set of "programs used to assist in the execution and management of programs".

At work, the action of "executing a program" is not particularly difficult in most cases. Usually, you edit the command first, then throw it into the shell, or an interface/platform, and then wait for the result to come out. Will use tools like crontab to pre-schedule.

With this method, if the scale is only one or two to a dozen programs, there may be no problem, but if there are hundreds or thousands of programs, it will be difficult to manage. The reason lies in the management issues derived from "quantity" and "dependency"

These management issues include: "What is the current state of the program?", "What is the sequence of program execution?", "If a certain program needs to be re-run, will it affect which downstream related programs?" When the number of programs is larger, it is less likely to be managed by the engineer's memory. Even if the records are assisted by files, maintenance and searching will take time and cost.

And because data analysis has become more and more important in recent years, the data governance issue of "whether the program is executed correctly and on time" has also been paid more and more attention. In order to solve these issues, I hope to implement a set of tools in this project, so that some management issues can be automated, dashboarded, and the results are presented in a visual way.

Maybe this project will overlap with some ETL tools (such as: SSIS, Trinity, DataStage, Automation) in function, because ETL tools also have the function of executing and managing programs, but because I haven't found a tool that can meet the needs , so that's another reason why I decided I wanted to develop my own.

I hope that users only need to maintain a work list (Excel format), and then after inputting the list into this tool, a graphical program dependency flow chart can be automatically generated. The graphical program dependency flowchart is a kind of DAG (Directed Acyclic Graph). After having a graph, many issues arise about how to operate it. I try to simplify these operations as much as possible, so that these operations and management behaviors can be easily performed only by making a setting on the graphical interface, pressing a button, and viewing a report.

Everyone is welcome to use this set of tools, but the design of the tools is based on my personal previous development experience and my own imagination, so if someone thinks that it is not easy to use, inconvenient, or not flexible enough, please feel free to feed these questions back to me, so that I can use them as a reference for improvement.


---

## 2. Use the Package & Authorization & Link:

The development of this project mainly uses the following python packages:

* PyQt: GUI programming (GNU GPL license)
* graphviz: draw flowcharts (EPL license)
* networkx: graph operations (BSD license)
* pandas: data reading and manipulation (BSD license)
* matplotlib: generate graphs (BSD license)

For the choice of software license for this project, I personally prefer the most free BSD license, but because the PyQt suite itself is a relatively strict GNU GPL license, I have to follow the GPL.

Links related to this project are as follows:

* Source code: https://github.com/Chen-Alfred/JDR
* Execution file: https://github.com/Chen-Alfred/JDR/tree/main/dist
* Documentation (English): https://hackmd.io/xsLDRVAMTF2gO0YHo3lxYw
* Documentation (Traditional Chinese): https://hackmd.io/GK-JknSJRnejy1CsYF5mcg


---

## 3. The Operating Structure of Using JDR Tool:
 
![](https://i.imgur.com/VbsRwyB.png)


**<center>Operational structure and related roles of using JDR tool</center>**

The relevant roles of the JDR tool operating framework are described as follows:
  * **Manager** : The manager who maintains the job list document should immediately update the document whenever a job is added or modified, or the execution rules are changed. It is recommended that someone in the organization who is familiar with program execution rules be employed, such as project managers and data modelers.
  * **Job list document** : A list document that records all jobs in the organization, written in Excel format, and maintained by the manager. For the format, please refer to the section " 4. Job list document ". In addition, the JDR tool also provides error checking for files, please refer to the section " Error checking for job list document ".
  * **Developer** : The engineer who develops the job within the organization. Each job must be developed according to certain specifications, and the execution status is registered and updated in the control table during execution.
  * **Job** : The program written by the developer must follow certain specifications during development, and register and update the execution status with the control table during execution. For details, please refer to the section " 5. Definitions of Programs, Operations, and Execution Items ".
  * **Control table database** : It is used to store the real-time status and information when the job is executed, and it is consolidated by the JDR tool and presented on the screen for user reference. There is only one control table. For details, please refer to the section " 6. Control table format and operation development principles ". For some flexible settings of the control table, you can refer to the section " Flexible Settings of the Control Table ".
  * **JDR tool** : The data governance tool used in this project. According to the settings in the job list document and the settings in the  control table, the dependencies and execution order of each job are presented on the screen in a visual way, and the user can understand all the jobs in a dynamic and interactive way for operation and management, it also provides report function to allow users to view the execution results. For details, please refer to the section " 7. How to use JDR tools ".

---

## 4. Job List Document
### (1). Field Description
Before using the JDR tool, a job list document must be maintained. This file is in Excel file format and must contain all the fields in the following table:

**<center>Field Descriptions for Job List Document</center>**
| # | Field name | Note |
| --| ---------- | -------- |
| 1 | job_no   | Arbitrary number assigned to the job, so that users can find it easily, either a number or a character string can be used.     |
| 2 | job_type | The category assigned to the job, the user can arbitrarily classify according to his own rules.     |
| 3 | job_name | The name of the job.     |
| 4 | job_freq | For the regular description of the execution time of the job, if there are multiple execution frequencies, please separate them with line break characters. This field is related to "Plan Execution Time", please refer to the section " About Execution Frequency "     |
| 5 | job_src  | The upstream jobs of this job. If there are multiple upstream jobs, please separate them with line break characters. This field is related to job dependency, please refer to " About job dependency ".   |
| 6 | job_not  | If the job is not actually required, please write "Y" in this column.     |
| 7 | job_cmd  | For the actual execution command of the job, provide the reserved word "${PLANDT}" as the plan execution time.     |

PS: The order of appearance of the fields may not follow the above table, but each field must be present.

### (2).About Execution Frequency
"Execution frequency" actually has two meanings:
1. **Describe regular behavior** : For example, when a program is designed to be "executed daily", "executed on the 1st of each month", and "executed on January 1st of each year", it means that it has a regular execution cycle. The description syntax can be described in the format of the following table in the job list document.
2. **Determine a specific time** : When the "execution frequency" occurs within a period of time, some specific time points can be determined. For example, if a program is "executed on the 1st of each month", then in the whole year of 2023 AD, the program will run on 2023-01-01, 2023-02-01, 2023-03-01...2023-12-01, these specific times are called "**plan execution time**" in this project .

**<center>The "job_freq" field of the job list document</center>**
| # | Examples of execution frequency expressions | Meaning |
| -------- | -------- | -------- |
| 1 | YYYYMMDD            | Every day (00:00:00)     |
| 2 | YYYYMMDD 080000     | Every day (08:00:00)     |
| 3 | YYYYMM01            | 1st of every month (00:00:00)     |
| 4 | YYYYMM05 120000     | 5th of every month (12:00:00)     |
| 5 | YYYYMM$$            | Last day of every month (00:00:00)     |
| 6 | YYYYMM$$ 233000     | Last day of every month (23:30:00)     |
| 7 | YYYY1025            | Every October 25th (00:00:00)     |
| 8 | YYYY1201 173000     | Every December 1st (17:30:00)     |
| 9 | YYYY02$$            | Every year on the last day of February (00:00:00)     |
| 10 | YYYY02$$ 180000    | Every year on the last day of February (18:00:00)     |
| 11 | 20200101           | Specific time: 2020-01-01 (00:00:00)     |
| 12 | 20221231 235900    | Specific time: 2022-12-31 (23:59:00)     |
| 13 | YYYY1301           | Format error (no 13th month)     |
| 14 | YYYYMM32           | Format error (no 32nd day)     |
| 15 | YYYYMMDD 250000    | Format error (no 25th hour)     |
| 16 | YYYYMMDD 0800      | Format error (wrong time format)     |
| 17 | YYYYMMDD 08        | Format error (wrong time format)     |
| 18 | YYYY$$01           | Format error ($$ can only be used to represent dates)     |
| 19 | YYYYMMDD-120000    | Format error (delimiter characters other than white space are not allowed between date and time)     |
| 20 | DDMMYYYY           | Format error (the description method does not conform to the definition, only the order of "year, month, day, hour, minute, second" is accepted)     |

### (3). About Job Dependency
"Job dependency" include two types:
1. **Intra-job dependency** : When a single job must be executed at multiple plan execution times within a period of time, the sequence of plan execution times must be followed.
2. **Inter-job dependency** : The dependency between different jobs is set according to the "job_freq" field in the job list document (delimited by line break characters). If an item (or job) has its upstream job with multiple planned execution times, select the upstream job that is no later than and closest to the plan execution time of the job.

### (4). Examples
**1. Example 1 (no dependency)** : 
The following takes 4 jobs as an example without any dependencies among them. You can set the job list document as follows:

| job_no | job_type | job_name | job_freq | job_src | job_not | job_cmd |
| ---- | ---- | ---- | -------- | ---- | ---- | ---- |
| 1 | test | Job1 | YYYYMMDD |      |    | ```python runjob.py Job1 ${PLANDT}``` |
| 2 | test | Job2 | YYYYMMDD |      |    | ```python runjob.py Job2 ${PLANDT}``` |
| 3 | test | Job3 | YYYYMMDD |      |    | ```python runjob.py Job3 ${PLANDT}``` |
| 4 | test | Job4 | YYYYMMDD |      |    | ```python runjob.py Job4 ${PLANDT}``` |

Set the start and end time to the same day (2023-01-01 in this example), and you can get the following figure. At this time, the four jobs are independent, and there is no order of execution.
![](https://i.imgur.com/Vow73nG.png)

**Example 2 (intra-job dependency)** : 
use the same job list document settings in Example 1, but set the start and end time from 2023-01-01 to 2023-01-02, then you can get the following figure, at this time only there are intra-job dependencies, but no inter-job dependencies. It means that the four jobs are independent, but the jobs of 2023-01-01 must be executed before the jobs of 2023-01-02 is executed.
![](https://i.imgur.com/HVhFhFW.png)

**3. Example 3 (Inter-job dependency)** : 

The following is an example of 4 jobs, which are dependent on each other. The job list document can be set as follows:

| job_no | job_type | job_name | job_freq | job_src | job_not | job_cmd |
| ---- | ---- | ---- | -------- | ---- | ---- | ---- |
| 1 | test | Job1 | YYYYMMDD |      |    | ```python runjob.py Job1 ${PLANDT}``` |
| 2 | test | Job2 | YYYYMMDD | Job1 |    | ```python runjob.py Job2 ${PLANDT}``` |
| 3 | test | Job3 | YYYYMMDD | Job1 |    | ```python runjob.py Job3 ${PLANDT}``` |
| 4 | test | Job4 | YYYYMMDD | Job2<br>Job3 |    | ```python runjob.py Job4 ${PLANDT}``` |

Set the start and end time to the same date (2023-01-01 in this example), and you can get the following figure. At this time, the execution order of these 4 jobs must follow the dependency setting: Job2 and Job3 can only be executed after Job1 is executed. Job4 can only be executed after both Job2 and Job3 are executed.
![](https://i.imgur.com/EXL6PPM.png)

**4. Example 4 (Inter-job Dependency + Intra-job Dependency)** : 
Use the same job list document settings in Example 3, but limit the start and end time to 2023-01-01 to 2023-01-02, then you can get the following Figure, at this time, there are inter-job dependency and intra-job dependency.
![](https://i.imgur.com/pwxjPuv.png)


---

## 5. Definitions of Program, Job, and Execution Item
### (1).Program
A series of instructions to complete specific functions are often written in some high-level programming language (such as: C/C++, Python), so it is like the Hello World written by students during practice, the daily execution programs of enterprises or organizations, and in this topic The JDR tools used are all types of programs.
### (2).Job
"Job" is also a kind of program, but it is more inclined to the term of work in an enterprise or organization. Jobs are usually used to complete specific tasks that are slightly more complex in the system. For example, telecommunications companies may have programs such as "billing job" to process bill amounts; semiconductor manufacturing industry may also have a "scheduling job" to arrange the sequence of machines for each product in the manufacturing line.
### (3).Execution Item
"Execution item" is the execution behavior of "job" at "specific time" (that is, the plan execution time) according to its "execution frequency". For example, the billing job of the telecommunications company may be executed once at the beginning of each month (execution frequency), because the customer receives the bill once a month. When it is executed at the beginning of January 2023 (plan execution time), the bill for January 2023 will be generated, and the execution at the beginning of February will generate the bill for February, and so on. Therefore, "execution item" can be regarded as a concept of "job + plan execution time".
### (4). Purpose of JDR Tool
The purpose of this tool is to visually arrange the execution order of each job on the screen according to its execution frequency and the dependencies between each job. Each execution event is an execution item on the screen. Users can directly manage and operate the execution items, such as: distinguish the execution status by color (the following figure), execute the item, execute the item and downstream items, generate management reports, and generate warning messages if the items are not executed in order, etc. 
![](https://i.imgur.com/SCopRFm.png)


* Status Management: JDR tool uses the following colors to indicate status:
  * initial (not executed): white (#FFFFFF)
  * waiting (waiting): pale yellow (#FFFFCC)
  * running (in progress): yellow (#FFFF00)
  * success (successful): green (#74C126)
  * failure (failed): red (#EFABCD)
  * In addition, "not job" and "undefined job" are gray (#C0C0C0) by default because they are inoperable.

* Status flow: The status is sequential. Except for "not job" and "undefined job", the status of themselves will not change. The status of other valid items starts from "initial", then changes to "waiting", "running", and finally depending on the execution result, it becomes "success" or "failure".
![](https://i.imgur.com/XAWobPB.png)



---

## 6. Control Table Format and Job Development Principles
"Job" is the main core of executing business logic, and JDR is just an auxiliary tool. If the JDR tool can instantly read the job execution status and reflect it on the screen, the execution logic in the job must be regulated, and the control table for recording the job status must be designed for this purpose. This tool simplifies the design and quantity of the control table as much as possible, so there is only one control table, which is convenient for users to use.

**PS: JDR tool only supports PostgreSQL as the control table database.**

### (1). Control Table DDL
The format of the fields in the control table is as follows:
```
create table job_exec_log (
  job_name  varchar(200),
  plan_dt   timestamp,
  status    varchar(20),
  act_sdt   timestamp,
  act_edt   timestamp,
  data_num  integer
);
```

### (2). Introduction to Control Table Fields
Description of each field in the control table:
| # | control table field | Note |
| --| -------- | ---- |
| 1 | job_name | job name        |
| 2 | plan_dt  | Plan execution time     |
| 3 | status   | Job execution status, including: running, success, failure |
| 4 | act_sdt  | Actual start execution time  |
| 5 | act_edt  | Actual end execution time  |
| 6 | data_num | The number of processed data, but the value of this field must be calculated by the job itself before filling into control table |

### (3). Job Development Specification
The logic of the job must include the part of the access control table. The following provides a brief pseudo code. Each job shall be developed according to this principle:

```
# 1. Execution starts
# 2. Register the status of this execution to the control table:
   insert into job_exec_log:
   ==> Fill in the fields include: job_name, plan_dt, status (fill in 'running'), act_sdt

# 3. Execute the main job logic
# 4. Update the status of this execution to the control table before the end:
  update job_exec_log：
  ==> The updated fields include: status (fill in 'success' or 'failure' according to the execution result), act_edt, data_num
      And add where conditioon: job_name, plan_dt, act_sdt
# 5. End of execution
```

---

## 7. How to Use JDR Tool
The operation method and various functions of JDR tool are introduced as follows:

### (1). UI Introduction
The UI appearance of the JDR tool is as shown in the figure below. It is mainly composed of four parts: setting area, item navigator button area, main operation area and log area.
![](https://i.imgur.com/4xiemZ6.png)


1. Setting Area: There are also four sub-tabs, "Basic", "DB", "Function", and "Information", which provide general settings, operation functions and information collection.

  * Basic:
    * Language setting: change the display language of this tool, currently supports English and Traditional Chinese.
    * Set the start and end intervals of job execution, and each job will determine the "plan execution time" within the start and end intervals according to its own execution frequency.
    * Read job list document and specify sheet name.
    * After the above settings are completed, a flow chart can be generated in the main operation area. During the production process, it will display the variable information and error/warning message in the log area.
    * You can set the color of items in various states by yourself, and it can be restored to the default color.
  ![](https://i.imgur.com/6L75dAX.png)

  * DB:
    * Control table database connection settings: including connection IP, user account, password, connection port, database name.
    * Control table setting: Since the name and fields used by the user as the control table may not necessarily be the same as those in this project, the flexibility of self-setting is provided.
    * **Note: Currently JDR tool only supports PostgreSQL as the control table database.**
  ![](https://i.imgur.com/RAz4mdc.png)

  * Function:
    * Run On Time:
    If this check box is ticked, it means that all items must wait until the actual time exceeds the plan execution time of the item before they can be executed; if this check box is not ticked, it means that all the item does not need to consider whether the actual time exceeds the plan execution time of the item, and can be directly executed.
    * Run All Items:
    regardless of whether there are successfully executed items in the main operation area, all items will be executed from scratch.
    * Continue All Items:
    Consider the items in the main operation area that have been successfully executed and have been executed in order, and continue to execute all remaining items behind them.
    * Stop All Items:
    If you want to interrupt the execution after executing the "Run All Items" or "Continue All Items" function, you can execute this function. After execution, the waiting items will be deleted, but the running item cannot be interrupted, but can only wait for its execution to complete.
    * Show Report:
    Displays a summary report (main report) of all items in the main operation area, including a pie chart of each item type and status, comparing the difference statistics between the plan execution time and the actual start execution time, duration and data number statistics.
    * Reload From DB:
    Since the user may use other methods to execute items, this function is provided to allow the user to update the status of each item on the main operation area according to the execution information of the control table.
    * Save SVG:
    Save the graphic on the main operation area as an SVG image file.
  ![](https://i.imgur.com/yeatnzo.png)

  * Information:
    ![](https://i.imgur.com/4pH2lUR.png)
    * Definition of job information:

    | #    | Noun | Meaning |
    | ---- | -------- | -------- |
    | (A1) | Document jobs    | The number of records in the job list document |
    | (A2) | Available jobs   | It meets the time interval, and "job_not" field is not Y, and it is defined in the job list document |
    | (A3) | Unavailable jobs | Does not meets the time interval |
    | (A4) | Not jobs         | "job_not" field is Y |
    | (A5) | Undefined jobs   | is not defined in the job list document |

    * Definition of item information:
    
    | #    | Noun | Meaning |
    | ---- | -------- | -------- |
    | (B1) | All items       | All items in the main operation area |
    | (B2) | Available items | It meets the time interval, and "job_not" field is not Y, and it is defined in the job list document |
    | (B3) | Initial items   | status is initial |
    | (B4) | Waiting items   | status is waiting |
    | (B5) | Running items   | status is running |
    | (B6) | Success items   | status is success |
    | (B7) | Failure itemss  | status is failure |

    * Relationship between job information and item information:
      * (A1) = (A2) + (A3) + (A4)
      * (B2) = (B3) + (B4) + (B5) + (B6) + (B7)
      * (B1) = (B2) + (A4) + (A5)
    ![](https://i.imgur.com/P0XUbk9.png)

  


2. Item Navigator Button Area: 
    When a flow chart is produced in the main operation area, a button representing the item will be generated in the item navigator button area at the same time. The purpose of the button is twofold:
    * Help to search for items in the main operation area: 
      When the number of items in the main operation area is large and the process is more complicated, it will become more troublesome to find a specific item. Therefore, this function is provided to make it easier for users to find items on the screen. When the button of an item is clicked, the item will be displayed in the "upper left corner" of the main operation area.
    * Helps to check the status of items: 
      The button is the same color as the items in the main operation area, so it can be used to quickly confirm the status of all items.
    ![](https://i.imgur.com/noIZEbT.png)


3. Main Operation Area:

  * Functions provided: This area is used to display the flow chart, and the user can operate the items here (available items can be operated, but not-job and undefined-job cannot be operated). Currently, three operations are provided for the user to choose:
    * Run Single Item
    * Run Dependency Item
    * Show Report
  * Reflect the status with color: After the available item is executed, the color will change according to the execution status. The default color is:
    * initial (not executed): white (#FFFFFF)
    * waiting (waiting): pale yellow (#FFFFCC)
    * running (in progress): yellow (#FFFF00)
    * success (successful): green (#74C126)
    * failure (failed): red (#EFABCD)
    * In addition, "not job" and "undefined job" are gray (#C0C0C0) by default because they are inoperable.
  * Execution time sequence check function: Since the user can execute available items arbitrarily, there may be errors in the execution time sequence, so a check function is provided here. If the end time of the upstream item is later than the start time of the downstream item, the color of the arrow between them will turn red, and the font color of the item in the item navigator button area will also turn red.
    ![](https://i.imgur.com/sFVi89z.png)



4. Log Area: 
    This area is used to output information during the execution period, including:
    * Environment variable settings
    * User actions
    * Execution messages for available items
    * Various error/warning messages, such as:
      * Whether the connection of the control table database is normal
      * Is there any error in the setting of the job list document?
      * Other error/warning information when producing flowcharts
![](https://i.imgur.com/JlWrpAt.png)




### (2). Use Case Demonstration
1. Language switching:
The JDR tool provides multi-language support. Currently, it supports Traditional Chinese and English, and the default is English. Just adjust the Language drop-down menu in the setting area.
![](https://i.imgur.com/vKtsC7R.png)

2. Functional operation for a single (or partial) item:
Suppose a job list document is set as follows:

| job_no | job_type | job_name | job_freq | job_src | job_not | job_cmd |
| ---- | ---- | ---- | -------- | ---- | ---- | ---- |
| 1 | test | Job1 | YYYYMMDD |      |    | ```python runjob.py Job1 ${PLANDT}``` |
| 2 | test | Job2 | YYYYMMDD | Job1 |    | ```python runjob.py Job2 ${PLANDT}``` |
| 3 | test | Job3 | YYYYMMDD | Job1 |    | ```python runjob.py Job3 ${PLANDT}``` |
| 4 | test | Job4 | YYYYMMDD | Job2<br>Job3 |    | ```python runjob.py Job4 ${PLANDT}``` |

  * [1]. Generate job dependency flow chart
    Open the JDR tool, set the start and end dates (both take 2023-03-01 as an example), then read the job list document, select the sheet to be read, and press generate button, the job dependency flow chart will be generated on the main operation area. (Please make sure that the connection to the control table database is normal)
    ![](https://i.imgur.com/x2ynjxU.gif)
    This takes English version job list document as example:
    ![](https://i.imgur.com/E8WD4w5.gif)


  * [2]. Run Single Item
    After generate a job dependency flow chart, you can arbitrarily select a single item whose status is initial, success or failure to execute. Just move the cursor to the item to be executed, press the right mouse button and click the "Run Single Item" function to execute the item, and the execution result will also be reflected in the main operation area and the item navigator button area.
    ![](https://i.imgur.com/35KM8Rd.gif)

  * [3]. Run Dependency Item
    After generate the job dependency flow chart, if you want to execute a series of items with upstream and downstream relationships, you can select the top-level item whose status is initial, success, or failure to execute. Just move the cursor to the top-level item to be executed, right-click the mouse and click the "Run Dependency Item" function to execute the item and its downstream items in sequence, and the execution results will also be reflected in the main operation area and item navigator buttons area.
    ![](https://i.imgur.com/gGbZLdC.gif)
    However, it must be noted that the execution sequence will also be affected by the execution result and all upstream states of the item.
    The following example shows that if the execution result of Job2 in the above figure is a failure, then the downstream Job4 will not be executed: 
    ![](https://i.imgur.com/IpYluf4.gif)
    and for example, if Job2 click the "Run Dependency Item" function, but the downstream Job4 will not be executed, because the upstream Job3 of Job4 has not been executed yet:
    ![](https://i.imgur.com/5AcKo9k.gif)


  * [4]. If the order of execution time is wrong, the user will be warned in color.
    Since the execution sequence of items are executed from the upper layer to the lower layer, normally, **the execution end time of the upper layer will be earlier than the execution start time of the lower layer** . But if this rule is violated because the user executes the project arbitrarily, the arrow color will be changed to red in the main operation area, and the button text of the lower layer will also be changed to red in the item navigator button area.
    ![](https://i.imgur.com/dEgA6Cg.gif)

  * [5]. Display item report
    In the context menu of the item, the item report of each item is provided. Just move the cursor to the item to display the report, right-click the mouse and click the "Show Report" function. The report contains two tabs:
    * Related Items: Displays all related upstream and downstream items related to this item, and provides the function of saving the flow chart as an SVG file.
    * Execution Info: Displays the historical execution information of the job recorded in the control table. Currently, four reports are provided for user reference, including: execution status statistics, comparison between plan execution time and start execution time, execution time length statistics, Processing data number statistics.
    ![](https://i.imgur.com/9b4Cj3h.gif)

3. Functional operation for all items: 
Suppose a job list document is set as follows:

| job_no | job_type | job_name | job_freq | job_src | job_not | job_cmd |
| ---- | ---- | ---- | -------- | ---- | ---- | ---- |
| 1 | test | Job1 | YYYYMMDD |      |    | ```python runjob.py Job1 ${PLANDT}``` |
| 2 | test | Job2 | YYYYMMDD |      |    | ```python runjob.py Job2 ${PLANDT}``` |
| 3 | test | Job3 | YYYYMMDD |      |    | ```python runjob.py Job3 ${PLANDT}``` |
| 4 | test | Job4 | YYYYMMDD | Job1<br>Job2 |    | ```python runjob.py Job4 ${PLANDT}``` |
| 5 | test | Job5 | YYYYMMDD | Job2<br>Job3 |    | ```python runjob.py Job5 ${PLANDT}``` |
| 6 | test | Job6 | YYYYMMDD | Job4<br>Job5 |    | ```python runjob.py Job5 ${PLANDT}``` |

The resulting job dependency flow chart is as follows:
![](https://i.imgur.com/z9LKXmr.png)

  * [1]. Run All Items
    If the user feels that it is too troublesome to execute the items one by one, this tool provides the function of executing all items at once. After generating the job dependency flow chart, you can switch to the "Function" tab in the setting area first, and then execute the "Run All Items" function, and then it can be executed sequentially from the top layer to the bottom Lower level until all items are executed, or interrupted due to an execution error.
    But it must be noted that **this function must be used without any waiting or running items to avoid repeated execution of the items.** If there are items in waiting or running status, this tool will prohibit the use of this function.
    The following example shows that after executing this function, the three projects Job1, Job2, and Job3 will be executed at the same time, and then according to the dependency settings, in order until all executions are completed.
    ![](https://i.imgur.com/V1Qri4h.gif)


  * [2]. Continue All Items
    Although the above "Run All Items" function can execute all items at once, but it is troublesome to execute from scratch every time. Therefore, this tool also provides function that can execute all items at once and avoid repeated execution.
    The following example assumes that Job2 and Job3 have been successfully executed first. If the user wants to execute all of them but wants to skip these two items, he can use the "Continue All Items" function, and the result will be it is directly executed by Job1 and Job5.
    Same as the Run All Items function, **using the Continue All Items function must not have any waiting or running status items to avoid items being executed repeatedly**. If there are items in waiting or running status, this tool will prohibit the use of this function.
    ![](https://i.imgur.com/80QWhCV.gif)
    This function can also be used when the order of execution time is wrong. The following example assumes that Job2, Job3, and Job5 have been successfully executed first, but the execution time of Job2 is later than that of Job5, resulting in a wrong order of execution time (the arrow also turns red). At this time, this function will take this situation into consideration, so Job1 and Job5 will be selected to start execution. After Job5 is re-executed, the information on the screen will also be updated accordingly (the arrow turns black).
    ![](https://i.imgur.com/ekc0OlB.gif)


  * [3]. Stop All Items
    When using the "Run All Items" or "Continue All Items" function, when you want to terminate halfway through the execution, you can use "Stop All Items" function. This function will remove the waiting items, but it should be noted that if there are running items, they cannot be terminated. You still have to wait for the completion of the execution of the items, and will not continue to execute its downstream items after the completion.
    In the following example, the user executes the Run All Items function first, and then presses the Stop All Items function when Job4 is waiting and Job5 is running, so that Job4 returns to the original initial status, but Job5 continues to run until execution.
    ![](https://i.imgur.com/PtN1B4v.gif)


  * [4]. Show Report
    Use the "Show Report" function to generate a summary report (main report) of all items in the main operation area. Currently, the following six reports are provided:
    * Job Count Statistics
    * Item Count Statistics
    * Status Count Statistics
    * Compare the gap between the plan execution time and the actual start execution time
    * Execution Time Length Statistics
    * Data Number Statistics
    ![](https://i.imgur.com/zy6uWga.gif)


  * [5]. Reload From DB
    Because the user may use other methods to execute the item, this function is provided to allow the user to update the status of each item in the main operation area based on the execution information of the control table.

  * [6]. Save SVG
    save the graphic on the main operation area as an SVG image file.



### (3). Use "Run On Time" as a Scheduling Tool
![](https://i.imgur.com/p8PG5Cm.png)

In the "Function" tab of the setting area, there is a "Run On Time" checkbox, which is used to limit whether the item needs to be executed on time according to its own plan execution time during execution .

If Run On Time is checked (default), then when using the "Run All Items" or "Continue All Items" function, it will not execute the items which the current time has not yet reached the plan execution, but change the status of these items to waiting, and wait until the current time reaches the plan execution time then unblocking these items and starting to execute them.

If Run On Time is not checked, then it will not check whether the plan execution time has been reached. This situation is usually used when testing jobs.
Therefore, after checking "Run On Time", JDR can be regarded as a scheduling tool, because future items will be executed on time, and users only need to wait for these items to be executed sequentially.

The following takes the execution day as 2023-03-12 as an example, and produces a flow chart between 2023-03-12 ~ 2023-03-13.


* When Run On Time is checked 
and the "Run All Items" button is pressed, Job1, Job2, Job3, and Job4 of 2023-03-12 will start to be executed sequentially, but Job1 of 2023-03-13 the status of waiting is always maintained, because it is currently 2023-03-12, and it has not yet reached 2023-03-13.
![](https://i.imgur.com/OxaoiUF.gif)

* When Run On Time is not checked 
and the "Run All Items" button is pressed, all items will be executed sequentially even if it is not yet 2023-03-13.
![](https://i.imgur.com/pOMuoLb.gif)



### (4).Flexible Setting of the Control Table
The control table is used to record the execution status of each item. Different companies or organizations may have similar designs, but they may not necessarily be the same as the design of this project (for example, the name of the control table is different, the field name is different, or the state definition different...), so this tool provides flexibility as much as possible, allowing users to set it by themselves, hoping that this tool can be applied to different systems.

The following takes other systems as examples and explains how to set them in the JDR tool.
If the name of the control table of other systems is changed to: **job_exec_log2**,
and the execution status of the program is defined **R, S, F** as running, success, failure,
and the fields are different from the design of this project, for example :

| # | field meaning | This project field name | Other system field name |
| --| ------------- | ----------------------- | ----------------------- |
| 1 | Job name                    | job_name | job_name2 |
| 2 | Plan execution time         | plan_dt  | plan_dt2  |
| 3 | Job execution status        | status   | status2   |
| 4 | Actual start execution time | act_sdt  | act_sdt2  |
| 5 | Actual end execution time   | act_edt  | act_edt2  |
| 6 | Number of data processed    | data_num | data_num2 |

Users can set the name and field definition of the control table in the "DB " tab of the setting area:

* Control Table Name: set to **job_exec_log2**
* Column Name (Job Name): set to **job_name2**
* Column Name (Plan Datetime): set to **plan_dt2**
* Column Name (Job Status): set to **case status2 when 'R' then 'running' when 'S' then 'success' when 'F' then 'failure' end**
* Column Name (Actual Start Datetime): set to **act_sdt2**
* Column Name (Actual End Datetime): set to **act_edt2**
* Column Name (Data Number): set to **data_num2**
![](https://i.imgur.com/6GDIFWU.png)

After setting and then producing the flow chart, it can be executed smoothly:
![](https://i.imgur.com/7k4ESG4.gif)



### (5).Error Checking of Job List Document
The job list document records all the jobs in the organization. It is maintained by the manager, but since it is maintained by people, there may be errors. Therefore, this tool provides some basic error checking functions. The result will be displayed in the log area, and this tool will give different processing methods depending on the type of error. The rules are as follows:

| # | Error/Warning | Type             |  Processing method |
| --| ----- | ------------------- | ----------- |
| 1 | Error | Job list document has wrong field name       | Unable to generate flow chart |
| 2 | Error | Graphics have cycle        | Generates a flow chart, but cannot operate  |
| 3 | Error | The database cannot be connected         | Generates a flow chart, but cannot operate   |
| 4 | Error | Missing "job_cmd" field in job list document | Generates a flow chart, but cannot operate, and the job become an invalid type  |
| 5 | Error | Missing "job_freq" field in job list document | Generates a flow chart, but cannot operate, and the job become an invalid type  |
| 6 | Error | The "job_freq" field is format error | Generates a flow chart, but cannot operate, and the job become an invalid type |
| 7 | Warning | The "job_src" field contains undefined jobs | Generates a flow chart, which can be operated, but the job become an undefined type |

Let's take a wrong job list document as an example, if the content is as follows:

| job_no | job_type | job_name | job_freq | job_src | job_not | job_cmd |
| ---- | ---- | ---- | -------- | ---- | ---- | ---- |
| 1 | test | Job1 | YYYYMMDD | JobX |    | ```python runjob.py Job1 ${PLANDT}``` |
| 2 | test | Job2 | YYYYMMDD | Job1<br>Job4 |    | ```python runjob.py Job2 ${PLANDT}``` |
| 3 | test | Job3 | YYYYMMDD | Job1 |    | ```python runjob.py Job3 ${PLANDT}``` |
| 4 | test | Job4 | YYYYMMDD | Job2<br>Job3 |    | ```python runjob.py Job4 ${PLANDT}``` |
| 5 | test | Job5 |          |      |    | ```python runjob.py Job5 ${PLANDT}``` |
| 6 | test | Job6 | YYYYMMDD |      |    |    |
| 7 | test | Job7 | YYYYMMDDD |      |    | ```python runjob.py Job7 ${PLANDT}``` |

The generated flowchart is as follows (although there is a generated flowchart, it cannot actually be operated):
![](https://i.imgur.com/GXabBkt.png)

The information in the log area is as follows:
![](https://i.imgur.com/beoHA3H.png)

Log content can find these errors:

* [Error]: Job5 did not fill in the "job_freq" field
* [Error]: Job6 did not fill in the "job_cmd" field
* [Error]: Job7 "job_freq" format error
* [Error]: There is a cycle in the graph: Job2 -> Job4 -> Job2
* [Error]: The database cannot be connected
* [Warning]: There is a JobX in the "job_src" column, which is considered as an undefined job


### (6).Color Adjustment of Item Status
The JDR tool provides default colors for various execution status, but if users do not like the default colors, they can set them by themselves, and they can also be changed back to the default colors after setting.
The following example demonstrates changing the color of the success status from green to blue, and then back to the default color:
![](https://i.imgur.com/aclyPBt.gif)

