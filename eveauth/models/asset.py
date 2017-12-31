from django.db import models
from django.db.models import Q, F, Sum

from eveauth.models.character import Character
from sde.models import Type, System, Station

class Asset(models.Model):
    id = models.BigIntegerField(primary_key=True)
    character = models.ForeignKey(Character, related_name="assets")
    parent = models.ForeignKey('self', null=True, default=None, db_constraint=False, related_name="items")

    type = models.ForeignKey(Type)
    flag = models.CharField(max_length=64, db_index=True)

    quantity = models.IntegerField(default=0)
    raw_quantity = models.IntegerField(default=0)
    singleton = models.BooleanField()

    system = models.ForeignKey(System, null=True, default=None)
    station = models.ForeignKey(Station, null=True, default=None)
    name = models.CharField(max_length=64, null=True, default=None)

    def __str__(self):
        return "%s (%s)" % (
            self.type.name,
            self.quantity
        )

    @property
    def price(self):
        return float(
            self.items.aggregate(
                total = Sum(
                    F('type__sell') * F('quantity'),
                    output_field=models.FloatField()
                )
            )['total']
        or 0) + (float(self.type.sell) * self.quantity)

    def ship_items(self):
        def getid(x):
            if x != None:
                return x.id
            else:
                return -1

        return self.items.exclude(
            id__in=map(
                getid,
                self.mods()
            )
        ).order_by(
            'flag',
            '-type__sell',
            'type__name'
        )

    @property
    def div_id(self):
        if self.type.group.category.id == 8:
            return self.flag
        else:
            return "%s-charge" % self.flag

    @property
    def is_ship(self):
        return self.singleton and self.type.group.category.id == 6

    # Style for items on the fitting panel
    def style(self):
        if self.type.group.category.id != 8:
            return {
                "HiSlot0": "position:absolute; left:73px; top:60px; width:32px; height:32px;",
                "HiSlot1": "position:absolute; left:102px; top:42px; width:32px; height:32px;",
                "HiSlot2": "position:absolute; left:134px; top:27px; width:32px; height:32px;",
                "HiSlot3": "position:absolute; left:169px; top:21px; width:32px; height:32px;",
                "HiSlot4": "position:absolute; left:203px; top:22px; width:32px; height:32px;",
                "HiSlot5": "position:absolute; left:238px; top:30px; width:32px; height:32px;",
                "HiSlot6": "position:absolute; left:270px; top:45px; width:32px; height:32px;",
                "HiSlot7": "position:absolute; left:295px; top:64px; width:32px; height:32px;",
                "MedSlot0": "position:absolute; left:26px; top:140px; width:32px; height:32px;",
                "MedSlot1": "position:absolute; left:24px; top:176px; width:32px; height:32px;",
                "MedSlot2": "position:absolute; left:23px; top:212px; width:32px; height:32px;",
                "MedSlot3": "position:absolute; left:30px; top:245px; width:32px; height:32px;",
                "MedSlot4": "position:absolute; left:46px; top:278px; width:32px; height:32px;",
                "MedSlot5": "position:absolute; left:69px; top:304px; width:32px; height:32px;",
                "MedSlot6": "position:absolute; left:100px; top:328px; width:32px; height:32px;",
                "MedSlot7": "position:absolute; left:133px; top:342px; width:32px; height:32px;",
                "LoSlot0": "position:absolute; left:344px; top:143px; width:32px; height:32px;",
                "LoSlot1": "position:absolute; left:350px; top:178px; width:32px; height:32px;",
                "LoSlot2": "position:absolute; left:349px; top:213px; width:32px; height:32px;",
                "LoSlot3": "position:absolute; left:340px; top:246px; width:32px; height:32px;",
                "LoSlot4": "position:absolute; left:323px; top:277px; width:32px; height:32px;",
                "LoSlot5": "position:absolute; left:300px; top:304px; width:32px; height:32px;",
                "LoSlot6": "position:absolute; left:268px; top:324px; width:32px; height:32px;",
                "LoSlot7": "position:absolute; left:234px; top:338px; width:32px; height:32px;",
                "RigSlot0": "position:absolute; left:148px; top:259px; width:32px; height:32px;",
                "RigSlot1": "position:absolute; left:185px; top:267px; width:32px; height:32px;",
                "RigSlot2": "position:absolute; left:221px; top:259px; width:32px; height:32px;",
                "SubSystemSlot0": "position:absolute; left:117px; top:131px; width:32px; height:32px;",
                "SubSystemSlot1": "position:absolute; left:147px; top:108px; width:32px; height:32px;",
                "SubSystemSlot2": "position:absolute; left:184px; top:98px; width:32px; height:32px;",
                "SubSystemSlot3": "position:absolute; left:221px; top:107px; width:32px; height:32px;"
            }[self.flag]
        else:
            return {
                "HiSlot0": "position:absolute; left:94px; top:88px; width:24px; height:24px;",
                "HiSlot1": "position:absolute; left:119px; top:70px; width:24px; height:24px;",
                "HiSlot2": "position:absolute; left:146px; top:58px; width:24px; height:24px;",
                "HiSlot3": "position:absolute; left:175px; top:52px; width:24px; height:24px;",
                "HiSlot4": "position:absolute; left:204px; top:52px; width:24px; height:24px;",
                "HiSlot5": "position:absolute; left:232px; top:60px; width:24px; height:24px;",
                "HiSlot6": "position:absolute; left:258px; top:72px; width:24px; height:24px;",
                "HiSlot7": "position:absolute; left:280px; top:91px; width:24px; height:24px;",
                "MedSlot0": "position:absolute; left:59px; top:154px; width:24px; height:24px;",
                "MedSlot1": "position:absolute; left:54px; top:182px; width:24px; height:24px;",
                "MedSlot2": "position:absolute; left:56px; top:210px; width:24px; height:24px;",
                "MedSlot3": "position:absolute; left:62px; top:238px; width:24px; height:24px;",
                "MedSlot4": "position:absolute; left:76px; top:265px; width:24px; height:24px;",
                "MedSlot5": "position:absolute; left:94px; top:288px; width:24px; height:24px;",
                "MedSlot6": "position:absolute; left:118px; top:305px; width:24px; height:24px;",
                "MedSlot7": "position:absolute; left:146px; top:318px; width:24px; height:24px;",
                "LoSlot0": "position:absolute; left:315px; top:150px; width:24px; height:24px;",
                "LoSlot1": "position:absolute; left:319px; top:179px; width:24px; height:24px;",
                "LoSlot2": "position:absolute; left:318px; top:206px; width:24px; height:24px;",
                "LoSlot3": "position:absolute; left:310px; top:234px; width:24px; height:24px;",
                "LoSlot4": "position:absolute; left:297px; top:261px; width:24px; height:24px;",
                "LoSlot5": "position:absolute; left:275px; top:283px; width:24px; height:24px;",
                "LoSlot6": "position:absolute; left:251px; top:300px; width:24px; height:24px;",
                "LoSlot7": "position:absolute; left:225px; top:310px; width:24px; height:24px;",
            }[self.flag]


    def highs(self):
        return self._slots(14, "HiSlot")

    def mids(self):
        return self._slots(13, "MedSlot")

    def lows(self):
        return self._slots(12, "LoSlot")

    def rigs(self):
        return self._slots(1137, "RigSlot")

    def subs(self):
        return list(
            self.items.filter(
                flag__startswith="SubSystemSlot"
            ).order_by(
                'flag'
            ).all()
        )

    def mods(self):
        mods = self.highs() + self.mids() + self.lows() + self.rigs() + self.subs() + self.scripts()
        if mods == None:
            return []
        else:
            return mods

    def scripts(self):
        return list(
            self.items.filter(
                Q(flag__startswith='HiSlot')
                | Q(flag__startswith='MedSlot')
                | Q(flag__startswith='LowSlot'),
            ).order_by(
                'flag'
            ).all()
        )


    def _slots(self, attribute_id, flag):
        slot_count = self.type.attributes.filter(attribute_id=attribute_id).first()
        if slot_count != None:
            slot_count = slot_count.value
        else:
            slot_count = 0
        slots = list(
            self.items.filter(
                flag__startswith=flag,
                singleton=True
            ).exclude(
                type__group__category_id=8
            ).order_by(
                'flag'
            ).all()
        )

        for i in range(len(slots), int(slot_count)):
            slots.append(None)
        return slots
