# A set of map tables for mapping SDE columns to attributes in our objects
# The first entry is used as the primary key

Region = [
    ('id', 'regionID'),
    ('name', 'regionName'),
    ('x', 'x'),
    ('y', 'y'),
    ('z', 'z'),
    ('radius', 'radius')
]

Constellation = [
    ('id', 'constellationID'),
    ('name', 'constellationName'),
    ('region_id', 'regionID'),
    ('x', 'x'),
    ('y', 'y'),
    ('z', 'z'),
    ('radius', 'radius')
]

System = [
    ('id', 'solarSystemID'),
    ('name', 'solarSystemName'),
    ('region_id', 'regionID'),
    ('constellation_id', 'constellationID'),
    ('x', 'x'),
    ('y', 'y'),
    ('z', 'z'),
    ('luminosity', 'luminosity'),
    ('border', 'border'),
    ('fringe', 'fringe'),
    ('corridor', 'corridor'),
    ('hub', 'hub'),
    ('international', 'international'),
    ('security', 'security'),
    ('radius', 'radius'),
    ('sun_id', 'sunTypeID'),
    ('security_class', 'securityClass')
]


MarketGroup = [
    ('id', 'marketGroupID'),
    ('parent_id', 'parentGroupID'),
    ('name', 'marketGroupName'),
    ('description', 'description'),
    ('icon_id', 'iconID'),
    ('has_types', 'hasTypes')
]


Category = [
    ('id', 'categoryID'),
    ('name', 'categoryName'),
    ('icon_id', 'iconID'),
    ('published', 'published')
]


Group = [
    ('id', 'groupID'),
    ('name', 'groupName'),
    ('category_id', 'categoryID'),
    ('icon_id', 'iconID'),
    ('anchored', 'anchored'),
    ('anchorable', 'anchorable'),
    ('fittable_non_singleton', 'fittableNonSingleton'),
    ('published', 'published')
]


Type = [
    ('id', 'typeID'),
    ('group_id', 'groupID'),
    ('name', 'typeName'),
    ('description', 'description'),
    ('mass', 'mass'),
    ('volume', 'volume'),
    ('capacity', 'capacity'),
    ('published', 'published'),
    ('market_group_id', 'marketGroupID'),
    ('icon_id', 'iconID')
]


Station = [
    ('id', 'stationID'),
    ('name', 'stationName'),
    ('type_id', 'stationTypeID'),
    ('system_id', 'solarSystemID'),
    ('x', 'x'),
    ('y', 'y'),
    ('z', 'z'),
]
