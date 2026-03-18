USE HumanManagement;
GO

CREATE DATABASE HumanManagement;
GO

USE HumanManagement;
GO


CREATE TABLE HumanType (
    typeid INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);
GO

CREATE TABLE Human (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    dob DATE,
    gender CHAR(1),
    typeid INT,

    CONSTRAINT FK_Human_HumanType FOREIGN KEY (typeid) 
    REFERENCES HumanType(typeid)
);
GO

-- Thêm dữ liệu vào bảng HumanType
INSERT INTO HumanType (typeid, name) VALUES 
(1, 'Employee'),
(2, 'Customer'),
(3, 'Freelancer');

-- Thêm dữ liệu vào bảng Human
INSERT INTO Human (id, name, dob, gender, typeid) VALUES 
(101, 'Nguyen Van A', '1995-05-15', 'M', 1),
(102, 'Tran Thi B', '1998-10-20', 'F', 1),
(103, 'Le Van C', '2000-01-01', 'M', 2),
(104, 'Pham Minh D', '1992-03-12', 'M', 3),
(105, 'Hoang Anh E', '1997-07-07', 'F', 2);
GO

SELECT * FROM Human;