#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hxann` package."""

import pytest
from click.testing import CliRunner

from hxann import cli
from hxann.hxann import translate_record


def test_content():
    sample_input = {
        "id": 2,
        "Start Time": "00:01:03",
        "End Time": "00:01:33",
        "Annotation Text": "annotation 1",
        "Video Link": "https://d2f1egay8yehza.cloudfront.net/HarvardXSOC1.jsx-V000800_DTH.mp4",
        "Tags": None,
    }
    expected_output = {
        "@context": "http://catchpy.harvardx.harvard.edu.s3.amazonaws.com/jsonld/catch_context_jsonld.json",
        "body": {
            "items": [
                {
                    "purpose": "commenting",
                    "type": "TextualBody",
                    "value": "annotation 1",
                }
            ],
            "type": "List",
        },
        "created": "2023-11-03T15:01:21+00:00",
        "creator": {"id": "admin", "name": "admin"},
        "id": 2,
        "modified": "2023-11-03T15:01:21+00:00",
        "permissions": {
            "can_admin": ["admin"],
            "can_delete": ["admin"],
            "can_read": [],
            "can_update": ["admin"],
        },
        "platform": {
            "collection_id": "None",
            "context_id": "None",
            "platform_name": "edX",
            "target_source_id": "123",
        },
        "schema_version": "1.1.0",
        "target": {
            "items": [
                {
                    "format": "video/mp4",
                    "selector": {
                        "items": [
                            {
                                "conformsTo": "http://www.w3.org/TR/media-frags/",
                                "refinedBy": [
                                    {"type": "CssSelector", "value": "#video1"}
                                ],
                                "type": "FragmentSelector",
                                "value": "t=63,93",
                            }
                        ],
                        "type": "List",
                    },
                    "source": "https://d2f1egay8yehza.cloudfront.net/HarvardXSOC1.jsx-V000800_DTH.mp4",
                    "type": "Video",
                }
            ],
            "type": "List",
        },
        "type": "Annotation",
    }

    result = translate_record(sample_input, "webann")
    assert result is not None
    assert result["target"]["items"][0]["source"] == sample_input["Video Link"]
    assert result["target"]["items"][0]["type"] == "Video"
    assert result["target"]["items"][0]["format"] == "video/mp4"
    assert result["target"]["items"][0]["selector"]["items"][0]["value"] == "t=63,93"


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert '"size": 0' in result.output
    help_result = runner.invoke(cli.cli, ["--help"])
    assert help_result.exit_code == 0
    assert "Show this message and exit." in help_result.output
