async def m001_initial(db):
    """
    Initial pay_links table.
    """
    await db.execute(
        f"""
        CREATE TABLE payerinv.pay_links (
            id {db.serial_primary_key},
            wallet TEXT NOT NULL,
            description TEXT NOT NULL,
            currency TEXT,
            min INTEGER NOT NULL,
            max INTEGER NOT NULL
        );
        """
    )
