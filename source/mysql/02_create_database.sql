{
    "type": "MySQLNotebook",
    "version": "1.0",
    "caption": "Untitled-1",
    "content": "CREATE DATABASE book_management;\nSHOW DATABASES;\nUSE book_management;\nSELECT DATABASE() AS current_datase;\ncreate database if not exists book_management;\n",
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
                "end": 6,
                "language": "mysql",
                "result": {
                    "type": "resultIds",
                    "list": [
                        "1d20c70d-7712-46c9-989b-528913fd8ed8",
                        "3806710d-4787-4b1b-a014-f718a126fbc7",
                        "a5c2a317-0dfa-4c5c-a7b5-8309e7b630ad",
                        "f6e9f7c9-b700-4ce8-b1cf-70e0ccac8651"
                    ]
                },
                "currentHeight": 300,
                "currentSet": 2,
                "statements": [
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 0,
                            "length": 32
                        },
                        "contentStart": 0,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 32,
                            "length": 16
                        },
                        "contentStart": 33,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 48,
                            "length": 21
                        },
                        "contentStart": 49,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 69,
                            "length": 37
                        },
                        "contentStart": 70,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 106,
                            "length": 47
                        },
                        "contentStart": 107,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 153,
                            "length": 1
                        },
                        "contentStart": 152,
                        "state": 3
                    }
                ]
            },
            "data": [
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "1d20c70d-7712-46c9-989b-528913fd8ed8",
                    "rows": [
                        {
                            "0": "book_management"
                        },
                        {
                            "0": "information_schema"
                        },
                        {
                            "0": "mysql"
                        },
                        {
                            "0": "performance_schema"
                        },
                        {
                            "0": "studen_db"
                        },
                        {
                            "0": "student_db"
                        },
                        {
                            "0": "sys"
                        }
                    ],
                    "columns": [
                        {
                            "title": "Database",
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
                        "text": "OK, 7 records retrieved in 0.715ms"
                    },
                    "totalRowCount": 7,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 1,
                    "sql": "\nSHOW DATABASES",
                    "updatable": false
                },
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "3806710d-4787-4b1b-a014-f718a126fbc7",
                    "rows": [
                        {
                            "0": "book_management"
                        }
                    ],
                    "columns": [
                        {
                            "title": "current_datase",
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
                        "text": "OK, 1 record retrieved in 0.277ms"
                    },
                    "totalRowCount": 1,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 3,
                    "sql": "\nSELECT DATABASE() AS current_datase",
                    "updatable": false,
                    "fullTableName": ""
                },
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "a5c2a317-0dfa-4c5c-a7b5-8309e7b630ad",
                    "rows": [],
                    "columns": [
                        {
                            "title": "*",
                            "field": "0",
                            "dataType": {
                                "type": 0
                            },
                            "inPK": false,
                            "nullable": false,
                            "autoIncrement": false
                        }
                    ],
                    "executionInfo": {
                        "text": "OK, 0 records retrieved in 0.361ms"
                    },
                    "totalRowCount": 0,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 2,
                    "sql": "\nUSE book_management",
                    "updatable": false
                },
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "f6e9f7c9-b700-4ce8-b1cf-70e0ccac8651",
                    "rows": [],
                    "columns": [
                        {
                            "title": "*",
                            "field": "0",
                            "dataType": {
                                "type": 0
                            },
                            "inPK": false,
                            "nullable": false,
                            "autoIncrement": false
                        }
                    ],
                    "executionInfo": {
                        "text": "OK, 1 row affected in 30.066ms"
                    },
                    "totalRowCount": 0,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 4,
                    "sql": "\ncreate database if not exists book_management",
                    "updatable": false
                }
            ]
        }
    ]
}