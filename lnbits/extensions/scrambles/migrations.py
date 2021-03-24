async def m001_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS scrambles_game (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            title TEXT NOT NULL,
            top_left TEXT NOT NULL,
            bottom_right TEXT NOT NULL,
            time TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """
    )
async def m002_initial(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS scrambles_funding (
            id TEXT PRIMARY KEY,
            scrambles_id TEXT NOT NULL,
            wallet TEXT NOT NULL,
            top_left TEXT NOT NULL,
            bottom_right TEXT NOT NULL,
            amount INTEGER NOT NULL,
            payment_hash TEXT NOT NULL,
            confirmed BOOLEAN DEFAULT 0,
            time TIMESTAMP NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """
    )