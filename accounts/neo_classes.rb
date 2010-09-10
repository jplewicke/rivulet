require 'Neo4j'

Neo4j::Config[:storage_path] = '/Users/jplewicke/rivulet/accounts/dbneo'
Lucene::Config[:storage_path] = '/Users/jplewicke/rivulet/accounts/dblucene'
Lucene::Config[:store_on_file] = true


#Neo4j-based classes. Objects with these types are the ones that are actually persisted
#in the Neo4j graph store.  Changing the properties for them may require a special
#migration for ALL existing database data.  Changing the few helper methods we
#have for them shouldn't have a similar impact, but it's best to be cautious here.

class CreditOffer
  include Neo4j::RelationshipMixin
  
  property :max_offered, :max_desired, :amount_used, :amount_held

  def max
    return [self.max_offered, self.max_desired].min
  end
  
  def usable
    return self.max - self.amount_used
  end
  
  def empty?
    return [self.max_offered, self.max_desired, self.amount_used, 
      self.amount_held] == [0,0,0,0]
  end
end


class User
  include Neo4j::NodeMixin
  
  property :user_id
  #property :secret
  
  has_n(:trusts).relationship(CreditOffer)
  
  has_n(:activelytrusts)
  
  has_n(:trusted_by).relationship(CreditOffer).from(User)
  
  index :user_id
  
  def trustrel(dest)
    
    if self.trusts.include?(dest)
      puts "yippee"
      rel = self.rels.outgoing(:trusts)[dest]
    else
      rel = self.trusts.new(dest)
      rel.max_offered = 0.0
      rel.max_desired = 0.0
      rel.amount_used = 0.0
      rel.amount_held = 0.0
    end
    
    return rel
  end
  
  
  def self.fromid(id)
    ret = nil
    
    result = User.find(:user_id => id)
    result.each {|x| ret = x}
    
    if ret == nil
      raise "No such user found."
    end
    return ret
  end

end
