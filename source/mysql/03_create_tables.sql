{
    "type": "MySQLNotebook",
    "version": "1.0",
    "caption": "Untitled-1",
    "content": "USe book_management;\nCREATE table readers(\nreader_id INT PRIMARY KEY AUTO_INCREMENT, # INT 数据类型，PRIMARY KEY主键，AUTO_INCREMENT自动添加\nname VARCHAR(50) NOT NULL,\ngender varchar(10),\nphone VARCHAR(20),\nregister_data DATE\n);\nSHOW tables;\nDESC readers;\n",
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
                "end": 11,
                "language": "mysql",
                "result": {
                    "type": "resultIds",
                    "list": [
                        "14f0fe24-550b-4797-8a35-e6be2dc92cd2",
                        "7db9140b-0f9b-4968-8292-af9c7f2acd59",
                        "25847e90-77ff-4882-84b5-5d997b7fdbd4"
                    ]
                },
                "currentHeight": 300,
                "currentSet": 2,
                "statements": [
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 0,
                            "length": 20
                        },
                        "contentStart": 0,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 20,
                            "length": 196
                        },
                        "contentStart": 21,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 216,
                            "length": 13
                        },
                        "contentStart": 217,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 229,
                            "length": 14
                        },
                        "contentStart": 231,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 243,
                            "length": 1
                        },
                        "contentStart": 242,
                        "state": 3
                    }
                ]
            },
            "data": [
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "14f0fe24-550b-4797-8a35-e6be2dc92cd2",
                    "rows": [
                        {
                            "0": "readers"
                        }
                    ],
                    "columns": [
                        {
                            "title": "Tables_in_book_management",
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
                        "text": "OK, 1 record retrieved in 1.032ms"
                    },
                    "totalRowCount": 1,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 2,
                    "sql": "\nSHOW tables",
                    "updatable": false
                },
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "7db9140b-0f9b-4968-8292-af9c7f2acd59",
                    "rows": [
                        {
                            "0": "reader_id",
                            "1": "int",
                            "2": "NO",
                            "3": "PRI",
                            "4": null,
                            "5": "auto_increment"
                        },
                        {
                            "0": "name",
                            "1": "varchar(50)",
                            "2": "NO",
                            "3": "",
                            "4": null,
                            "5": ""
                        },
                        {
                            "0": "gender",
                            "1": "varchar(10)",
                            "2": "YES",
                            "3": "",
                            "4": null,
                            "5": ""
                        },
                        {
                            "0": "phone",
                            "1": "varchar(20)",
                            "2": "YES",
                            "3": "",
                            "4": null,
                            "5": ""
                        },
                        {
                            "0": "register_data",
                            "1": "date",
                            "2": "YES",
                            "3": "",
                            "4": null,
                            "5": ""
                        }
                    ],
                    "columns": [
                        {
                            "title": "Field",
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
                        },
                        {
                            "title": "Type",
                            "field": "1",
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
                        },
                        {
                            "title": "Null",
                            "field": "2",
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
                        },
                        {
                            "title": "Key",
                            "field": "3",
                            "dataType": {
                                "type": 43,
                                "needsQuotes": true
                            },
                            "inPK": false,
                            "nullable": false,
                            "autoIncrement": false
                        },
                        {
                            "title": "Default",
                            "field": "4",
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
                        },
                        {
                            "title": "Extra",
                            "field": "5",
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
                        "text": "OK, 5 records retrieved in 24.256ms"
                    },
                    "totalRowCount": 5,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 3,
                    "sql": "\nDESC readers",
                    "updatable": false
                },
                {
                    "tabId": "0bdd7247-c680-47ca-f495-c3f0d675975e",
                    "resultId": "25847e90-77ff-4882-84b5-5d997b7fdbd4",
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
                        "text": "OK, 0 records retrieved in 0.363ms"
                    },
                    "totalRowCount": 0,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 0,
                    "sql": "USe book_management",
                    "updatable": false
                }
            ]
        }
    ]
}