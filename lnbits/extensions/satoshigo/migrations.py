async def m001_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS satoshigo_game (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            wallet_key TEXT NOT NULL,
            title TEXT NOT NULL,
            coins TEXT NOT NULL,
            render_pin INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            time TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """
    )


async def m002_initial(db):
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


async def m003_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS satoshigo_player (
            id TEXT PRIMARY KEY,
            user_name TEXT NOT NULL,
            walletid TEXT NOT NULL,
            adminkey TEXT NOT NULL,
            inkey TEXT NOT NULL,
            time TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """
    )


async def m004_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS satoshigo_players (
            inkey TEXT PRIMARY KEY,
            game_id TEXT NOT NULL,
            user_name TEXT NOT NULL,
            time TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """
    )


async def m005_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS satoshigo_areas (
            id TEXT PRIMARY KEY,
            lng INTEGER NOT NULL,
            lat INTEGER NOT NULL,
            pot INTEGER NOT NULL,
            time TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """
    )
