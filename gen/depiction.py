# follow https://rustup.rs
# pip3 install maturin jinja2 minify-html
import html
import json
import os
import re
import minify_html
from jinja2 import Environment, FileSystemLoader
from extra import *

root = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(root, '../templates')
screenshots_dir = os.path.join(root, '../screenshots')
env = Environment(loader=FileSystemLoader(templates_dir), trim_blocks=True, lstrip_blocks=True)
html_template = env.get_template('index.html')

tweaks = [
        {
            "file": "ytmusicnocast",
            "title": "YouTubeMusicNoCast",
            "min_ios": "15.0",
            "description": "<p>Hide the Cast Button in the whole YTMusic iOS Application</p>",
            "changes": [
                ["1.0", "Initial Release"]
                    ],
        },
        {
            "file": "chefkochnoads",
            "title": "ChefKochNoAds",
            "min_ios": "15.0",
            "description": "<p>hides ads in Chefkoch iOS Apllication</p>"
        },
] + extra

sileo_keys = [
    "headerImage", "tintColor", "backgroundColor"
]

for entry in tweaks:
    file = entry.get("file")
    title = entry.get("title")
    min_ios = entry.get("min_ios")
    max_ios = entry.get("max_ios")
    strict_range = entry.get("strict_range")
    screenshots = entry.get("screenshots")
    featured_as_banner = entry.get("featured_as_banner")
    changes = entry.get("changes")
    # link_source_code = entry.get("link_source_code")
    inline_source_code = entry.get("inline_source_code")
    debug = entry.get("debug")
    description = re.sub(r'\s+', ' ', entry.get("description"))
    extra_content = entry.get("extra_content")
    if extra_content:
        extra_content = re.sub(r'\s+', ' ', extra_content)
    output_path = os.path.join(root, "../depictions", f"{file}.html")

    SOURCE_CODE = None
    screenshot_objects = list(filter(None, list(map(
        lambda e: None if e.name.startswith('.') else {
            "url": f"https://zsaaiq.github.io/jailbreakrepo/screenshots/{file}/{e.name}",
            "accessibilityText": e.name
        },
        os.scandir(os.path.join(screenshots_dir, file))
    )))) if screenshots else None

    if inline_source_code:
        SOURCE_CODE_FOUND = False
        POSSIBLE_FOLDERS = ['SpringBoard-Switch', 'System-iOS', 'YouTube', 'Camera']
        try:
            for folder in POSSIBLE_FOLDERS:
                source_code_path = f'../../{folder}/{file}/Tweak.x'
                if os.path.exists(source_code_path):
                    with open(source_code_path, 'r') as source_code_content:
                        SOURCE_CODE = source_code_content.read()
                        SOURCE_CODE_FOUND = True
                        break
        except IOError:
            print(f"Could not read source code of {title}")
        if not SOURCE_CODE_FOUND:
            print(f"Source code of {title} not found")
            continue
    with open(output_path, 'w') as fh:
        fh.write(minify_html.minify(html_template.render(
            title=title,
            min_ios=min_ios,
            max_ios=max_ios,
            strict_range=strict_range,
            changes=changes,
            screenshots=screenshot_objects,
            description=description,
            extra_content=extra_content,
            source_code=html.escape(SOURCE_CODE) if SOURCE_CODE is not None else None,
            debug=debug
        ), minify_js=False, minify_css=False))
    print(f"Generated {output_path}")

    no_sileo = entry.get("no_sileo")
    if no_sileo:
        continue
    sileo_output_path = os.path.join(root, "../sileodepictions", f"{file}.json")

    with open(os.path.join(templates_dir, "index.json")) as json_file:
        data = json.load(json_file)
        for key in sileo_keys:
            val = entry.get(key)
            if val:
                data[key] = val
        if featured_as_banner and 'headerImage' not in entry:
            data['headerImage'] = f"https://zsaaiq.github.io/jailbreakrepo//repo/features/{file}.png"
        tabs = data["tabs"]
        VIEWS = None
        for json_entry in tabs:
            tabname = json_entry["tabname"]
            if tabname == "Details":
                VIEWS = json_entry["views"]
                VIEWS[0]["markdown"] = description
                if screenshot_objects is not None and screenshot_objects.count:
                    screenshots_json = {
                        "class": "DepictionScreenshotsView",
                        "itemCornerRadius": 14,
                        "screenshots": screenshot_objects,
                        "itemSize": "{160,284}"
                    }
                    VIEWS.insert(0, screenshots_json)
                if extra_content:
                    VIEWS.append({
                        "class": "DepictionMarkdownView",
                        "markdown": extra_content,
                        "useSpacing": True,
                        "useRawFormat": True
                    })
        if VIEWS and min_ios:
            support_versions = {
                "class": "DepictionSubheaderView",
                "useMargins": True,
                "title": f"Compatible with iOS {min_ios} to {max_ios}" if min_ios and max_ios else f"Compatible with iOS {min_ios} +"
            }
            VIEWS.insert(0, support_versions)
        if SOURCE_CODE:
            source_code_tab = {
                "class": "DepictionStackView",
                "tabname": "Source Code",
                "views": [
                    {
                        "class": "DepictionMarkdownView",
                        "markdown": f"```\n{SOURCE_CODE}\n```"
                    }
                ]
            }
            tabs.append(source_code_tab)
        if changes:
            changes_tab = {
                "class": "DepictionStackView",
                "tabname": "Changelog",
                "views": []
            }
            VIEWS = changes_tab["views"]
            FIRST_CHANGE = True
            for change in changes:
                if not FIRST_CHANGE:
                    VIEWS.append({
                        "class": "DepictionSeparatorView"
                    })

                VIEWS.append({
                    "class": "DepictionSubheaderView",
                    "title": f"Version {change[0]}"
                })
                CHANGE_PART = ""
                if isinstance(change[1], list):
                    for c in change[1]:
                        CHANGE_PART += f"- {c}\n"
                else:
                    CHANGE_PART = f"- {change[1]}"
                VIEWS.append({
                    "class": "DepictionMarkdownView",
                    "markdown": CHANGE_PART
                })
                FIRST_CHANGE = False
            tabs.append(changes_tab)

    with open(sileo_output_path, 'w') as out_file:
        json.dump(data, out_file)
    print(f"Generated {sileo_output_path}")
