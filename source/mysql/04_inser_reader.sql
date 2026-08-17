{
    "type": "MySQLNotebook",
    "version": "1.0",
    "caption": "Script",
    "content": "USE book_management;\nSHOW TABLES;\nDESC readers;\n\nINSERT INTO readers (name, gender, phone, register_data)\nVALUES ('张三', '男', '13800000001', '2026-08-07');\n\nSELECT * FROM readers;\n\nINSERT INTO readers (name, gender, phone, register_data)\nVALUES\n('李四', '女', '13800000002', '2026-08-07'),\n('王五', '男', '13800000003', '2026-08-08'),\n('赵六', '女', '13800000004', '2026-08-08');\n\nSElECT name, phone from reades;",
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
                "end": 16,
                "language": "mysql",
                "result": {
                    "type": "resultIds",
                    "list": [
                        "4c9a8990-81ec-4581-b8dc-dd48d8df6f2e",
                        "9c11dd6c-1b5f-4d19-f81e-0d5fd302e429",
                        "9cfad0b6-d544-4ebe-f535-c7d7a294bfab",
                        "787bdd56-c0a8-4874-b0d9-517609073299",
                        "bde1c84d-fd5f-45a8-85e1-a8bf7649d924",
                        "0b5805e3-c002-4dcd-d938-0b935df21326"
                    ]
                },
                "currentHeight": 300,
                "currentSet": 3,
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
                            "length": 13
                        },
                        "contentStart": 21,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 33,
                            "length": 14
                        },
                        "contentStart": 35,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 47,
                            "length": 107
                        },
                        "contentStart": 49,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 154,
                            "length": 24
                        },
                        "contentStart": 156,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 178,
                            "length": 191
                        },
                        "contentStart": 180,
                        "state": 0
                    },
                    {
                        "delimiter": ";",
                        "span": {
                            "start": 369,
                            "length": 33
                        },
                        "contentStart": 371,
                        "state": 0
                    }
                ]
            },
            "data": [
                {
                    "tabId": "99dc9ab7-e638-4106-ecf0-d619fd56c9f4",
                    "resultId": "4c9a8990-81ec-4581-b8dc-dd48d8df6f2e",
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
                        "text": "OK, 1 record retrieved in 1.176ms"
                    },
                    "totalRowCount": 1,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 1,
                    "sql": "\nSHOW TABLES",
                    "updatable": false
                },
                {
                    "tabId": "99dc9ab7-e638-4106-ecf0-d619fd56c9f4",
                    "resultId": "9c11dd6c-1b5f-4d19-f81e-0d5fd302e429",
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
                        "text": "OK, 5 records retrieved in 1.763ms"
                    },
                    "totalRowCount": 5,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 2,
                    "sql": "\nDESC readers",
                    "updatable": false
                },
                {
                    "tabId": "99dc9ab7-e638-4106-ecf0-d619fd56c9f4",
                    "resultId": "9cfad0b6-d544-4ebe-f535-c7d7a294bfab",
                    "rows": [
                        {
                            "0": 1,
                            "1": "张三",
                            "2": "男",
                            "3": "13800000001",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 2,
                            "1": "张三",
                            "2": "男",
                            "3": "13800000001",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 3,
                            "1": "张三",
                            "2": "男",
                            "3": "13800000001",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 4,
                            "1": "张三",
                            "2": "男",
                            "3": "13800000001",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 5,
                            "1": "张三",
                            "2": "男",
                            "3": "13800000001",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 6,
                            "1": "张三",
                            "2": "男",
                            "3": "13800000001",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 7,
                            "1": "张三",
                            "2": "男",
                            "3": "13800000001",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 8,
                            "1": "张三",
                            "2": "男",
                            "3": "13800000001",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 9,
                            "1": "李四",
                            "2": "女",
                            "3": "13800000002",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 10,
                            "1": "王五",
                            "2": "男",
                            "3": "13800000003",
                            "4": "2026-08-08"
                        },
                        {
                            "0": 11,
                            "1": "赵六",
                            "2": "女",
                            "3": "13800000004",
                            "4": "2026-08-08"
                        },
                        {
                            "0": 12,
                            "1": "张三",
                            "2": "男",
                            "3": "13800000001",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 13,
                            "1": "李四",
                            "2": "女",
                            "3": "13800000002",
                            "4": "2026-08-07"
                        },
                        {
                            "0": 14,
                            "1": "王五",
                            "2": "男",
                            "3": "13800000003",
                            "4": "2026-08-08"
                        },
                        {
                            "0": 15,
                            "1": "赵六",
                            "2": "女",
                            "3": "13800000004",
                            "4": "2026-08-08"
                        },
                        {
                            "0": 16,
                            "1": "张三",
                            "2": "男",
                            "3": "13800000001",
                            "4": "2026-08-07"
                        }
                    ],
                    "columns": [
                        {
                            "title": "reader_id",
                            "field": "0",
                            "dataType": {
                                "type": 4,
                                "flags": [
                                    "SIGNED",
                                    "ZEROFILL"
                                ],
                                "numericPrecision": 10,
                                "parameterFormatType": "OneOrZero",
                                "synonyms": [
                                    "INTEGER",
                                    "INT4"
                                ]
                            },
                            "inPK": true,
                            "nullable": false,
                            "autoIncrement": true
                        },
                        {
                            "title": "name",
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
                            "title": "gender",
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
                            "nullable": true,
                            "autoIncrement": false,
                            "default": null
                        },
                        {
                            "title": "phone",
                            "field": "3",
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
                            "nullable": true,
                            "autoIncrement": false,
                            "default": null
                        },
                        {
                            "title": "register_data",
                            "field": "4",
                            "dataType": {
                                "type": 27,
                                "needsQuotes": true
                            },
                            "inPK": false,
                            "nullable": true,
                            "autoIncrement": false,
                            "default": null
                        }
                    ],
                    "executionInfo": {
                        "text": "OK, 16 records retrieved in 0.3ms"
                    },
                    "totalRowCount": 16,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 4,
                    "sql": "\n\nSELECT * FROM readers",
                    "updatable": true,
                    "fullTableName": "readers"
                },
                {
                    "tabId": "99dc9ab7-e638-4106-ecf0-d619fd56c9f4",
                    "resultId": "787bdd56-c0a8-4874-b0d9-517609073299",
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
                        "text": "OK, 0 records retrieved in 0.328ms"
                    },
                    "totalRowCount": 0,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 0,
                    "sql": "USE book_management",
                    "updatable": false
                },
                {
                    "tabId": "99dc9ab7-e638-4106-ecf0-d619fd56c9f4",
                    "resultId": "bde1c84d-fd5f-45a8-85e1-a8bf7649d924",
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
                        "text": "OK, 1 row affected in 67.034ms"
                    },
                    "totalRowCount": 0,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 3,
                    "sql": "\n\nINSERT INTO readers (name, gender, phone, register_data)\nVALUES ('张三', '男', '13800000001', '2026-08-07')",
                    "updatable": false
                },
                {
                    "tabId": "99dc9ab7-e638-4106-ecf0-d619fd56c9f4",
                    "resultId": "0b5805e3-c002-4dcd-d938-0b935df21326",
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
                        "text": "OK, 3 rows affected in 68.612ms"
                    },
                    "totalRowCount": 0,
                    "hasMoreRows": false,
                    "currentPage": 0,
                    "index": 5,
                    "sql": "\n\nINSERT INTO readers (name, gender, phone, register_data)\nVALUES\n('李四', '女', '13800000002', '2026-08-07'),\n('王五', '男', '13800000003', '2026-08-08'),\n('赵六', '女', '13800000004', '2026-08-08')",
                    "updatable": false
                }
            ]
        }
    ]
}