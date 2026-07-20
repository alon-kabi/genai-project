-------------------------------------------------
-- יצירת Database
-------------------------------------------------

IF DB_ID('Tech') IS NULL
BEGIN
    CREATE DATABASE Tech;
END;
GO

-------------------------------------------------
-- מעבר ל Database
-------------------------------------------------

USE Tech;
GO

-------------------------------------------------
-- מחיקת טבלה קיימת
-------------------------------------------------

IF OBJECT_ID('dbo.Schedule', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.Schedule;
END;


-------------------------------------------------
-- יצירת טבלת Schedule
-------------------------------------------------

CREATE TABLE dbo.Schedule
(
    ScheduleID INT IDENTITY(1,1) PRIMARY KEY,

    [Date] DATE NOT NULL,

    InterviewTime TIME(0) NOT NULL,

    Position VARCHAR(50) NOT NULL,

    Available BIT NOT NULL,

    MeetingType VARCHAR(10) NOT NULL
);



-------------------------------------------------
-- יצירת נתוני ראיונות
-- שנה 2026
-------------------------------------------------

WITH Dates AS
(
    SELECT CAST('2026-01-01' AS DATE) AS InterviewDate

    UNION ALL

    SELECT DATEADD(DAY,1,InterviewDate)

    FROM Dates

    WHERE InterviewDate < '2026-12-31'
),


Times AS
(
    SELECT CAST('09:00:00' AS TIME(0)) AS InterviewTime

    UNION ALL SELECT CAST('10:00:00' AS TIME(0))
    UNION ALL SELECT CAST('11:00:00' AS TIME(0))
    UNION ALL SELECT CAST('12:00:00' AS TIME(0))
    UNION ALL SELECT CAST('13:00:00' AS TIME(0))
    UNION ALL SELECT CAST('14:00:00' AS TIME(0))
    UNION ALL SELECT CAST('15:00:00' AS TIME(0))
    UNION ALL SELECT CAST('16:00:00' AS TIME(0))
    UNION ALL SELECT CAST('17:00:00' AS TIME(0))
),


Positions AS
(
    SELECT 'Python Dev' AS Position

    UNION ALL SELECT 'SQL Dev'

    UNION ALL SELECT 'Data Analyst'

    UNION ALL SELECT 'ML Engineer'
)



INSERT INTO dbo.Schedule
(
    [Date],
    InterviewTime,
    Position,
    Available,
    MeetingType
)


SELECT

    d.InterviewDate,

    t.InterviewTime,

    p.Position,


    -- 70% זמינות

    CASE

        WHEN ABS(
            CHECKSUM(
                d.InterviewDate,
                t.InterviewTime,
                p.Position
            )
        ) % 10 < 7

        THEN 1

        ELSE 0

    END AS Available,


    -- סוג פגישה

    CASE

        WHEN ABS(
            CHECKSUM(
                p.Position,
                t.InterviewTime
            )
        ) % 2 = 0

        THEN 'Zoom'

        ELSE 'Office'

    END AS MeetingType


FROM Dates d

CROSS JOIN Times t

CROSS JOIN Positions p


OPTION (MAXRECURSION 400);
GO


-------------------------------------------------
-- InterviewBooking
-------------------------------------------------

USE Tech;
GO

IF OBJECT_ID('dbo.InterviewBooking', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.InterviewBooking;
END;
GO

CREATE TABLE dbo.InterviewBooking (
    BookingID INT IDENTITY(1,1) PRIMARY KEY,

    Position VARCHAR(100) NOT NULL,

    Interview_date DATE NOT NULL,

    Interview_time TIME(0) NOT NULL,

    Interview_type VARCHAR(100) NOT NULL,

    Status VARCHAR(20) NULL,

    CandidateName NVARCHAR(100) NULL,

    CandidatePhone VARCHAR(20) NULL,

    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),

    UpdatedDate DATETIME NULL
);
GO

-- אינדקסים
CREATE INDEX IX_InterviewBooking_Date
ON dbo.InterviewBooking (Interview_date);

CREATE INDEX IX_InterviewBooking_Position
ON dbo.InterviewBooking (Position);

CREATE INDEX IX_InterviewBooking_Status
ON dbo.InterviewBooking (Status);
GO

