<h3>Welcome to Borderless360 Test Task</h3>

The program prints specified event related json data 
and exports it to HTML on demand.

Requirements: 
- Python 3.9
- pip
- virtualenv

<h5>Installation (Linux/OSX, different steps 3 and 4 for Windows):</h5>

1. git clone https://github.com/intr00der/borderless360-test-task.git

2. python3.9 -m virtualenv venv
 
3. pip install -r requirements.txt

4. source venv/bin/activate

<h5>Usage:</h5>

```python cli.py print -e``` (```-e``` is for HTML export)

You can specify the files that should be read,
and the HTML export file destination path.

Example: ```python cli.py print -f input/sample1* -e -d output/my_export_file.html```

This will read all files that match "input/sample1*" wildcard pattern and will export data to "output/my_export_file.html"

(```python cli.py print -h``` for details)


<h5>Explanation:</h5>

This project consists of multiple modules:
1. **_report.py_** - contains  the ```Report``` class.

```Report``` class takes an event dictionary data, serializes it and makes a group of ```EventMetaData``` objects out of it.

The ```Report``` object has its "context" attribute which is the main information holder for printing and HTML rendering.

The context holds ```EventMetaData``` objects which data structures that hold event's main information.


2. _**printer.py**_ - contains the ```ReportPrinter``` class.

```ReportPrinter``` object takes input file path pattern, boolean that represents the need of HTML export, and output file path,
creates the ```Report``` objects, creates summary with full metrics that sum up from each ```Report```,
prints the reports with their respective summaries and the final summary, it's also responsible for rendering its "_context" dictionary into an HTML content
and writing that content to the specified output path.

3. **_cli.py_** - contains the CLI that allows user to use the program.

<h5>Dependency markup:</h5> 

```EventMetaData``` objects contain main data of each event.

```Report.context``` contains ```EventMetaData``` objects with additional report data.

```ReportPrinter._context``` contains ```Report``` objects with additional global data.
