import aiosqlite

async def check_tables():
    # Guilds
    async with aiosqlite.connect('guilds.db') as db:
        # Creates the "guilds" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS guilds (
            GuildId INTEGER PRIMARY KEY AUTOINCREMENT,
            GuildName STRING,
            GuildDescription STRING,
            GuildLevel INTEGER,
            GuildBoosts INTEGER,
            GuildMembers INTEGER,
            OwnerId INTEGER,
            CommandCooldown INTEGER DEFAULT 30
        )
        """)

        # Creates the "guild_members" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS guild_members (
            MembershipId INTEGER PRIMARY KEY AUTOINCREMENT,
            GuildName STRING,
            GuildID INTEGER,
            MemberID INTEGER,
            PrimaryID INTEGER
        )
        """)

        # Creates the "guild_invites" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS guild_invites (
            InviteId INTEGER PRIMARY KEY AUTOINCREMENT,
            GuildId INTEGER,
            MessageId INTEGER
        )
        """)

        # Creates the "profiles" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            ProfileId INTEGER PRIMARY KEY AUTOINCREMENT,
            UserId INTEGER,
            DisplayName STRING,
            Description STRING,
            Status STRING,
            DisplayPicture STRING,
            Thumbnail STRING,
            embedColor STRING
        )
        """)
        await db.commit()

    # Quacky
    async with aiosqlite.connect('quacky.db') as db:
        # Creates the "inventories" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS inventories (
            InvId INTEGER PRIMARY KEY AUTOINCREMENT,
            UserId INTEGER,
            Items TEXT DEFAULT '{}'
        )
        """)

        # Creates the "dimensions" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS dimensions (
            DimId INTEGER PRIMARY KEY AUTOINCREMENT,
            DimName TEXT,
            Blocks TEXT DEFAULT '{}',
            Mobs TEXT DEFAULT '{}'
        )
        """)

        # Creates the "wallets" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            WalletId INTEGER PRIMARY KEY AUTOINCREMENT,
            UserId INTEGER,
            Coins INTEGER DEFAULT 0
        )
        """)

        # Creates the "shop" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS shop (
            ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
            ItemName STRING,
            SafeName STRING,
            Cost INTEGER
        )
        """)

        # Crates the "items" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS items (
            ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
            ItemName STRING,
            SellValue INTEGER DEFAULT 0,
            CanSell INTEGER DEFAULT 0,
            CostValue INTEGER DEFAULT 0,
            CanBuy INTEGER DEFAULT 0,
            CanSmelt INTEGER DEFAULT 0,
            HarvestLevel INTEGER DEFAULT 0,
            Emoji STRING DEFAULT ''
        )
        """)
        await db.commit()