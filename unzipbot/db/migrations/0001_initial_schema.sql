-- description: Initial v7 relational schema.

CREATE TABLE IF NOT EXISTS Upload_Modes (
    type TEXT PRIMARY KEY CHECK(type IN ('media', 'doc'))
);

CREATE TABLE IF NOT EXISTS Languages (
    locale TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Task_Types (
    type TEXT PRIMARY KEY CHECK(type IN ('extract', 'merge'))
);

CREATE TABLE IF NOT EXISTS Payment_Means (
    mean TEXT PRIMARY KEY CHECK(mean IN ('paypal', 'telegram', 'gh', 'bmac', 'custom'))
);

CREATE TABLE IF NOT EXISTS Payment_Frequencies (
    freq TEXT PRIMARY KEY CHECK(freq IN ('monthly', 'yearly'))
);

CREATE TABLE IF NOT EXISTS Vip_Statuses (
    status TEXT PRIMARY KEY CHECK(status IN ('active', 'expired', 'cancelled', 'paused'))
);

CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY,
    is_banned INTEGER NOT NULL DEFAULT 0 CHECK(is_banned IN (0, 1)),
    upload_mode TEXT NOT NULL DEFAULT 'media' REFERENCES Upload_Modes(type),
    lang TEXT NOT NULL DEFAULT 'en' REFERENCES Languages(locale),
    uploaded_count INTEGER NOT NULL DEFAULT 0 CHECK(uploaded_count >= 0)
);

CREATE TABLE IF NOT EXISTS System (
    id INTEGER PRIMARY KEY CHECK(id = 0),
    boot_time REAL,
    old_boot_time REAL,
    maintenance INTEGER NOT NULL DEFAULT 0 CHECK(maintenance IN (0, 1))
);

CREATE TABLE IF NOT EXISTS Thumb (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL REFERENCES User(id) ON DELETE CASCADE,
    slot INTEGER NOT NULL DEFAULT 0 CHECK(slot >= 0),
    file_id TEXT NOT NULL,
    temp_id TEXT,
    UNIQUE(uid, slot)
);

CREATE TABLE IF NOT EXISTS Password (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL REFERENCES User(id) ON DELETE CASCADE,
    value TEXT NOT NULL,
    UNIQUE(uid, value)
);

CREATE TABLE IF NOT EXISTS Task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL REFERENCES User(id) ON DELETE CASCADE,
    user_task_nb INTEGER NOT NULL,
    started INTEGER NOT NULL DEFAULT 0 CHECK(started IN (0, 1)),
    start_time REAL NOT NULL DEFAULT 0,
    type TEXT NOT NULL REFERENCES Task_Types(type),
    cancelled INTEGER NOT NULL DEFAULT 0 CHECK(cancelled IN (0, 1)),
    message_id INTEGER NOT NULL,
    UNIQUE(uid, type, message_id)
);

CREATE TABLE IF NOT EXISTS Vip (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER NOT NULL UNIQUE REFERENCES User(id) ON DELETE CASCADE,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' REFERENCES Vip_Statuses(status),
    early INTEGER NOT NULL DEFAULT 0 CHECK(early IN (0, 1)),
    donator INTEGER NOT NULL DEFAULT 0 CHECK(donator IN (0, 1)),
    lifetime INTEGER NOT NULL DEFAULT 0 CHECK(lifetime IN (0, 1)),
    gifted INTEGER NOT NULL DEFAULT 0 CHECK(gifted IN (0, 1)),
    first_start TEXT NOT NULL,
    nb_payments INTEGER NOT NULL DEFAULT 1 CHECK(nb_payments >= 0),
    gap INTEGER NOT NULL DEFAULT 0 CHECK(gap IN (0, 1))
);

CREATE TABLE IF NOT EXISTS Vip_Payment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vip_id INTEGER NOT NULL REFERENCES Vip(id) ON DELETE CASCADE,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    mean TEXT NOT NULL REFERENCES Payment_Means(mean),
    proof TEXT NOT NULL UNIQUE,
    frequency TEXT NOT NULL REFERENCES Payment_Frequencies(freq),
    paid_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Vip_Referral (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vip_id INTEGER NOT NULL UNIQUE REFERENCES Vip(id) ON DELETE CASCADE,
    referral TEXT NOT NULL UNIQUE,
    referee TEXT UNIQUE
);
