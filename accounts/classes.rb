require 'Neo4j'

Neo4j::Config[:storage_path] = '/Users/jplewicke/rivulet/accounts/dbneo'
Lucene::Config[:storage_path] = '/Users/jplewicke/rivulet/accounts/dblucene'
Lucene::Config[:store_on_file] = true

class CreditOffer
  include Neo4j::RelationshipMixin
  
  property :max_credit_offered, :max_credit_desired, :credit_used

end

class User
  include Neo4j::NodeMixin
  
  property :user_id
  #property :secret
  
  has_n(:trusts).relationship(Credit)
  has_n(:tradable_for)
  has_n(:trusted_by).relationship(Credit).from(User)
  
  index :user_id
  
  def trustrel(dest)
    return self.rels.outgoing(:trusts)[dest]
  end
end


# A comprehensive object that tracks bilateral credit relationships,
# since payments can occur in either 

class CreditRelationship
  attr_accessor :source, :dest, :credit_offered, :credit_received
  
  def initialize(source, dest)
    @source = source
    @dest = dest
    
    @credit_offered = @source.rels.outgoing(:trusts)[@dest]
    @credit_received = @source.rels.outgoing(:trusts)[@dest]
  end
end
  
  