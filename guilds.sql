--
START TRANSACTION;

-- Table: guild_invites

-- Table: guild_members

-- Table: guilds

-- Table: dimensions
INSERT INTO dimensions (DimId, DimName, Blocks, Mobs) VALUES (2, 'Overworld', '{"Iron Ore": 12, "Copper Ore": 14, "Silver Ore": 15, "Gold Ore": 16, "Diamond": 21, "Emerald": 22, "Coal": 26}', '{"Test": [[12, "Iron Ore", 35, 1, 0, 0, 1, 1, "<:ironore:1244857703340445708>"], 100], "Test2": ["Gold Ore", 200]}');

-- Table: inventories
INSERT INTO inventories (InvId, UserId, Items) VALUES (1, 503641822141349888, '{"Log": 127, "Netherite Axe": 2, "Netherite Pickaxe": 1, "Fortune 3": 1, "Coal": 57, "Iron Ingot": 5, "Gold Ingot": 5, "Copper Ingot": 5, "Diamond": 5, "Emerald": 6}');
INSERT INTO inventories (InvId, UserId, Items) VALUES (2, 1029146068996325447, '{"Log": 275, "Netherite Axe": 1, "Wooden Axe": 1, "Iron Ore": 1163, "Wooden Pickaxe": 1, "Gold Ore": 3, "Silver Ore": 11, "Copper Ore": 2, "Emerald": 6, "Netherite Pickaxe": 1, "Fortune 3": 1, "Iron Ingot": 112, "Coal": 120.0}');
INSERT INTO inventories (InvId, UserId, Items) VALUES (3, 878174748436234291, '{}');
INSERT INTO inventories (InvId, UserId, Items) VALUES (4, 520584647545978890, '{"Log": 9}');
INSERT INTO inventories (InvId, UserId, Items) VALUES (5, 400740456943845396, '{"Netherite Axe": 1, "Log": 36}');
INSERT INTO inventories (InvId, UserId, Items) VALUES (6, 125344262081609728, '{}');

-- Table: profiles
INSERT INTO profiles (ProfileId, UserId, DisplayName, Description, Status, DisplayPicture, Thumbnail, embedColor) VALUES (1, 1029146068996325447, 'Andrew', 'cs2 gooner', 'i am a loser', 'https://media.tenor.com/FbDCpv1tdSoAAAAi/lean.gif', 'https://media.tenor.com/S894mCfpIZ0AAAAM/izdi-morshall-prime-real-izdi-morshall.gif', '0xAC6BF1');
INSERT INTO profiles (ProfileId, UserId, DisplayName, Description, Status, DisplayPicture, Thumbnail, embedColor) VALUES (2, 503641822141349888, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO profiles (ProfileId, UserId, DisplayName, Description, Status, DisplayPicture, Thumbnail, embedColor) VALUES (3, 125344262081609728, NULL, NULL, NULL, NULL, NULL, 'red');

-- Table: items
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (7, 'Wooden Axe', 0, 0, 100, 1, 0, 0, '<:axe_wood:1247118028420677654>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (8, 'Stone Axe', 0, 0, 250, 1, 0, 0, '<:axe_stone:1247118027217178655>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (9, 'Iron Axe', 0, 0, 500, 1, 0, 0, '<:axe_iron:1247118024989872178>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (10, 'Diamond Axe', 0, 0, 1500, 1, 0, 0, '<:axe_diamond:1247118023911931966>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (11, 'Netherite Axe', 0, 0, 2500, 1, 0, 0, '<:axe_netherite:1247118026265067570>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (12, 'Iron Ore', 35, 1, 0, 0, 1, 1, '<:ironore:1244857703340445708>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (13, 'Wooden Pickaxe', 0, 0, 120, 1, 0, 0, '<:pick_wood:1248191409882927145>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (14, 'Copper Ore', 25, 1, 0, 0, 1, 1, '<:copperore:1244857698550419488>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (15, 'Silver Ore', 45, 1, 0, 0, 1, 2, '<:silverore:1244857707203264562>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (16, 'Gold Ore', 55, 1, 0, 0, 1, 2, '<:goldore:1244857702627278878>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (17, 'Stone Pickaxe', 0, 0, 300, 1, 0, 0, '<:pick_stone:1248318203344453652>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (18, 'Iron Pickaxe', 0, 0, 650, 1, 0, 0, '<:pick_iron:1248318201440505876>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (19, 'Diamond Pickaxe', 0, 0, 2000, 1, 0, 0, '<:pick_diamond:1248318200437932102>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (20, 'Netherite Pickaxe', 0, 0, 3000, 1, 0, 0, '<:pick_netherite:1248318202383958047>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (21, 'Diamond', 100, 1, 0, 0, 0, 3, '<:diamond:1244857699770961921>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (22, 'Emerald', 125, 1, 0, 0, 0, 3, '<:emerald:1244857701121523732>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (23, 'Fortune 1', 300, 1, 500, 1, 0, 0, '<a:enchant:1249174933347504168>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (24, 'Fortune 2', 500, 1, 1000, 1, 0, 0, '<a:enchant:1249174933347504168>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (25, 'Fortune 3', 1000, 1, 1500, 1, 0, 0, '<a:enchant:1249174933347504168>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (26, 'Coal', 0, 0, 0, 0, 0, 0, '<:coal:1244858270414540861>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (27, 'Iron Ingot', 50, 1, 0, 0, 0, 0, '<:iron_ingot:1249180923489026100>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (28, 'Copper Ingot', 40, 1, 0, 0, 0, 0, '<:copper_ingot:1249180921387815017>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (29, 'Silver Ingot', 65, 1, 0, 0, 0, 0, '<:silver_ingot:1249180924042809366>');
INSERT INTO items (ItemId, ItemName, SellValue, CanSell, CostValue, CanBuy, CanSmelt, HarvestLevel, Emoji) VALUES (30, 'Gold Ingot', 80, 1, 0, 0, 0, 0, '<:gold_ingot:1249180922612289566>');

-- Table: shop
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Wooden Axe', 'WoodenAxe', 100);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Stone Axe', 'StoneAxe', 250);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Iron Axe', 'IronAxe', 500);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Diamond Axe', 'DiamondAxe', 1500);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Netherite Axe', 'NetheriteAxe', 2500);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Wooden Pickaxe', 'WoodenPickaxe', 120);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Stone Pickaxe', 'StonePickaxe', 300);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Iron Pickaxe', 'IronPickaxe', 650);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Diamond Pickaxe', 'DiamondPickaxe', 2000);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Netherite Pickaxe', 'NetheritePickaxe', 3000);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Fortune 1', 'Fortune1', 750);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Fortune 2', 'Fortune2', 1000);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Fortune 3', 'Fortune3', 1500);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Sharpness 1', 'Sharpness1', 500);
INSERT INTO shop (ItemId, ItemName, SafeName, Cost) VALUES (1, 'Wooden Sword', 'WoodenSword', 140);

-- Table: wallets
INSERT INTO wallets (WalletId, UserId, Coins) VALUES (1, 1029146068996325447, 2149517348);
INSERT INTO wallets (WalletId, UserId, Coins) VALUES (2, 503641822141349888, 99993500);
INSERT INTO wallets (WalletId, UserId, Coins) VALUES (3, 878174748436234291, 0);
INSERT INTO wallets (WalletId, UserId, Coins) VALUES (4, 400740456943845396, 55);
INSERT INTO wallets (WalletId, UserId, Coins) VALUES (5, 125344262081609728, 0);

COMMIT;