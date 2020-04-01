CREATE DATABASE TimberService;
use TimberService;

CREATE TABLE Authentication (   
    Username VARCHAR(30) PRIMARY KEY,
    Password VARCHAR(128) NOT NULL,
    Salt VARCHAR(32) NOT NULL
);

CREATE TABLE Users (
    Username VARCHAR(30) PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Age INT NOT NULL,
    Sex CHAR NOT NULL
);

INSERT INTO Users (Username, FirstName, LastName, Age, Sex) VALUES ('gigel20cm', 'George', 'Barna', 24, 'M');
INSERT INTO Users (Username, FirstName, LastName, Age, Sex) VALUES ('bmw1995', 'Giany', 'Mocanu', 28, 'M');
INSERT INTO Users (Username, FirstName, LastName, Age, Sex) VALUES ('lili_unghii_gel', 'Liliana', 'Tigaie', 21, 'F');
INSERT INTO Users (Username, FirstName, LastName, Age, Sex) VALUES ('maria_lov3', 'Maria', 'Ioana', 18, 'F');
INSERT INTO Users (Username, FirstName, LastName, Age, Sex) VALUES ('lightyagami', 'Virgil', 'Popescu', 20, 'M');
INSERT INTO Users (Username, FirstName, LastName, Age, Sex) VALUES ('alina_dumitru', 'Alina', 'Dumitru', 23, 'F');

-- Passwords for all this username is "Anaaremere123@"
INSERT INTO Authentication (Username, Password, Salt) VALUES ('gigel20cm', 'apEWvdwCd+QwzFIMjJ8k4osGuvazRQc1o7AkMi+YAhjYfd2p0GIY2BVPiXXxES/HjX5N73sRUZ7jBatU++gyag==',
'XD0M2hKRkrFoTcShWJ/BSA==');

INSERT INTO Authentication (Username, Password, Salt) VALUES ('bmw1995', 'TCP5jv8UlHGp28uB+VXY7A6//CV2AIM4FUqZFQbJRiRFqmFcXqzKy0iFOdtDHscpUMVpGC21Gh5PGBn0s2x3Jw===', 'Gmfn1BkBvhzLQubuNWehIg==');

INSERT INTO Authentication (Username, Password, Salt) VALUES ('maria_lov3', 
'ppcMYWOD58ocN6iqE9hOf0tNB2zLetHGzZjmbRynjNggKYNpDrsgEq9YCZLMqsrgjmGOI1I5SOQgb+EdkixShQ==',
'n8VLWmCKvSvIVoF8iYWtag==');

INSERT INTO Authentication (Username, Password, Salt) VALUES ('lili_unghii_gel', 
'31TBBemnMvsWPKn7LsTVktT5D4UnPz4ozRHH/5L786DlLu+FE1Nc5191cUBJLSDoXy0h346Np/hrpxs9u0qDfQ==',
'RWW+6dbBCYmFgGSDqWzvrQ==');

INSERT INTO Authentication (Username, Password, Salt) VALUES ('lightyagami', 
'odT78KMtjv2jK3Dd8Hh6cv5O1qikdWoAz/2ONJt4fs6AgmLDQ7nJYC7IpqRQ7aV2DUyVfns+uCYA0dCUmfcO4w==',
'WntOsTWxVwbk7fwAj+GtGg==');

INSERT INTO Authentication (Username, Password, Salt) VALUES ('alina_dumitru', 
'OW4j+HT+ei7FXhBi8HAyicPYewb2KSmPLpZjPPg4YZS8P+/y9knJOg+Go81axwdq7IX+a/ydvJy56lv0kYWPMQ==',
'1e+hkOybpc8wXtPxHmGI2w==');


