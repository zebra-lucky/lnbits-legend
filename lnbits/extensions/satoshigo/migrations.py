async def m001_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS satoshigo_funding (
            id TEXT PRIMARY KEY,
            satoshigo_id TEXT NOT NULL,
            wallet TEXT NOT NULL,
            tplat INTEGER NOT NULL,
            tplon INTEGER NOT NULL,
            btlat INTEGER NOT NULL,
            btlon INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            payment_hash TEXT NOT NULL,
            confirmed BOOLEAN DEFAULT 0,
            time TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """
    )


async def m002_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS satoshigo_game (
            hash TEXT PRIMARY KEY,
            title TEXT PRIMARY KEY,
            description TEXT PRIMARY KEY,
            area TEXT PRIMARY KEY,
            appearance TEXT PRIMARY KEY,
            isDefault INTEGER PRIMARY KEY,
            flags INTEGER PRIMARY KEY,
            totalFunds INTEGER PRIMARY KEY,
            fundsCollected INTEGER PRIMARY KEY
        );
    """
    )


async def m003_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS satoshigo_players (
            id TEXT PRIMARY KEY,
            user_name TEXT NOT NULL,
            adminkey TEXT NOT NULL,
            inkey TEXT PRIMARY KEY,
            gameHash TEXT NOT NULL,
            enableHiScore INTEGER NULL
        );
    """
    )


async def m004_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS satoshigo_areas (
            hash TEXT PRIMARY KEY,
            lon INTEGER NOT NULL,
            lat INTEGER NOT NULL,
            radius INTEGER NOT NULL,
            gameHash TEXT NOT NULL,
            time TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """
    )


async def m005_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS satoshigo_items (
            hash TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            areaHash TEXT NOT NULL,
            data INTEGER NOT NULL,
            appearance TEXT NOT NULL
        );
    """
    )
