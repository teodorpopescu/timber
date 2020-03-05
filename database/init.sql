CREATE DATABASE TimberService;
use TimberService;

CREATE TABLE Authentication (   
    Username VARCHAR(30) PRIMARY KEY,
    Password VARCHAR(128) NOT NULL,
    Salt VARCHAR(32) NOT NULL
);

INSERT INTO Authentication (Username, Password, Salt) VALUES ('test1', '0zNYADm4dAeTfm1ahp7qm1uHafKEHDNt9CjyI0buAl/8nETlJbmmRESsvONQV7Li4xYSjRL+e9ImE23FBGIRvg==',
'0AvHYlywEtjvqu9GIydTHw==');

INSERT INTO Authentication (Username, Password, Salt) VALUES ('test2', 'TgAT4LxH2hVDprx2gnGgpe9Ety0baMeD1cblsl3Wh+K1VtfyyoGe9A1x6ynpTXVYPyFwtNwe8WPJHpdTATYIwQ==', '9UC2H9yrxmxYO8KbCvTfQA==');

INSERT INTO Authentication (Username, Password, Salt) VALUES ('test3', 
'aNvd/6fguoiFRGT42mzTQJ8sUPebmKs9bZBWvMhbn/6GtNeuH04md9T0qH0HPU0VQBvzxXKuhcJTHzDfIwGeUg==',
'XPzIKcwprHzsuQhOX6euvw==');
