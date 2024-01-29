# Severity checker
Script to check you prometheus alerts YAML files and bring severities to a unified form

## How to
```shell
python3 main.py <path_to_alert_files>

 File            Line   Value                 
───────────────────────────────────────────── 
 ./alerts.yaml   16     warning -> minor      
 ./alerts.yaml   25     disaster -> critical  
 ./alerts.yaml   40     none -> info          
 ./alerts.yaml   197    warning -> minor    
```