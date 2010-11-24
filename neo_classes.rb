require 'neo4j'

Neo4j::Config[:storage_path] = "#{Dir.pwd}/dbneo"
Lucene::Config[:storage_path] = "#{Dir.pwd}/dblucene"
Lucene::Config[:store_on_file] = true


#Neo4j-based classes. Objects with these types are the ones that are actually persisted
#in the Neo4j graph store.  Changing the properties for them may require a special
#migration for ALL existing database data.  Changing the few helper methods we
#have for them shouldn't have a similar impact, but it's best to be cautious here.



#A CreditOffer is an offer by the source user to allow the destination user to owe
#up to a specified number of units to the source user.
#In double-entry book-keeping, the balance (amount_used + amount_held) of an outgoing
#CreditOffer is the value of debits(assets) that the destination user has assured the
#source user of.
#The balance of an incoming CreditOffer is the value of credits(liabilities) that are
#owed by the user.
#The credit limits of an outgoing CreditOffer that are offered represent
#the maximum number of debits that the source user is willing to accept from the
#destination user. The max_desired debits is the maximum number of debits that the
#destination user is willing to provide to the source user.
#The debits that are in amount_held are counted against the current credit limits.
#They are assumed to be reserved for repayment outside the credit network through
#provision of some sort of real-world service or good.
#The debits that are in amount_used are available for clearing the credits
#of the source user.


class CreditOffer
  include Neo4j::RelationshipMixin
  
  property :max_offered, :max_desired, :amount_used, :amount_held

  def max
    return [self.max_offered, self.max_desired].min
  end
  
  def usable
    return [self.max - self.amount_used - self.amount_held,0.0].max
  end
  
  def empty?
    return [self.max_offered, self.max_desired, self.amount_used, 
      self.amount_held] == [0,0,0,0]
  end
end


#Each user is identified by a user_id and a secret, both assumed to be hashed values.
#Each user has a default depth of transactions that they are limited to in the 

class User
  include Neo4j::NodeMixin
  
  property :user_id, :depth, :secret
  
  has_n(:trusts).relationship(CreditOffer)
  
  has_n(:activelytrusts)
  
  has_n(:trusted_by).relationship(CreditOffer).from(User)
  
  index :user_id
  
  def trustrel(dest)
    
    if self.trusts.include?(dest)
      #puts "yippee"
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
  rescue
    nil
  end
  
  def self.creds_from_id(user_id)
    user = self.fromid(user_id)
    unless user.nil?
      return user.credentials
    end
    nil
  end
  
  def credentials
    return [self.user_id, self.secret]
  end
  
  def to_json
    {
      :user => self.user_id,
      :depth => self.depth,
      :account_url => "/accounts/#{self.user_id}",
      :credit_url => "/credits/#{self.user_id}",
      :transaction_url => "/transactions/#{self.user_id}",
      :reservation_url => "/transactions/#{self.user_id}/held"
    }.to_json
  end
end
