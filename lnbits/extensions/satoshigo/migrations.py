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
            tplat TEXT NOT NULL,
            tplon TEXT NOT NULL,
            btlat TEXT NOT NULL,
            btlon TEXT NOT NULL,
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
        CREATE TABLE IF NOT EXISTS satoshigo_players (
            id TEXT PRIMARY KEY,
            admin TEXT NOT NULL,
            time TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """
    )