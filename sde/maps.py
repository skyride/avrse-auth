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


AttributeCategory = [
    ('id', 'categoryID'),
    ('name', 'categoryName'),
    ('description', 'categoryDescription')
]


AttributeType = [
    ('id', 'attributeID'),
    ('name', 'attributeName'),
    ('category_id', 'categoryID'),
    ('description', 'description'),
    ('icon_id', 'iconID'),
    ('default_value', 'defaultValue'),
    ('published', 'published'),
    ('display_name', 'displayName'),
    ('unit_id', 'unitID'),
    ('stackable', 'stackable'),
    ('high_is_good', 'highIsGood')
]


TypeAttribute = [
    ('type_id', 'typeID'),
    ('attribute_id', 'attributeID'),
    ('value_int', 'valueInt'),
    ('value_float', 'valueFloat')
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
