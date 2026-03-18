IF DB_ID('HumanManagement') IS NULL
BEGIN
    CREATE DATABASE HumanManagement;
END
GO

USE HumanManagement;
GO

IF OBJECT_ID('dbo.trg_Human_ValidateInsert', 'TR') IS NOT NULL
    DROP TRIGGER dbo.trg_Human_ValidateInsert;
GO

IF OBJECT_ID('dbo.Human', 'U') IS NOT NULL
    DROP TABLE dbo.Human;
GO

IF OBJECT_ID('dbo.HumanType', 'U') IS NOT NULL
    DROP TABLE dbo.HumanType;
GO

CREATE TABLE HumanType (
    typeid INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);
GO

CREATE TABLE Human (
    id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    dob DATE NULL,
    gender CHAR(1) NULL,
    typeid INT,
    CONSTRAINT FK_Human_HumanType FOREIGN KEY (typeid)
        REFERENCES HumanType(typeid)
);
GO

CREATE TRIGGER dbo.trg_Human_ValidateInsert
ON dbo.Human
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (
        SELECT 1
        FROM inserted i
        GROUP BY i.id
        HAVING COUNT(*) > 1
    )
    BEGIN
        RAISERROR(N'ID bị trùng trong dữ liệu insert.', 16, 1);
        RETURN;
    END;

    IF EXISTS (
        SELECT 1
        FROM inserted i
        INNER JOIN dbo.Human h ON h.id = i.id
    )
    BEGIN
        RAISERROR(N'ID đã tồn tại, không được trùng.', 16, 1);
        RETURN;
    END;

    IF EXISTS (
        SELECT 1
        FROM inserted i
        WHERE i.dob IS NOT NULL
          AND (i.dob < '1900-01-01' OR i.dob > '2026-12-31')
    )
    BEGIN
        RAISERROR(N'Ngày sinh phải trong khoảng từ 1900-01-01 đến 2026-12-31.', 16, 1);
        RETURN;
    END;

    INSERT INTO dbo.Human (id, name, dob, gender, typeid)
    SELECT i.id, i.name, i.dob, i.gender, i.typeid
    FROM inserted i;
END;
GO

-- Thêm dữ liệu vào bảng HumanType
INSERT INTO HumanType (typeid, name)
VALUES
    (1, 'Employee'),
    (2, 'Customer'),
    (3, 'Freelancer');

-- Thêm dữ liệu vào bảng Human
INSERT INTO Human (id, name, dob, gender, typeid)
VALUES
    (101, 'Nguyen Van A', '1995-05-15', 'M', 1),
    (102, 'Tran Thi B', '1998-10-20', 'F', 1),
    (103, 'Le Van C', '2000-01-01', 'M', 2),
    (104, 'Pham Minh D', '1992-03-12', 'M', 3),
    (105, 'Hoang Anh E', '1997-07-07', 'F', 2);
GO

SELECT * FROM Human;