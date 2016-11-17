import mongoengine
from marvinbot.utils import localized_date


class ProbeAlias(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)
    alias = mongoengine.StringField(unique=True)
    probe_id = mongoengine.LongField(required=True)
    user_id = mongoengine.LongField(required=True)
    username = mongoengine.StringField(required=True)

    date_added = mongoengine.DateTimeField(default=localized_date)
    date_modified = mongoengine.DateTimeField(default=localized_date)
    date_deleted = mongoengine.DateTimeField(required=False, null=True)

    @classmethod
    def by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def by_probe_id(cls, probe_id):
        try:
            return cls.objects.get(probe_id=probe_id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def by_alias(cls, alias):
        try:
            return cls.objects.get(alias=alias)
        except cls.DoesNotExist:
            return None

    @classmethod
    def all(cls):
        try:
            return cls.objects(date_deleted=None)
        except:
            return None

    def __str__(self):
        return "{{ id = {id}, alias = \"{alias}\", probe_id = \"{probe_id}\" }}".format(id=self.id, probe_id=self.probe_id, alias=self.alias)
