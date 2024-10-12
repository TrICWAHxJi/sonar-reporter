import html
import json
import os
import subprocess
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

import toml
from mako.template import Template


def filter_results(results):
    filtered_results = []

    for result in results:
        properties = result.get('properties', {})
        status = properties.get("status")

        if status != 'CLOSED':
            filtered_results.append(result)

    return filtered_results

def strip_scheme(url: str) -> str:
    schemaless = urlparse(url)._replace(scheme='').geturl()
    return schemaless[2:] if schemaless.startswith("//") else schemaless

def export_from_sonar(url, token, project_key, output_path, output_format="sarif"):
    copy_env = os.environ.copy()
    copy_env["SONAR_HOST_URL"] = url
    copy_env["SONAR_TOKEN"] = token
    output = open(output_path, "w")
    subprocess.run(["sonar-findings-export", "-k", project_key, "--format", output_format], stdout=output, env=copy_env)


def aggregate_regions_by_file(results):
    file_regions = defaultdict(list)

    for result in results:
        location = result['locations'][0]
        physical_location = location['physicalLocation']
        file_path = strip_scheme(physical_location['artifactLocation']['uri'])
        region = physical_location['region']

        file_regions[file_path].append(region)

    return file_regions


def highlight_region_in_line(line, start_col, end_col=None):
    before_highlight = line[:start_col]
    if end_col:
        highlighted_part = line[start_col:end_col]
        after_highlight = line[end_col:]
    else:
        highlighted_part = line[start_col:]
        after_highlight = ""

    before_highlight = html.escape(before_highlight)
    highlighted_part = f'<span class="highlighted">{html.escape(highlighted_part)}</span>'
    after_highlight = html.escape(after_highlight)

    return before_highlight + highlighted_part + after_highlight


def apply_highlighting_to_file_content(file_content, regions):
    lines = file_content.splitlines()
    highlighted_content = ""

    for idx, line in enumerate(lines, 1):
        regions_in_line = [region for region in regions if
                           region['startLine'] <= idx <= region.get('endLine', region['startLine'])]

        if regions_in_line:
            escaped_line = ""
            for region in regions_in_line:
                start_line = region['startLine']
                end_line = region.get('endLine', start_line)
                start_column = region.get('startColumn', 1) if idx == start_line else 1
                end_column = region.get('endColumn', None) if idx == end_line else None

                if idx == start_line and idx == end_line:
                    escaped_line = highlight_region_in_line(line, start_column, end_column)
                elif idx == start_line:
                    escaped_line = highlight_region_in_line(line, start_column)
                elif idx == end_line:
                    escaped_line = highlight_region_in_line(line, 1, end_column)
                else:
                    escaped_line = f'<span class="highlighted">{html.escape(line)}</span>'
            escaped_line = f'-{idx: <4}{escaped_line}'
        else:
            escaped_line = f'{idx: <5}' + html.escape(line)

        highlighted_content += escaped_line + "\n"

    return highlighted_content


def create_html_report_with_aggregated_regions(results, root_dir=None):
    file_regions = aggregate_regions_by_file(results)

    files_with_highlighting = {}

    for file_path, regions in file_regions.items():
        if root_dir:
            full_file_path = Path(root_dir + file_path)
        else:
            full_file_path = Path(file_path)

        try:
            file_content = full_file_path.read_text(encoding='utf-8')
        except Exception as e:
            file_content = f"Error reading file {full_file_path}: {str(e)}"
            regions = []

        highlighted_content = apply_highlighting_to_file_content(file_content, regions)

        files_with_highlighting[file_path] = highlighted_content

    template = Template(filename='template.html.mako')

    html_report = template.render(files=files_with_highlighting)

    return html_report

with open('config.toml', 'r') as f:
    config = toml.load(f)

sarif_path = "./report.sarif"
sonar_url = config["sonar"]["url"]
sonar_token = config["sonar"]["token"]
project_key = config["sonar"]["project_key"]
export_from_sonar(sonar_url, sonar_token, project_key, sarif_path)

with open(sarif_path, 'r', encoding='utf-8') as f:
    sarif_data = json.load(f)

run = sarif_data['runs'][0]
results = run['results']
results = filter_results(results)

root_directory = config["project"]["src"]

html_report_with_columns = create_html_report_with_aggregated_regions(results, root_dir=root_directory)

output_file_with_columns = "./report.html"
with open(output_file_with_columns, 'w', encoding='utf-8') as f:
    f.write(html_report_with_columns)