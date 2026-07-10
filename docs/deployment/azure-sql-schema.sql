-- Habit Life RPG Chapter 8 Azure SQL schema draft.
-- This mirrors the MVP Users/Habits model used by the SQLite local chapters.

CREATE TABLE Users (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(80) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(255) NOT NULL,
    Level INT NOT NULL DEFAULT 1,
    Exp INT NOT NULL DEFAULT 0,
    Gold INT NOT NULL DEFAULT 0,
    Hp INT NOT NULL DEFAULT 100,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE Habits (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL,
    Title NVARCHAR(120) NOT NULL,
    Category NVARCHAR(40) NOT NULL,
    LastCheckIn DATETIME2 NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Habits_Users FOREIGN KEY (UserId) REFERENCES Users(Id)
);

CREATE INDEX IX_Habits_UserId ON Habits(UserId);
