{
    "type": "MySQLNotebook",
    "version": "1.0",
    "caption": "Script",
    "content": "SELECT 1+1 AS RESULT;\n\nSELECT 'Hello mysql' AS message;\n\nSELECT 10*20 as value;\n\nSELECT VERSION() as mysql_version;",
    "options": {
        "tabSize": 4,
        "indentSize": 4,
        "insertSpaces": true,
        "defaultEOL": "LF",
        "trimAutoWhitespace": true
    },
    "viewState": null,
    "contexts": [
        {
            "state": {
                "start": 1,
                "end": 7,
                "language": "mysql",
                "result": {
                    "type": "resultIds",
                    "list": [
                        "2c81f29b-611f-4f0d-9411-82c0f0eecf89",
                        "ee532059-0bcf-4d66-fb2b-5f36a91df0bb",
                        "5945c60d-7328-40c7-d5ca-cb3e080facec",
                        "8299e90d-17f8-43bd-c8c0-b96440f8db8d"
                    ]
                },
                "currentHeight": 300,
                "currentSet": 4,
                "statements": [
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 0,
                            "length": 21
                        },
                        "contentStart": 0,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 21,
                            "length": 34
                        },
                        "contentStart": 23,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 55,
                            "length": 24
                        },
                        "contentStart": 57,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 79,
                            "length": 36
                        },
                        "contentStart": 81,
                        "state": 0
                    }
                ]
            },
            "data": [
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "2c81f29b-611f-4f0d-9411-82c0f0eecf89",
                    "rows": [
                        {
                            "0": 2
                        }
                    ],
                    "columns": [
                        {
                            "title": "RESULT",
                            "field": "0",
                            "dataType": {
                                "type": 1,
                                "flags": [
                                    "UNSIGNED",
                                    "ZEROFILL"
                                ],
                                "numericPrecision": 3,
                                "parameterFormatType": "OneOrZero",
                                "synonyms": [
                                    "BOOL",
                                    "BOOLEAN",
                                    "INT1"
                                ]
                            },
                            "inPK": false,
                            "nullable": false,
                            "autoIncrement": false
                        }
                    ],
                    "executionInfo": {
                        "text": "OK, 1 record retrieved in 0.356ms"
                    },
                    "totalRowCount": 1,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 0,
                    "sql": "SELECT 1+1 AS RESULT",
                    "updatable": false,
                    "fullTableName": ""
                },
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "ee532059-0bcf-4d66-fb2b-5f36a91df0bb",
                    "rows": [
                        {
                            "0": "Hello mysql"
                        }
                    ],
                    "columns": [
                        {
                            "title": "message",
                            "field": "0",
                            "dataType": {
                                "type": 17,
                                "characterMaximumLength": 65535,
                                "flags": [
                                    "BINARY",
                                    "ASCII",
                                    "UNICODE"
                                ],
                                "needsQuotes": true,
                                "parameterFormatType": "OneOrZero"
                            },
                            "inPK": false,
                            "nullable": false,
                            "autoIncrement": false
                        }
                    ],
                    "executionInfo": {
                        "text": "OK, 1 record retrieved in 0.646ms"
                    },
                    "totalRowCount": 1,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 1,
                    "sql": "\n\nSELECT 'Hello mysql' AS message",
                    "updatable": false,
                    "fullTableName": ""
                },
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "5945c60d-7328-40c7-d5ca-cb3e080facec",
                    "rows": [
                        {
                            "0": 200
                        }
                    ],
                    "columns": [
                        {
                            "title": "value",
                            "field": "0",
                            "dataType": {
                                "type": 2,
                                "flags": [
                                    "UNSIGNED",
                                    "ZEROFILL"
                                ],
                                "numericPrecision": 5,
                                "parameterFormatType": "OneOrZero",
                                "synonyms": [
                                    "INT2"
                                ]
                            },
                            "inPK": false,
                            "nullable": false,
                            "autoIncrement": false
                        }
                    ],
                    "executionInfo": {
                        "text": "OK, 1 record retrieved in 0.325ms"
                    },
                    "totalRowCount": 1,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 2,
                    "sql": "\n\nSELECT 10*20 as value",
                    "updatable": false,
                    "fullTableName": ""
                },
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "8299e90d-17f8-43bd-c8c0-b96440f8db8d",
                    "rows": [
                        {
                            "0": "8.0.43"
                        }
                    ],
                    "columns": [
                        {
                            "title": "mysql_version",
                            "field": "0",
                            "dataType": {
                                "type": 17,
                                "characterMaximumLength": 65535,
                                "flags": [
                                    "BINARY",
                                    "ASCII",
                                    "UNICODE"
                                ],
                                "needsQuotes": true,
                                "parameterFormatType": "OneOrZero"
                            },
                            "inPK": false,
                            "nullable": false,
                            "autoIncrement": false
                        }
                    ],
                    "executionInfo": {
                        "text": "OK, 1 record retrieved in 0.316ms"
                    },
                    "totalRowCount": 1,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 3,
                    "sql": "\n\nSELECT VERSION() as mysql_version",
                    "updatable": false,
                    "fullTableName": ""
                }
            ]
        }
    ]
}