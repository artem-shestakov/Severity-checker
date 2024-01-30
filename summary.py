import os, re, sys, yaml
from yaml import Loader


class RuleDumper(yaml.SafeDumper):
    # HACK: insert blank lines between top-level objects
    # inspired by https://stackoverflow.com/a/44284819/3786245
    def increase_indent(self, flow=False, indentless=False):
        return super(RuleDumper, self).increase_indent(flow, False)

    def write_line_break(self, data=None):
        indent = self.indent or 0
        if not self.indention or self.column > indent \
            or (self.column == indent and not self.whitespace):
            super().write_line_break(data)

        if len(self.indents) == 4:
            super().write_line_break()


def is_annotation(rule: dict) -> bool:
    if "annotations" in rule.keys():
        return True
    return False

def is_summary(annotations: dict) -> bool:
    if "summary" in annotations.keys():
        return True
    return False

def is_description(annotations: dict) -> bool:
    if "description" in annotations.keys():
        return True
    return False

def format_sum(summary: str) -> str:
    m = re.search(r"^({{ \$labels\.instance }}\s*->)\s*.*$", summary)
    if m:
        return summary
    else:
        return f"{{{{ $labels.instance }}}} -> {summary}"

def update_sum(data: dict) -> dict:
    for group in data["groups"]:
        for rule in group["rules"]:
            if is_annotation(rule):
                if is_summary(rule["annotations"]):
                    rule["annotations"]["summary"] = format_sum(rule["annotations"]["summary"])
                else:
                    if is_description(rule["annotations"]):
                        rule["annotations"]["summary"] = f"{{{{ $labels.instance }}}} -> {rule['annotations']['description']}"
                    else:
                        rule["annotations"]["summary"] = "{{ $labels.instance }} -> none"
            else:
                rule["annotations"] = {
                    "summary": "{{ $labels.instance }} -> none",
                    "description": "none"
                }
    return data
            

if __name__ == "__main__":
    # Check path ergument
    if len(sys.argv) < 2:
        print("path argument is missing")
        sys.exit(1)
    
    # Search yaml files and check severity
    for root, dirs, files in os.walk(sys.argv[1]):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                with open(root+'/'+file, "r", encoding="utf-8") as yaml_file:
                    data = yaml.load(yaml_file, Loader=Loader)
                    yaml_file.close()
                    if isinstance(data, dict) and "groups" in data.keys():
                        new_data = update_sum(data)
                        with open(root+'/'+file, "r+", encoding="utf-8") as f:
                            yaml.dump(data, f, 
                                encoding="utf-8",
                                allow_unicode=True,
                                width=1000,
                                Dumper=RuleDumper,
                                sort_keys=False)
                            f.close()
