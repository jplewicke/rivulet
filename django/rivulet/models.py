from neo4j.model import django_model as model

class Person(model.NodeModel):
    first_name = model.Property()
    last_name = model.Property()
    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

class Company(model.NodeModel):
    name = model.Property(indexed=True)
    owners = model.Relationship(Person,
        type=model.Outgoing.OWNED_BY,
        related_name="owns",
    )
    employees = model.Relationship(Person,
        type=model.Incoming.WORKS_AT,
        related_name="employer",
        related_single=True, # Only allow Persons to work at one Company
    )
    def __unicode__(self):
        return self.name
