import os, yaml, re, sys
from rich import box
from rich.console import Console
from rich.table import Table, Column
from yaml.loader import Loader


table = Table(
    Column(header="File"),
    Column(header="Line"),
    Column(header="Value"),
    box=box.SIMPLE
)

# All changes
chg_logs = {}

def get_config(config)-> dict:
    with open(config, 'r') as config_file:
        conf = yaml.load(config_file, Loader=Loader)
        config_file.close()
        return conf

def print_table(table):
    console = Console()
    console.print(table)

def find_severity(line: str) -> str:
    m = re.search(r"^\s*severity:\s*(\w+)?\s*$", line)
    if m:
        if m.group(1):
            return m.group(1)
        else:
            return "empty value"
    return None

def check_severity(filename, config=dict):
    with open(filename, 'r') as file:
        lines = file.readlines()
        line_num = 1
        # Read line by line
        for line in lines:
            # Find severity in line
            severity = find_severity(line)
            # If find and severity is incorrect
            if severity and severity not in [key for key in config]:
                # default new severity
                new_severity = 'unknown'
                for zont_severity, mapping_severities in config.items():
                    for mapping_severity in mapping_severities:
                        if severity == mapping_severity:
                            new_severity = zont_severity
                if new_severity != "unknown":
                    table.add_row(filename, str(line_num), f"{severity} -> {new_severity}")
                else:
                    # Color log if severity unknown
                    table.add_row(filename, str(line_num), f"{severity} -> {new_severity}", style="red")
                if filename not in chg_logs.keys():
                    chg_logs[filename] = {}
                
                chg_logs[filename][str(line_num)] = {
                    "old_severity": severity,
                    "new_severity": new_severity 
                }              
            line_num += 1

if __name__ == "__main__":
    # Check path ergument
    if len(sys.argv) < 2:
        print("path argument is missing")
        sys.exit(1)

    # Read config file
    config = get_config("config.yaml")
    
    # Search yaml files and check severity
    for root, dirs, files in os.walk(sys.argv[1]):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                check_severity(root+'/'+file, config=config)

    # If bad severities were found
    if table.row_count > 0:
        print_table(table)

    # Change 
    for file, chg_lines in chg_logs.items():
        with open(file, "r") as f:
            data = f.readlines()
            f.close()
            
            for chg_line_num, chg_data in chg_lines.items():
                data[int(chg_line_num)-1] = data[int(chg_line_num)-1].replace(
                    chg_logs[file][chg_line_num]["old_severity"],
                    chg_logs[file][chg_line_num]["new_severity"]
                )
            with open(file, "r+") as f:
                f.writelines(data)
                f.close()
